from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import torch
from diffusers import (
    StableDiffusionXLPipeline,
    KDPM2AncestralDiscreteScheduler,
    AutoencoderKL,
)
import time
import requests
import io
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/Corcelio/mobius"
headers = {"Authorization": "Bearer REPLACE_ME"}


def index(request):
    return render(request, "index.html", None)


@csrf_exempt
def create(request):
  # Define prompts and generate image
  prompt = "Hyper-Realism, Front Face View, White Background, no hair in the way of a single person's face with the following attributes: " + request.POST.get('hair_color') + " " + request.POST.get('hair_type') + " " + request.POST.get('hair_length') + " " + request.POST.get('skin_type') + " " + request.POST.get('eye_color') + " " + request.POST.get('skin_color') + " " + request.POST.get('ethnicity') + " " + request.POST.get('gender') + " " + request.POST.get('bodyfat') + " " + request.POST.get('age') + " facing directly forward."
  negative_prompt = ""
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
    prompt = make_prompt(request)
    negative_prompt = ""

    image = pipe(
      prompt=prompt,
      negative_prompt=negative_prompt,
      width=1024,
      height=1024,
      guidance_scale=7,
      num_inference_steps=50,
      clip_skip=3,
    ).images[0]

  image.save("static/images/generated_image.png")
  
  torch.cuda.empty_cache()
  
  static_path = "/static/images/generated_image.png"
  # add t as a parameter to prevent caching
  return render(request, "avatar_display.html", {'image_path': static_path + "?t=" + str(time.time())})



@csrf_exempt
def create_with_hugging_face(request):
    prompt = make_prompt(request)

    image_bytes = query({
        "inputs": prompt,
    })

    image = Image.open(io.BytesIO(image_bytes))
    image.save("static/images/generated_image.png")
    static_path = "/static/images/generated_image.png"
    return render(request, "avatar_display.html", {'image_path': static_path + "?t=" + str(time.time())})


def make_prompt(request):
    return (("Hyper-Realism, Front Face View, White Background, of a single person's face with the following "
             "attributes: ") + request.POST.get('hair_color') + " " + request.POST.get('hair_type') + " " +
            request.POST.get('hair_length') + " " + request.POST.get('skin_type') + " " + request.POST.get(
                'eye_color') + " " + request.POST.get('skin_color') + " " + request.POST.get('ethnicity') + " " +
            request.POST.get('gender') + " " + request.POST.get('bodyfat') + " " + request.POST.get('age') + " facing directly forward.")


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content
>>>>>>> 6a27d1b325303c241b27ebc1fcc8c830144da964
