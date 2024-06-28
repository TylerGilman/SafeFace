import time
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
from PIL import Image
from io import BytesIO
import logging
import os
import subprocess
from create_face.models import UserImage

logger = logging.getLogger("swap_face")


def get_image_data(image_id, image_path):
    if image_id:
        user_image = get_object_or_404(UserImage, id=image_id)
        with open(user_image.image_path, 'rb') as f:
            logger.info(f"Retrieved image from database: {user_image.image_path}")
            return f.read()
    elif image_path:
        try:
            if 'base64,' in image_path:
                logger.info("Decoding base64 image from image path.")
                return base64.b64decode(image_path.split('base64,')[1])
            else:
                with open(image_path, 'rb') as f:
                    logger.info(f"Retrieved image from filesystem: {image_path}")
                    return f.read()
        except (IndexError, FileNotFoundError) as e:
            logger.error(f"Error retrieving image: {e}")
            return None
    return None


def decode_base64_image(data_url):
    if 'base64,' in data_url:
        image_data = data_url.split('base64,')[1]
        return base64.b64decode(image_data)
    return None


def save_image_to_temp(image, filename):
    temp_dir = os.path.join(os.path.dirname(__file__), 'data/tmp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    image.save(temp_path)
    return temp_path


def run_facefusion(output, source, target, headless=True):
    logger.info('Running FaceFusion command...')
    start_time = time.time()
    venv_path = '.venv/bin/activate'
    command = f'source {venv_path} && python swap_face/facefusion/run.py -s {source} -t {target} -o {output} {"--headless" if headless else ""}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    logger.info(f'FaceFusion command completed in {end_time - start_time} seconds')
    logger.info(f'Subprocess stdout: {result.stdout}')
    logger.info(f'Subprocess stderr: {result.stderr}')
    return result


def make_response_data(image_data, filename, output_image_data=None, image_id=None):
    response_data = {
        'image_data': f"data:image/jpeg;base64,{image_data}",
        'filename': filename
    }
    if output_image_data:
        response_data['output_image_data'] = f"data:image/png;base64,{output_image_data}"
    if image_id:
        response_data['image_id'] = image_id
    return response_data


@csrf_exempt
def swap_face(request):
    if request.method == 'POST':
        template = 'swap_face_content.html' if request.POST.get('render_mode') == 'content' else 'swap_face.html'

        image_id = request.POST.get('image_id')
        image_path = request.POST.get('image_path')
        logger.info(f"Received image_id: {image_id}, image_path: {image_path[:50] if image_path else None}")
        image_data = get_image_data(image_id, image_path)
        if image_data is not None:
            logger.info("Image data successfully retrieved.")
        else:
            logger.error("Image data could not be retrieved.")
            return JsonResponse({'error': 'Invalid image path or image not found'}, status=400)

        uploaded_file = request.POST.get('uploaded_file')
        if uploaded_file:
            logger.info('Uploaded file found, running face swap...')
            uploaded_file_data = decode_base64_image(uploaded_file)
            if not uploaded_file_data:
                return JsonResponse({'error': 'Invalid uploaded file data'}, status=400)

            uploaded_image = Image.open(BytesIO(uploaded_file_data))
            temp_uploaded_file_path = save_image_to_temp(uploaded_image, 'uploaded_image.png')

            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_data = Image.open(BytesIO(base64.b64decode(image_base64)))
            temp_image_data_path = save_image_to_temp(image_data, 'image_data.png')

            temp_output_path = os.path.join(os.path.dirname(__file__), 'data/tmp/output_image.png')
            run_facefusion(temp_output_path, temp_image_data_path, temp_uploaded_file_path)

            with open(temp_output_path, 'rb') as output_file:
                output_image_data = output_file.read()
                output_image_base64 = base64.b64encode(output_image_data).decode('utf-8')

            response_data = make_response_data(
                image_base64,
                request.POST.get('filename'),
                output_image_base64,
                image_id
            )
            logger.info(f'Response data, image_data: {response_data["image_data"][:50]}, output_image_data: {response_data["output_image_data"][:50]}')

            return JsonResponse(response_data)
        else:
            logger.info('No uploaded file found, returning image data...')
            return render(
                request,
                template,
                make_response_data(
                    base64.b64encode(image_data).decode('utf-8'),
                    request.POST.get('filename'),
                    image_id=image_id
                )
            )

    return JsonResponse({'error': 'Invalid request method'}, status=400)
