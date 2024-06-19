from django.contrib import admin
from django.urls import path
from authentication.views import home, login_page, register_page
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
    path('', home, name="home"),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register'),
]