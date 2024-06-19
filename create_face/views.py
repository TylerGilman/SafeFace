from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from create_face.ml_handler.pipeline import PipelineHandler
from create_face.ml_handler.hugging_face import HuggingFaceHandler
import time
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

pipeline_handler = PipelineHandler()
hugging_face_handler = HuggingFaceHandler()

@csrf_exempt
@login_required(login_url='/auth/login/')
def index(request):
    if request.method == "POST":
        return create(request)
    # Just get the page
    form_fields = [
        {'id': 'gender', 'label': 'Gender', 'placeholder': 'Select Gender', 'options': ['Male', 'Female', 'Ugly']},
        {'id': 'hair_color', 'label': 'Hair Color', 'placeholder': 'Select Hair Color', 'options': ['Brown', 'Ginger', 'Blonde', 'Black', 'White', 'Purple']},
        {'id': 'hair_type', 'label': 'Hair Type', 'placeholder': 'Select Hair Type', 'options': ['Curly', 'Straight', 'Messy', 'Wavy']},
        {'id': 'hair_length', 'label': 'Hair Length', 'placeholder': 'Select Hair Length', 'options': ['Very Short', 'Short', 'Medium', 'Long', 'Very Long']},
        {'id': 'skin_color', 'label': 'Skin Color', 'placeholder': 'Select Skin Color', 'options': ['White', 'Pale', 'Tan', 'Dark', 'Very Dark']},
        {'id': 'skin_type', 'label': 'Skin Type', 'placeholder': 'Select Skin Type', 'options': ['Acne', 'Clear', 'Freckles', 'See-Through']},
        {'id': 'age', 'label': 'Age', 'placeholder': 'Select Age', 'options': ['Child', 'Teenager', 'Adult', 'Elderly']},
        {'id': 'ethnicity', 'label': 'Ethnicity', 'placeholder': 'Select Ethnicity', 'options': ['African', 'Caucasian', 'Italian', 'Jewish', 'British', 'Finnish', 'Mexican', 'Chinese', 'Vietnamese']},
        {'id': 'eye_color', 'label': 'Eye Color', 'placeholder': 'Select Eye Color', 'options': ['Brown', 'Blue', 'Gray', 'Yellow', 'Green', 'Red']},
        {'id': 'body', 'label': 'Body Type', 'placeholder': 'Select Body Type','options': ['Morbidly Obese', 'Obese', 'Chubby', 'Muscular', 'Athletic', 'Unnaturally Muscular', 'Normal', 'Thin', 'Skeleton']}
    ]
    return render(request, "create_face.html", {'form_fields': form_fields})


@csrf_exempt
def create(request):
    generate_method = request.POST.get("generate_method")
    if generate_method == "pipeline":
        return create_with_pipeline(request)
    elif generate_method == "hugging_face":
        return create_with_hugging_face(request)
    else:
        return render(request, "error.html", {"message": "Invalid generate method."})


@csrf_exempt
def create_with_pipeline(request):
    prompt = make_prompt(request)
    image = pipeline_handler.generate_image(prompt)
    if image:
        image.save("static/images/generated_image.png")
        static_path = "/static/images/generated_image.png"
        return render(request, "avatar_display.html",
                      {"generate_method": "pipeline", "image_path": static_path + "?t=" + str(time.time())})
    else:
        return render(request, "error.html", {"message": "Failed to generate image using pipeline."})


@csrf_exempt
def create_with_hugging_face(request):
    prompt = make_prompt(request)
    try:
        image = hugging_face_handler.generate_image(prompt)
        if image:
            image.save("static/images/generated_image.png")
            static_path = "/static/images/generated_image.png"
            return render(request, "avatar_display.html",
                          {"generate_method": "hugging_face", "image_path": static_path + "?t=" + str(time.time())})
        else:
            return render(request, "error.html", {"message": "Failed to generate image using HuggingFace."})
    except Exception as e:
        return render(request, "error.html", {"message": str(e)})


def make_prompt(request):
    return (
        "Hyper-Realism, Front Face View, White Background, of a single person's clean face with the following "
        "attributes:"
        + request.POST.get("hair_color") + " "
        + request.POST.get("hair_type") + " "
        + request.POST.get("hair_length") + " "
        + request.POST.get("eye_color") + " "
        + request.POST.get("skin_color") + " ,"
        + request.POST.get("skin_type") + " "
        + request.POST.get("ethnicity") + " "
        + request.POST.get("gender") + " "
        + request.POST.get("body") + " "
        + request.POST.get("age") + " facing directly forward."
    )
