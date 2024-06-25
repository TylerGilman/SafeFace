from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="create"),
    path("save_image/", views.save_image, name="save_image"),
    path("delete/<int:id>/", views.delete_image, name="delete_image"),
]
