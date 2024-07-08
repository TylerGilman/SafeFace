from django.contrib import admin
from django.urls import include, path
from django.conf import settings   # Application settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # Static files serving
from django.views.generic import RedirectView  # For redirecting root URL
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/auth/', permanent=True)),
    path('create/', include('create_face.urls')),
    path('swap_face/', include('swap_face.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('login/', RedirectView.as_view(url='/auth/login/', permanent=True)),
] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

