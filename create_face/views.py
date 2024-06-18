from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ml_handler.pipeline import PipelineHandler
from ml_handler.hugging_face import HuggingFaceHandler
import time

pipeline_handler = PipelineHandler()
hugging_face_handler = HuggingFaceHandler()

@csrf_exempt
def create(request):
  if request.POST.get("generate_method") == "pipeline":
    return create_with_pipline(request)
  elif request.POST.get("generate_method") == "hugging_face":
    return create_with_hugging_face(request)
  else:
    return render(request, "error.html", {"message": "Invalid generate method."})
      
@csrf_exempt
def create_with_pipline(request):
    prompt = make_prompt(request)
    image = pipeline_handler.generate_image(prompt)
    if image:
        image.save("static/images/generated_image.png")
        static_path = "/static/images/generated_image.png"
        return render(request, "avatar_display.html", {"generate_method": "pipeline", "image_path": static_path + "?t=" + str(time.time())})
    else:
        return render(request, "error.html", {"message": "Failed to generate image using pipeline."})

@csrf_exempt
def create_with_hugging_face(request):
    prompt = make_prompt(request)
    image = hugging_face_handler.generate_image(prompt)
    if image:
        image.save("static/images/generated_image.png")
        static_path = "/static/images/generated_image.png"
        return render(request, "avatar_display.html", {"generate_method": "hugging_face", "image_path": static_path + "?t=" + str(time.time())})
    else:
        return render(request, "error.html", {"message": "Failed to generate image using Hugging Face."})

def make_prompt(request):
    return (
        "Hyper-Realism, Front Face View, White Background, of a single person's clean face with the following attributes: "
        + request.POST.get("hair_color") + " "
        + request.POST.get("hair_type") + " "
        + request.POST.get("hair_length") + " "
        + request.POST.get("skin_type") + " "
        + request.POST.get("eye_color") + " "
        + request.POST.get("skin_color") + " "
        + request.POST.get("ethnicity") + " "
        + request.POST.get("gender") + " "
        + request.POST.get("body") + " "
        + request.POST.get("age") + " facing directly forward."
    )

@csrf_exempt
def index(request):
    if request.method=="POST":
        return create(request)
    ## Just get the page
    return render(request, "index.html", None)
