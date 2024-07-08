import asyncio
import torch
from diffusers import StableDiffusionXLPipeline, KDPM2AncestralDiscreteScheduler, AutoencoderKL
from .base_ml import BaseMLHandler

class PipelineHandler(BaseMLHandler):
    def __init__(self, vae_model="madebyollin/sdxl-vae-fp16-fix", pipeline_model="Corcelio/mobius", max_queue_size=10):
        super().__init__(max_queue_size)
        self.vae_model = vae_model
        self.pipeline_model = pipeline_model
        self.pipe = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        vae = AutoencoderKL.from_pretrained(self.vae_model, torch_dtype=torch.float16)
        self.pipe = StableDiffusionXLPipeline.from_pretrained(self.pipeline_model, vae=vae, torch_dtype=torch.float16)
        self.pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.to(self.device)

    async def generate_image(self, prompt):
        if self.pipe is None:
            raise ValueError("Pipeline has not been initialized")

        try:
            # Run in an executor to avoid blocking the event loop
            image = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.pipe(
                    prompt=prompt,
                    negative_prompt="",
                    width=1024,
                    height=1024,
                    guidance_scale=7,
                    num_inference_steps=50,
                    clip_skip=3,
                    callback=self._callback,
                    callback_steps=1
                ).images[0]
            )
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
        finally:
            torch.cuda.empty_cache()

        return image

    def _callback(self, step, timestep, latents):
        if self.cancel_flag.is_set():
            raise BaseMLHandler.CancellationException("Image generation was cancelled.")

pipeline_handler = PipelineHandler()