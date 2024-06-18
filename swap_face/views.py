from django.shortcuts import render

# Create your views here.
def index(request):
    print("Hello, world!")
    return render(request, "swap_face.html")