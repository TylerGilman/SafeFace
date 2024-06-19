from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("create_face.urls")),
    path("create/", include("create_face.urls")),
    path("swap_face/", include("swap_face.urls")),
    path("admin/", admin.site.urls),
]
