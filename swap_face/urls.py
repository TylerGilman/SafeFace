from django.urls import path

from . import views

urlpatterns = [
    path("", views.swap_face, name="index"),
]
