from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("create_with_hugging_face", views.create_with_hugging_face, name="create_with_hugging_face"),
]