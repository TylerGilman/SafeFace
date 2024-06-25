from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse
import base64
from PIL import Image
from io import BytesIO
import os
import subprocess
import logging

# Set up logging
logger = logging.getLogger("create_face")


@csrf_exempt
def swap_face(request):
    if request.method == 'POST':
        if request.POST.get(('csrf_token') != get_token(request)):
            return JsonResponse({'error': 'Invalid CSRF token'}, status=400)
        template = 'swap_face.html'
        if request.POST.get('render_mode') == 'content':
            template = 'swap_face_content.html'

        image_data = request.POST.get('image_data')
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)

        uploaded_file_data = request.POST.get('uploaded_file')
        # Swap if the post request sends a image_data and a filename
        if uploaded_file_data and image_data:
            # Process the uploaded_file_data (if it's base64 encoded)
            uploaded_file_data = uploaded_file_data.split('base64,')[1]
            uploaded_file_data = base64.b64decode(uploaded_file_data)
            uploaded_image = Image.open(BytesIO(uploaded_file_data))

            # Process the image_data (if it's base64 encoded)
            image_data = image_data.split('base64,')[1]
            image_data = base64.b64decode(image_data)
            image_data = Image.open(BytesIO(image_data))

            # Save the images to temporary files
            temp_uploaded_file_path = '/tmp/uploaded_image.png'
            temp_image_data_path = '/tmp/image_data.png'
            # NEED ERROR HANDLING
            uploaded_image.save(temp_uploaded_file_path)
            image_data.save(temp_image_data_path)
            
            # Verify that the files were saved
            if not os.path.exists(temp_uploaded_file_path):
                logger.error(f'Uploaded image file not found at {temp_uploaded_file_path}')
            if not os.path.exists(temp_image_data_path):
                logger.error(f'Image data file not found at {temp_image_data_path}')
            logger.debug(f'Saved uploaded image to {temp_uploaded_file_path}')
            logger.debug(f'Loaded uploaded image and image data')

            # Define the output path for the face swapped image
            temp_output_path = '/tmp/output_image.png'

            # Call the FaceFusion command
            #command = f'python swap_face/facefusion/run.py {temp_uploaded_file_path} {temp_image_data_path} {temp_output_path}'
            
            command = f'python swap_face/facefusion/install.py'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
             # Log the stdout and stderr outputs for debugging
            logger.debug(f'Subprocess stdout: {result.stdout}')
            logger.debug(f'Subprocess stderr: {result.stderr}')
            #command = f'python swap_face/facefusion/run.py'
            #result = subprocess.run(command, shell=True, capture_output=True, text=True)
             # Log the stdout and stderr outputs for debugging
            #logger.debug(f'Subprocess stdout: {result.stdout}')
            #logger.debug(f'Subprocess stderr: {result.stderr}')

            if result.returncode == 0:
                # Load the output image and convert it to base64
                with open(temp_output_path, 'rb') as output_file:
                    output_image_data = output_file.read()
                    output_image_base64 = base64.b64encode(output_image_data).decode('utf-8')

                # Return the base64 encoded output image in the response
                return JsonResponse({'status': 'success', 'message': 'Face swap successful', 'output_image': output_image_base64})
            else:
                return JsonResponse({'status': 'error', 'message': 'Face swap failed', 'error': result.stderr})

        response_data = {
            'image_data': image_data
        }
        return render(request, template, response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
