from django.core.management.base import BaseCommand
from django.core.files import File
from create_face.models import UserImage
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Load default images into the database'

    def handle(self, *args, **kwargs):
        # Check if there is an admin user, if not create one
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('adminpassword')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()

        # Define the path to the default images
        default_images_path = 'static/default_images'
        default_images = ['default1.png']

        for image_name in default_images:
            image_path = os.path.join(default_images_path, image_name)
            # get image binary data
            with open(image_path, 'rb') as f:
                image_data = f.read()
                UserImage.objects.create(user=admin_user, image=image_data)

        self.stdout.write(self.style.SUCCESS('Successfully loaded default images'))