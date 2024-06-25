from django.shortcuts import render
from create_face.ml_handler.pipeline import PipelineHandler
from create_face.ml_handler.hugging_face import HuggingFaceHandler
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from io import BytesIO
import base64

import logging
from create_face.models import UserImage

pipeline_handler = PipelineHandler()
hugging_face_handler = HuggingFaceHandler()

# Set up logging
logger = logging.getLogger("create_face")

@csrf_exempt
@login_required
def delete_image(request, id):
    try:
        # Attempt to get the image by ID
        image = UserImage.objects.get(id=id)
        image.delete()
        logger.info(f'Image with id {id} deleted successfully.')
        return render(request, "empty.html", None)  # Redirect to the desired page after deletion
    except UserImage.DoesNotExist:
        logger.error(f'Image with id {id} not found.')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
    return render(request, "error.html", {"message": "Failed to delete image."})



@csrf_exempt
def index(request):
    if request.method == "POST":
        return create(request)
    if request.GET.get("render_mode") == "content":
        template = "create_face_content.html"
    else:
        template = "create_face.html"

    form_fields = [
        {'id': 'gender', 'label': 'Select Gender',
            'options': ['Male', 'Female', 'Ugly']},
        {'id': 'hair_color', 'label': 'Select Hair Color',
         'options': ['Brown', 'Ginger', 'Blonde', 'Black', 'White', 'Purple']},
        {'id': 'hair_type', 'label': 'Select Hair Type',
            'options': ['Curly', 'Straight', 'Messy', 'Wavy']},
        {'id': 'hair_length', 'label': 'Select Hair Length',
         'options': ['Very Short', 'Short', 'Medium', 'Long', 'Very Long']},
        {'id': 'skin_color', 'label': 'Select Skin Color',
            'options': ['White', 'Pale', 'Tan', 'Dark', 'Very Dark']},
        {'id': 'skin_type', 'label': 'Select Skin Type', 'options': [
            'Acne', 'Clear', 'Freckles', 'See-Through']},
        {'id': 'age', 'label': 'Select Age', 'options': [
            'Child', 'Teenager', 'Adult', 'Elderly']},
        {'id': 'ethnicity', 'label': 'Select Ethnicity',
         'options': ['African', 'Caucasian', 'Italian', 'Jewish', 'British', 'Finnish', 'Mexican', 'Chinese',
                     'Vietnamese']},
        {'id': 'eye_color', 'label': 'Select Eye Color',
         'options': ['Brown', 'Blue', 'Gray', 'Yellow', 'Green', 'Red']}
    ]

    mode = request.GET.get("mode")
    change_mode = request.GET.get("change_mode")
    if not mode:
        mode = "create_mode"

    images = []
    if mode == "gallery_mode":
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = None

        user_images = UserImage.objects.filter(
            user=request.user) if request.user.is_authenticated else []
        default_images = UserImage.objects.filter(
            user=admin_user) if admin_user else []
        images = list(default_images) + list(user_images)

        # Encode images to base64
        for image in images:
            image.image = base64.b64encode(
                force_bytes(image.image)).decode('utf-8')
            image.id = image.id

    if change_mode == "true":
        return render(request, "create_form.html",
                      {'guest': request.GET.get("guest"), 'render_mode': 'content', 'mode': mode, 'form_fields': form_fields, 'images': images})

    return render(request, template,
                  {'guest': request.GET.get("guest"), 'form_fields': form_fields, 'mode': mode, 'images': images})


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


@login_required
def save_image(request):
    if request.method == "POST":
        image_data = request.POST.get("image_data")
        if image_data:
            _, imgstr = image_data.split(';base64,')
            data = base64.b64decode(imgstr)

            user_image = UserImage(user=request.user, image=data)
            user_image.save()
            return HttpResponse("Image saved successfully.")
        else:
            return HttpResponse("No image data provided.")
    return HttpResponse("Invalid request method.")


def make_prompt(request):
    attributes = [
        ("hair color", request.POST.get("hair_color")),
        ("hair type", request.POST.get("hair_type")),
        ("hair length", request.POST.get("hair_length")),
        ("eye color", request.POST.get("eye_color")),
        ("skin color", request.POST.get("skin_color")),
        ("skin type", request.POST.get("skin_type")),
        ("ethnicity", request.POST.get("ethnicity")),
        ("gender", request.POST.get("gender")),
        ("age", request.POST.get("age"))
    ]

    prompt = "Hyper-Realism, Front Face View, White Background, of a single person's clean face with the following: "
    attributes = [f"{label}: {value}" for label, value in attributes if value]

    if attributes:
        prompt += ", ".join(attributes) + "."
    else:
        prompt += "a clean face with a white background."

    prompt += " The person is looking directly into the camera, with a neutral expression."

    return prompt
