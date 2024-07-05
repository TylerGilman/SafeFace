import torch
from diffusers import StableDiffusionXLPipeline, KDPM2AncestralDiscreteScheduler, AutoencoderKL
from .base_ml import BaseMLHandler

class PipelineHandler(BaseMLHandler):
    def __init__(self, vae_model="madebyollin/sdxl-vae-fp16-fix", pipeline_model="Corcelio/mobius"):
        super().__init__()
        self.vae_model = vae_model
        self.pipeline_model = pipeline_model
        self.pipe = None

    @BaseMLHandler.handle_errors
    def generate_image(self, prompt, cancel_flag):
        # Load VAE component
        vae = AutoencoderKL.from_pretrained(self.vae_model, torch_dtype=torch.float16)

        # Configure the pipeline
        self.pipe = StableDiffusionXLPipeline.from_pretrained(self.pipeline_model, vae=vae, torch_dtype=torch.float16)
        self.pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.to(self.device)

        # Generate the image
        def callback(step, timestep, latents):
            if cancel_flag.is_set():
                raise CancellationException("Image generation was cancelled.")
            return

        try:
            image = self.pipe(
                prompt=prompt,
                negative_prompt="",
                width=1024,
                height=1024,
                guidance_scale=7,
                num_inference_steps=50,
                clip_skip=3,
                callback=callback,
                callback_steps=1
            ).images[0]
        except CancellationException:
            return None
        finally:
            torch.cuda.empty_cache()

        return image

class CancellationException(Exception):
    pass

pipeline_handler = PipelineHandler()