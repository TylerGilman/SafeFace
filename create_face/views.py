from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import torch
from diffusers import (
    StableDiffusionXLPipeline,
    KDPM2AncestralDiscreteScheduler,
    AutoencoderKL,
)




def index(request):
  return render(request, "index.html", None)

@csrf_exempt
def create(request):
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
  prompt = "Hyper-Realism, Profile View, White Background, of a person with the following attributes: " + request.POST.get('hair_color')+ ", " + request.POST.get('eye_color') + ", " + request.POST.get('skin_type') + ", " + request.POST.get('ethnicity') + ", " + request.POST.get('gender') + ", " + request.POST.get('bodyfat') + ", face directly forward."
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


  image.save("static/images/generated_image.png")
  
  return render(request, "index.html", {"avatar": "true"})