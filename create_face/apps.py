from django.apps import AppConfig
from django.apps import apps
import asyncio

class CreateFaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "create_face"

    def ready(self):
        # This method is called by Django during startup
        from .ml_handler import pipeline_handler
        self.pipeline_handler = pipeline_handler

# Create a function to start the processing
async def start_pipeline_processing():
    # Get the app config from Django's app registry
    config = apps.get_app_config('create_face')
    if hasattr(config, 'pipeline_handler'):
        await config.pipeline_handler.start_processing()
    else:
        print("Warning: pipeline_handler not found in app config")
        