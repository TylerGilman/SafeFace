from django.db import models
from django.contrib.auth.models import User


class UserImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_path = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
