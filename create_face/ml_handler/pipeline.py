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
        self.cancel_flag = asyncio.Event()


    def _initialize_pipeline(self):
        vae = AutoencoderKL.from_pretrained(self.vae_model, torch_dtype=torch.float16)
        self.pipe = StableDiffusionXLPipeline.from_pretrained(self.pipeline_model, vae=vae, torch_dtype=torch.float16)
        self.pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.to(self.device)

        
    async def cancel_generation(self):
        self.cancel_flag.set()
        
    async def add_to_queue(self, prompt):
        future = asyncio.Future()
        await self.queue.put((prompt, future))
        return await future

    async def _process_queue(self):
        while True:
            prompt, future = await self.queue.get()
            try:
                result = await self.generate_image(prompt, self.cancel_flag)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()
            self.cancel_flag.clear()  # Reset the flag after each generation

    @BaseMLHandler.handle_errors
    async def generate_image(self, prompt, cancel_flag):
        if self.pipe is None:
            raise ValueError("Pipeline has not been initialized")

        def callback(step, timestep, latents):
            if cancel_flag.is_set():
                raise CancellationException("Image generation was cancelled.")
            return

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
                    callback=callback,
                    callback_steps=1
                ).images[0]
            )
        except CancellationException:
            return None
        finally:
            torch.cuda.empty_cache()

        return image

class CancellationException(Exception):
    pass

pipeline_handler = PipelineHandler()