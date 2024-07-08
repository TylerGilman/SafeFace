from django.contrib import admin
from django.urls import path
from authentication.views import home_page, login_page, register_page, logout_view
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
    path('login/', login_page, name='login_page'),
    path('', home_page, name='home_page'),
    path('register/', register_page, name='register'),
    path('logout/', logout_view, name='logout'),
]

# Make sure to add this decorator to your URL pattern
#from asgiref.sync import async_to_sync
#create_with_pipeline = async_to_sync(create_with_pipeline)