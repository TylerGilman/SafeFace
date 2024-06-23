from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse

@csrf_exempt
def swap_face(request):
    if request.method == 'POST':
        if request.POST.get(('csrf_token') != get_token(request)):
            return JsonResponse({'error': 'Invalid CSRF token'}, status=400)
        template = 'swap_face.html'
        if request.POST.get('render_mode') == 'content':
            template = 'swap_face_content.html'
        image_path = request.POST.get('image_data')
        
        if not image_path:
            return JsonResponse({'error': 'No image data provided'}, status=400)

        response_data = {
            'image_path': image_path
        }
        return render(request, template, response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
