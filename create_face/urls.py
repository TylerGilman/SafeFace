from django.urls import path

from . import views

urlpatterns = [
    path("create", views.index, name="create"),
    path("create_with_hugging_face", views.create_with_hugging_face, name="create_with_hugging_face"),
]