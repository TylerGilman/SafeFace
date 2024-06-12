import torch
from diffusers import (
    StableDiffusionXLPipeline,
    KDPM2AncestralDiscreteScheduler,
    AutoencoderKL,
)

# Load VAE component
vae = AutoencoderKL.from_pretrained(
    "madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16
)

# Configure the pipeline
pipe = StableDiffusionXLPipeline.from_pretrained(
    "Corcelio/mobius", vae=vae, torch_dtype=torch.float16
)
pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.to("cuda")

# Define prompts and generate image
prompt = "Front Headshot of a person with the following attributes: male, super chad, brown hair, brown eyes"
negative_prompt = ""

image = pipe(
    prompt,
    negative_prompt=negative_prompt,
    width=1024,
    height=1024,
    guidance_scale=7,
    num_inference_steps=50,
    clip_skip=3,
).images[0]


image.save("generated_image.png")
