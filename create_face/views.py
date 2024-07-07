import base64
import json
import logging
import os
import random
import threading
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader

from create_face.ml_handler.hugging_face import HuggingFaceHandler
from create_face.ml_handler.pipeline import PipelineHandler
from create_face.models import UserImage
from safe_face_web import settings

# Global variable to store the cancellation flag
cancel_flag = threading.Event()

pipeline_handler = PipelineHandler()
hugging_face_handler = HuggingFaceHandler()

# Set up logging
logger = logging.getLogger("create_face")

form_fields = [
    {
        'id': 'gender',
        'label': 'Gender',
        'options': ['Male', 'Female', 'Other']
    },
    {
        'id': 'hair_color',
        'label': 'Hair Color',
        'options': ['Brown', 'Ginger', 'Blonde', 'Black', 'White', 'Purple']
    },
    {
        'id': 'hair_type',
        'label': 'Hair Type',
        'options': ['Curly', 'Straight', 'Messy', 'Wavy']
    },
    {
        'id': 'hair_length',
        'label': 'Hair Length',
        'options': ['Very Short', 'Short', 'Medium', 'Long', 'Very Long']
    },
    {
        'id': 'skin_color',
        'label': 'Skin Color',
        'options': ['Fair', 'Light', 'Medium', 'Dark', 'Deep']
    },
    {
        'id': 'skin_type',
        'label': 'Skin Type',
        'options': ['Acne', 'Clear', 'Freckles', 'Sensitive']
    },
    {
        'id': 'age',
        'label': 'Age',
        'options': ['Child', 'Teenager', 'Adult', 'Elderly']
    },
    {
        'id': 'ethnicity',
        'label': 'Ethnicity',
        'options': ['African', 'Caucasian', 'Italian', 'Jewish', 'British', 'Finnish', 'Mexican', 'Chinese',
                    'Vietnamese']
    },
    {
        'id': 'eye_color',
        'label': 'Eye Color',
        'options': ['Brown', 'Blue', 'Gray', 'Yellow', 'Green', 'Red']
    },
    {
        'id': 'facial_hair',
        'label': 'Facial Hair',
        'options': ['Beard', 'Mustache', 'Goatee', 'Clean Shaven']
    },
]


def index(request):
    if request.method == "POST":
        return create(request)

    render_mode = request.GET.get("render_mode")
    if render_mode == "content":
        template = "create_face_content.html"
    else:
        template = "create_face.html"

    mode = request.GET.get("mode")
    change_mode = request.GET.get("change_mode")
    if not mode:
        mode = "create_mode"

    images = []
    if change_mode == "true":
        if mode == "gallery_mode" or mode == "create_mode":
            user_images = UserImage.objects.filter(
                user=request.user) if request.user.is_authenticated else []
            if len(user_images) == 0:
                logger.error("No images found for the user.")
            for user_image in user_images:
                with open(user_image.image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                    images.append({'id': user_image.id, 'image': image_base64})

            default_images = get_default_images()
            images.extend(default_images)
            return render(request, "create_form.html",
                          {'guest': request.GET.get("guest"), 'render_mode': 'content', 'mode': mode,
                           'form_fields': form_fields, 'images': images})
    context = {
        'guest': request.GET.get("guest"),
        'form_fields': form_fields,
        'mode': mode,
        'images': images
    }
    loaded_template = loader.get_template(template)
    rendered_template = loaded_template.render(context, request)
    response = HttpResponse(rendered_template)
    response['HX-Trigger'] = json.dumps({
        "showMessage": {
            "text": "Welcome, create an Avatar or pick from the gallery!",
            "type": "info"
        }
    })
    return response


def create(request):
    generate_method = request.POST.get("generate_method")
    if generate_method == "pipeline":
        return create_with_pipeline(request)
    elif generate_method == "hugging_face":
        return create_with_hugging_face(request)
    else:
        return render(request, "error.html", {"message": "Invalid generate method."})


def create_with_pipeline(request):
    prompt = make_prompt(request)

    # Reset the cancellation flag
    cancel_flag.clear()

    def generate_image_with_cancel_check():
        return pipeline_handler.generate_image(prompt, cancel_flag)

    # Run the generation in a separate thread
    thread = threading.Thread(target=generate_image_with_cancel_check)
    thread.start()
    thread.join()  # Wait for the thread to complete

    if cancel_flag.is_set():
        return HttpResponse("Image generation was cancelled.")

    image = generate_image_with_cancel_check()
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
        return JsonResponse({"error": "Failed to generate image using Pipeline."}, status=400)


def create_with_hugging_face(request):
    prompt = make_prompt(request)

    # Reset the cancellation flag
    cancel_flag.clear()

    def generate_image_with_cancel_check():
        return hugging_face_handler.generate_image(prompt, cancel_flag)

    # Run the generation in a separate thread
    thread = threading.Thread(target=generate_image_with_cancel_check)
    thread.start()
    thread.join()  # Wait for the thread to complete

    if cancel_flag.is_set():
        return HttpResponse("Image generation was cancelled.")

    try:
        image = generate_image_with_cancel_check()
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
            return JsonResponse({"error": "Failed to generate image using HuggingFace."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def cancel_generation(request):
    cancel_flag.set()
    return render(request, 'button_container.html')


def clear_attributes(request):
    new_form_fields = form_fields.copy()
    for field in new_form_fields:
        field['default'] = ''

    return render(request, "create_form.html", {
        'guest': request.GET.get("guest"),
        'render_mode': 'content',
        'mode': 'create_mode',
        'form_fields': new_form_fields,
        'images': []
    })


def randomize_attributes(request):
    new_form_fields = form_fields.copy()
    for field in new_form_fields:
        # Randomly select an option for each
        field['default'] = random.choice(field['options'])

    return render(request, "create_form.html", {
        'guest': request.GET.get("guest"),
        'render_mode': 'content',
        'mode': 'create_mode',
        'form_fields': new_form_fields,
        'images': []
    })


@login_required
def save_image(request):
    if request.method == "POST":
        image_data = request.POST.get("image_path")
        if image_data:
            _, imgstr = image_data.split(';base64,')
            data = base64.b64decode(imgstr)
            # Check how many images the user has saved
            user_images = UserImage.objects.filter(user=request.user)
            if len(user_images) >= 5:
                logger.info("Maximum number of saved images, cannot save!")
                return JsonResponse(
                    {"error": "Maximum number of images saved!"},
                    status=400,
                    headers={
                        'HX-Trigger': json.dumps({
                            "showMessage": {
                                "text": "Maximum number of images saved!",
                                "type": "warning"
                            }
                        })
                    })
            # Save the image to the file system
            filename = f"{request.user.id}_image_{len(user_images) + 1}.png"
            file_path = save_image_to_file_system(
                data, request.user.id, filename)
            # Save the file path to the database
            user_image = UserImage(user=request.user, image_path=file_path)
            user_image.save()
            logger.info("Image saved successfully.")
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "showMessage": {
                            "text": "Avatar Saved To Gallery",
                            "type": "success"
                        }
                    })
                })
        else:
            logger.error("Cannot save, no image data provided.")
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "showMessage": {
                            "text": "No Avatar To Save",
                            "type": "warning"
                        }
                    })
                })
    return JsonResponse({"error": "Error Saving Image."}, status=400)


@login_required
def delete_image(request, id):
    logger.info(f'Attempting to delete image with id: {id}')
    if str(id).startswith("default-"):
        logger.info('Cannot delete default image')
        return JsonResponse({"error": "Cannot delete default image."}, status=400)
    try:
        logger.info(f'Fetching image with id: {id}')
        image = UserImage.objects.get(id=id)
        image_path = image.image_path
        logger.info(f'Deleting image from database')
        image.delete()
        logger.info(f'Checking if file exists: {image_path}')
        if os.path.exists(image_path):
            logger.info(f'Removing file: {image_path}')
            os.remove(image_path)
        logger.info(f'Image with id {id} deleted successfully.')
        return HttpResponse(status=200,
                            headers={
                                'HX-Trigger': json.dumps({
                                    "showMessage": {
                                        "text": "Avatar Deleted",
                                        "type": "success"
                                    }
                                })
                            })
    except UserImage.DoesNotExist:
        logger.error(f'Image with id {id} not found.')
    except Exception as e:
        logger.error(f'An error occurred: {e}', exc_info=True)
    return JsonResponse({"error": "Failed to delete image."}, status=400)


def save_image_to_file_system(image_data, user_id, filename):
    directory = os.path.join(settings.MEDIA_ROOT, 'user_images', str(user_id))
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'wb') as f:
        f.write(image_data)
    return file_path


def get_default_images():
    default_images = []
    default_images_dir = os.path.join(settings.MEDIA_ROOT, 'default_images')

    if os.path.exists(default_images_dir):
        for filename in os.listdir(default_images_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(default_images_dir, filename)
                with open(filepath, 'rb') as f:
                    image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    default_images.append(
                        {'id': f'default-{filename}', 'image': image_base64})

    return default_images


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
