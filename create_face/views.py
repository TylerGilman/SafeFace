from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from create_face.ml_handler.pipeline import PipelineHandler
from create_face.ml_handler.hugging_face import HuggingFaceHandler
import time
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from PIL import Image
import base64


pipeline_handler = PipelineHandler()
hugging_face_handler = HuggingFaceHandler()

@csrf_exempt
def index(request):
    if request.method == "POST":
        return create(request)
      
      
    form_fields = [
        {'id': 'gender', 'label': 'Gender', 'label': 'Select Gender', 'options': ['Male', 'Female', 'Ugly']},
        {'id': 'hair_color', 'label': 'Hair Color', 'label': 'Select Hair Color', 'options': ['Brown', 'Ginger', 'Blonde', 'Black', 'White', 'Purple']},
        {'id': 'hair_type', 'label': 'Hair Type', 'label': 'Select Hair Type', 'options': ['Curly', 'Straight', 'Messy', 'Wavy']},
        {'id': 'hair_length', 'label': 'Hair Length', 'label': 'Select Hair Length', 'options': ['Very Short', 'Short', 'Medium', 'Long', 'Very Long']},
        {'id': 'skin_color', 'label': 'Skin Color', 'label': 'Select Skin Color', 'options': ['White', 'Pale', 'Tan', 'Dark', 'Very Dark']},
        {'id': 'skin_type', 'label': 'Skin Type', 'label': 'Select Skin Type', 'options': ['Acne', 'Clear', 'Freckles', 'See-Through']},
        {'id': 'age', 'label': 'Age', 'label': 'Select Age', 'options': ['Child', 'Teenager', 'Adult', 'Elderly']},
        {'id': 'ethnicity', 'label': 'Ethnicity', 'label': 'Select Ethnicity', 'options': ['African', 'Caucasian', 'Italian', 'Jewish', 'British', 'Finnish', 'Mexican', 'Chinese', 'Vietnamese']},
        {'id': 'eye_color', 'label': 'Eye Color', 'label': 'Select Eye Color', 'options': ['Brown', 'Blue', 'Gray', 'Yellow', 'Green', 'Red']},
        {'id': 'body', 'label': 'Body Type', 'label': 'Select Body Type','options': ['Morbidly Obese', 'Obese', 'Chubby', 'Muscular', 'Athletic', 'Unnaturally Muscular', 'Normal', 'Thin', 'Skeleton']}
    ]
      
    mode = request.GET.get("mode")
    change_mode = request.GET.get("change_mode") 
    if not mode:
      mode = "create_mode"
    if change_mode == "true":
        print("mode: ", mode)
        return render(request, "create_form.html", {'guest': request.GET.get("guest"), 'form_fields': form_fields, 'mode': mode})
    return render(request, "create_face.html", {'guest': request.GET.get("guest"), 'form_fields': form_fields, 'mode': mode})



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
        # Save the image to a BytesIO object
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        
        # Encode the image in base64
        image_base64 = base64.b64encode(image_io.read()).decode('utf-8')
        image_data = f"data:image/png;base64,{image_base64}"
        
        # Render the template with the base64 image
        return render(request, "avatar_display.html", {
            "generate_method": "pipeline",
            "image_path": image_data
        })
    else:
        return render(request, "error.html", {"message": "Failed to generate image using pipeline."})

@csrf_exempt
def create_with_hugging_face(request):
    prompt = make_prompt(request)
    try:
        image = hugging_face_handler.generate_image(prompt)
        if image:
            # Save the image to a BytesIO object
            image_io = BytesIO()
            image.save(image_io, format='PNG')
            image_io.seek(0)
            
            # Encode the image in base64
            image_base64 = base64.b64encode(image_io.read()).decode('utf-8')
            image_data = f"data:image/png;base64,{image_base64}"
            
            # Render the template with the base64 image
            return render(request, "avatar_display.html", {
                "generate_method": "hugging_face",
                "image_path": image_data
            })
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
