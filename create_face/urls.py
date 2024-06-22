from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="create"),
    path("save_image/", views.save_image, name="save_image"),
]
