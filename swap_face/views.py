from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse

@csrf_exempt
def swap_face(request):
    if request.method == 'POST':
        image_path = request.POST.get('image_data')
        
        if not image_path:
            return JsonResponse({'error': 'No image data provided'}, status=400)

        response_data = {
            'image_path': image_path
        }
        return render(request, "swap_face.html", response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
