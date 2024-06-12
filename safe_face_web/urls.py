from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("create_face.urls")),
    path("admin/", admin.site.urls),
]