import asyncio
import torch
import logging
from diffusers import StableDiffusionXLPipeline, KDPM2AncestralDiscreteScheduler, AutoencoderKL
from .base_ml import BaseMLHandler

logger = logging.getLogger(__name__)

class PipelineHandler(BaseMLHandler):
    def __init__(self, vae_model="madebyollin/sdxl-vae-fp16-fix", pipeline_model="Corcelio/mobius", max_queue_size=10):
        super().__init__(max_queue_size)
        self.vae_model = vae_model
        self.pipeline_model = pipeline_model
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.image_counter = 0
        self.max_images_before_cleanup = 10
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        vae = AutoencoderKL.from_pretrained(self.vae_model, torch_dtype=torch.float16)
        self.pipe = StableDiffusionXLPipeline.from_pretrained(self.pipeline_model, vae=vae, torch_dtype=torch.float16)
        self.pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.to(self.device)

    def unload_pipeline(self):
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            torch.cuda.empty_cache()
        logger.info("Pipeline unloaded and CUDA cache cleared")

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
            self.image_counter += 1
            if self.image_counter >= self.max_images_before_cleanup:
                await self.periodic_cleanup()
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
        finally:
            torch.cuda.empty_cache()

        return image

    def _callback(self, step, timestep, latents):
        if self.cancel_flag.is_set():
            raise BaseMLHandler.CancellationException("Image generation was cancelled.")

    def to_cpu(self):
        if self.pipe is not None:
            self.pipe = self.pipe.to('cpu')
            torch.cuda.empty_cache()
        logger.info("Pipeline moved to CPU and CUDA cache cleared")

    def to_gpu(self):
        if self.pipe is not None:
            self.pipe = self.pipe.to(self.device)
        logger.info("Pipeline moved to GPU")

    async def cleanup(self):
        await self.cancel_generation()
        self.unload_pipeline()
        logger.info("Cleanup completed")

    async def periodic_cleanup(self):
        self.to_cpu()
        await asyncio.sleep(1)  # Allow time for other operations
        self.to_gpu()
        self.image_counter = 0
        logger.info("Periodic cleanup completed")

    def log_memory_usage(self):
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            logger.info(f"GPU Memory allocated: {allocated:.2f} GB")
            logger.info(f"GPU Memory cached: {reserved:.2f} GB")
        else:
            logger.info("CUDA is not available")

pipeline_handler = PipelineHandler()

# Cleanup function to be called when shutting down the application
async def shutdown_cleanup():
    await pipeline_handler.cleanup()
    logger.info("Application shutdown cleanup completed")