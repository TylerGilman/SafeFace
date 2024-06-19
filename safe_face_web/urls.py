from django.contrib import admin
from django.urls import include, path
from django.conf import settings   # Application settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # Static files serving
from django.views.generic import RedirectView  # For redirecting root URL

urlpatterns = [
    path('', RedirectView.as_view(url='/home/', permanent=True)),  # Redirect root URL to /home/
    path('create/', include('create_face.urls')),
    path('swap_face/', include('swap_face.urls')),
    path('admin/', admin.site.urls),
    path('home/', include('authentication.urls')),
]

# Include static files URL patterns if in debug mode
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()