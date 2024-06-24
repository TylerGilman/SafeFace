from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse
import base64
from PIL import Image
from io import BytesIO
import subprocess


@csrf_exempt
def swap_face(request):
    if request.method == 'POST':
        
        template = 'swap_face.html'
        if request.POST.get('render_mode') == 'content':
            template = 'swap_face_content.html'

        image_data = request.POST.get('image_data')
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)

        uploaded_file = request.POST.get('uploaded_file')
        if image_data and uploaded_file:
            try:
                # Process the uploaded_file_data (if it's base64 encoded)
                uploaded_file_data = uploaded_file.split('base64,')[1]
                uploaded_file_data = base64.b64decode(uploaded_file_data)
                uploaded_image = Image.open(BytesIO(uploaded_file_data))

                # Convert the uploaded image to bytes
                uploaded_file_bytes = BytesIO()
                uploaded_image.save(uploaded_file_bytes, format='JPEG')
                uploaded_file_bytes = uploaded_file_bytes.getvalue()

                # Process the image_data (if it's base64 encoded)
                image_data = image_data.split('base64,')[1]
                image_data = base64.b64decode(image_data)
                image_data = Image.open(BytesIO(image_data))

                # Convert the image data to bytes
                image_data_bytes = BytesIO()
                image_data.save(image_data_bytes, format='JPEG')
                image_data_bytes = image_data_bytes.getvalue()

                # Call the face swap script using subprocess
                command = "./swap_face/facefusion/run.py"
                process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Send the image data to the script
                stdout_data, stderr_data = process.communicate(input=image_data_bytes + b'\n' + uploaded_file_bytes)

                if process.returncode != 0:
                    return JsonResponse({'error': f'Face swap failed: {stderr_data.decode("utf-8")}'}, status=500)

                # The script should output the result image data
                output_image_data = stdout_data.strip()

                # Return the swapped face image as a response
                swapped_image_base64 = base64.b64encode(output_image_data).decode('utf-8')
                return JsonResponse({'status': 'success', 'swapped_image': swapped_image_base64})

            except subprocess.CalledProcessError as e:
                return JsonResponse({'error': f'Face swap failed: {e}'}, status=500)
            except Exception as e:
                return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

        response_data = {'image_data': image_data}
        return render(request, template, response_data)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
