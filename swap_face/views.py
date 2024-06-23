from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse
import base64
from PIL import Image
from io import BytesIO


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

        filename = request.POST.get('filename')
        print("image_path: ", image_data)
        print("filename: ", filename)
        # Swap if the post request sends a image_data and a filename
        if image_data and filename:
            # Swap Time
            uploaded_file_data = request.POST.get('uploaded_file')
            image_data = request.POST.get('image_data')

            # Process the uploaded_file_data (if it's base64 encoded)
            if uploaded_file_data:
                uploaded_file_data = uploaded_file_data.split('base64,')[1]
                uploaded_file_data = base64.b64decode(uploaded_file_data)
                uploaded_image = Image.open(BytesIO(uploaded_file_data))

            # Process the image_data (if it's base64 encoded)
            image_data = image_data.split('base64,')[1]
            image_data = base64.b64decode(image_data)
            image_data = Image.open(BytesIO(image_data))

            # Handle the uploaded_file and image_data
            # Perform face swap operation

            # Return appropriate response
            return JsonResponse({'status': 'success', 'message': 'Face swap successful'})

            response_data = {
                'image_path': image_data,
                'filename': filename,
            }
            return render(request, template, response_data)

        response_data = {
            'image_data': image_data
        }
        return render(request, template, response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

