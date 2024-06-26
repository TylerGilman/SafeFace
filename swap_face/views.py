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


@csrf_exempt
def swap_face(request):
    if request.method == 'POST':
        template = 'swap_face.html'
        if request.POST.get('render_mode') == 'content':
            template = 'swap_face_content.html'

        image_id = request.POST.get('image_id')
        image_path = request.POST.get('image_path')
        image_data = None

        if image_id:
            # Retrieve image from the database using image_id
            user_image = get_object_or_404(UserImage, id=image_id)
            with open(user_image.image_path, 'rb') as f:
                image_data = f.read()
        elif image_path:
            # Handle default image from the file system
            try:
                if 'base64,' in image_path:
                    image_data = base64.b64decode(image_path.split('base64,')[1])
                else:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
            except (IndexError, FileNotFoundError) as e:
                # logger.error(f"Error processing image_path: {e}")
                return JsonResponse({'error': 'Invalid image path or image not found'}, status=400)

        if not image_data:
            return JsonResponse({'error': 'No image data or image ID provided'}, status=400)

        image_base64 = base64.b64encode(image_data).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        filename = request.POST.get('filename')
        uploaded_file_data = request.POST.get('uploaded_file')

        if uploaded_file_data:
            uploaded_file_data = uploaded_file_data.split('base64,')[1]
            uploaded_file_data = base64.b64decode(uploaded_file_data)
            uploaded_image = Image.open(BytesIO(uploaded_file_data))

            # Convert the uploaded image to bytes
            uploaded_file_bytes = BytesIO()
            uploaded_file_bytes = uploaded_file_bytes.getvalue()

            # Process the image_data (if it's base64 encoded)
            image_data = image_data.split('base64,')[1]
            image_data = base64.b64decode(image_data)
            image_data = Image.open(BytesIO(image_data))

            # Create a temporary directory if it doesn't exist
            temp_dir = os.path.join(os.path.dirname(__file__), 'data/tmp')
            os.makedirs(temp_dir, exist_ok=True)

             # Save the images to temporary files
            temp_uploaded_file_path = os.path.join(temp_dir, 'uploaded_image.png')
            temp_image_data_path = os.path.join(temp_dir, 'image_data.png')
            uploaded_image.save(temp_uploaded_file_path)
            image_data.save(temp_image_data_path)

            # Define the output path for the face swapped image
            temp_output_path = os.path.join(temp_dir, 'output_image.png')

            # Call the FaceFusion command
            command = f'python swap_face/facefusion/run.py -h'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            # Log the stdout and stderr outputs for debugging
            logger.info(f'Subprocess stdout: {result.stdout}')
            logger.info(f'Subprocess stderr: {result.stderr}')

            # Handle the uploaded_file and image_data
            # Perform face swap operation here

            # Return appropriate response
            return JsonResponse({'status': 'success', 'message': 'Face swap successful'})

        response_data = {'image_data': image_data_url, 'filename': filename, 'image_id': image_id} \
            if image_id else {'image_data': image_data_url, 'filename': filename}
        return render(request, template, response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
