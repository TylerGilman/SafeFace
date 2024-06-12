from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import torch
from diffusers import (
    StableDiffusionXLPipeline,
    KDPM2AncestralDiscreteScheduler,
    AutoencoderKL,
)




def index(request):
  initial_food_value = "none"  # This can be dynamic based on your logic
  context = {
        'food': initial_food_value,
    }
  return render(request, "index.html", context)

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
  prompt = "Front Headshot of a person with the following attributes: " + request.POST.get('character')
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


  if request.method == 'POST':
      character = request.POST.get('character')
      print(character)  # Print the "character" attribute
  return render(request, None)