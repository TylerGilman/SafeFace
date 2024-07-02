import os
from django.shortcuts import render
from create_face.ml_handler.pipeline import PipelineHandler
from create_face.ml_handler.hugging_face import HuggingFaceHandler
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from io import BytesIO
import base64
import logging
from create_face.models import UserImage
from safe_face_web import settings

pipeline_handler = PipelineHandler()
hugging_face_handler = HuggingFaceHandler()

# Set up logging
logger = logging.getLogger("create_face")


def index(request):
    if request.method == "POST":
        return create(request)
    if request.GET.get("render_mode") == "content":
        template = "create_face_content.html"
    else:
        template = "create_face.html"

    form_fields = [
        {'id': 'gender', 'label': 'Gender', 'options': ['Male', 'Female', 'Ugly']},
        {'id': 'hair_color', 'label': 'Hair Color',
         'options': ['Brown', 'Ginger', 'Blonde', 'Black', 'White', 'Purple']},
        {'id': 'hair_type', 'label': 'Hair Type', 'options': ['Curly', 'Straight', 'Messy', 'Wavy']},
        {'id': 'hair_length', 'label': 'Hair Length',
         'options': ['Very Short', 'Short', 'Medium', 'Long', 'Very Long']},
        {'id': 'skin_color', 'label': 'Skin Color', 'options': ['White', 'Pale', 'Tan', 'Dark', 'Very Dark']},
        {'id': 'skin_type', 'label': 'Skin Type', 'options': ['Acne', 'Clear', 'Freckles', 'See-Through']},
        {'id': 'age', 'label': 'Age', 'options': ['Child', 'Teenager', 'Adult', 'Elderly']},
        {'id': 'ethnicity', 'label': 'Ethnicity',
         'options': ['African', 'Caucasian', 'Italian', 'Jewish', 'British', 'Finnish', 'Mexican', 'Chinese',
                     'Vietnamese']},
        {'id': 'eye_color', 'label': 'Eye Color', 'options': ['Brown', 'Blue', 'Gray', 'Yellow', 'Green', 'Red']}
    ]

    mode = request.GET.get("mode")
    change_mode = request.GET.get("change_mode")
    if not mode:
        mode = "create_mode"

    images = []
    if mode == "gallery_mode":
        user_images = UserImage.objects.filter(user=request.user) if request.user.is_authenticated else []
        if len(user_images) == 0:
            logger.error("No images found for the user.")
        for user_image in user_images:
            with open(user_image.image_path, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
                images.append({'id': user_image.id, 'image': image_base64})

        default_images = get_default_images()
        images.extend(default_images)

    if change_mode == "true":
        return render(request, "create_form.html",
                      {'guest': request.GET.get("guest"), 'render_mode': 'content', 'mode': mode,
                       'form_fields': form_fields, 'images': images})

    return render(request, template,
                  {'guest': request.GET.get("guest"), 'form_fields': form_fields, 'mode': mode, 'images': images})


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

            # Check how many images the user has saved
            user_images = UserImage.objects.filter(user=request.user)
            if len(user_images) >= 5:
                return HttpResponse("You have reached the maximum number of saved images.")

            # Save the image to the file system
            filename = f"{request.user.id}_image_{len(user_images) + 1}.png"
            file_path = save_image_to_file_system(data, request.user.id, filename)

            # Save the file path to the database
            user_image = UserImage(user=request.user, image_path=file_path)
            user_image.save()
            logger.info("Image saved successfully.")

            return render(request, "empty.html", {
                "generatedSaved": None,
                "showMessage": "Saved successfully!"
            })
        else:
            logger.error("Cannot save, no image data provided.")
            return HttpResponse("No image data provided.")
    return HttpResponse("Invalid request method.")


@login_required
def delete_image(request, id):
    if id.startswith("default-"):
        return render(request, "error.html", {"message": "Cannot delete default images."})
    try:
        # Attempt to get the image by ID
        image = UserImage.objects.get(id=id)
        image_path = image.image_path
        image.delete()

        # Remove the image file from the file system
        if os.path.exists(image_path):
            os.remove(image_path)

        logger.info(f'Image with id {id} deleted successfully.')
        return render(request, "empty.html", None)  # Redirect to the desired page after deletion
    except UserImage.DoesNotExist:
        logger.error(f'Image with id {id} not found.')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
    return render(request, "error.html", {"message": "Failed to delete image."})


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
                    default_images.append({'id': f'default-{filename}', 'image': image_base64})

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
