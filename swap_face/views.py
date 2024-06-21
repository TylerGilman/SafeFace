from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from PIL import Image
import base64


@csrf_exempt
def swap_face(request):
    image_data = request.GET.get('image_data')
    if image_data:
        try:
            # Decode the base64 image data
            image_data = image_data.split(",")[1] if "," in image_data else image_data
            image = Image.open(BytesIO(base64.b64decode(image_data)))
            
            # Process the image (e.g., swap face)
            # Your face-swapping logic here
            
            # Save the processed image to a BytesIO object
            image_io = BytesIO()
            image.save(image_io, format='PNG')
            image_io.seek(0)
            
            # Encode the processed image in base64
            image_base64 = base64.b64encode(image_io.read()).decode('utf-8')
            image_data = f"data:image/png;base64,{image_base64}"
            
            # Render the template with the base64 image
            return render(request, "avatar_display.html", {
                "generate_method": "swap_face",
                "image_path": image_data
            })
        except Exception as e:
            return render(request, "error.html", {"message": str(e)})
    else:
        return render(request, "error.html", {"message": "No image data provided."})
