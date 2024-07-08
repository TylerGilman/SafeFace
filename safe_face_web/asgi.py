import os
from django.core.asgi import get_asgi_application
from create_face.apps import start_pipeline_processing
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safe_face_web.settings')

django_asgi_app = get_asgi_application()

async def application(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                # Start the pipeline processing
                await start_pipeline_processing()
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        await django_asgi_app(scope, receive, send)