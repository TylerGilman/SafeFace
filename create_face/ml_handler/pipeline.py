import torch
from diffusers import StableDiffusionXLPipeline, KDPM2AncestralDiscreteScheduler, AutoencoderKL
from .base_ml import BaseMLHandler

class PipelineHandler(BaseMLHandler):
    def __init__(self, vae_model="madebyollin/sdxl-vae-fp16-fix", pipeline_model="Corcelio/mobius"):
        super().__init__()
        self.vae_model = vae_model
        self.pipeline_model = pipeline_model

    @BaseMLHandler.handle_errors
    def generate_image(self, prompt):
        # Load VAE component
        vae = AutoencoderKL.from_pretrained(self.vae_model, torch_dtype=torch.float16)

        # Configure the pipeline
        pipe = StableDiffusionXLPipeline.from_pretrained(self.pipeline_model, vae=vae, torch_dtype=torch.float16)
        pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(pipe.scheduler.config)
        pipe.to(self.device)

        # Generate the image
        image = pipe(
            prompt=prompt,
            negative_prompt="",
            width=1024,
            height=1024,
            guidance_scale=7,
            num_inference_steps=50,
            clip_skip=3,
        ).images[0]

        torch.cuda.empty_cache()
        return image
