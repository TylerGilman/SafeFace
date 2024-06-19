import requests
from PIL import Image
import io
from .base_ml import BaseMLHandler


class HuggingFaceHandler(BaseMLHandler):
    def __init__(self):
        super().__init__()
        self.API_URL = "https://api-inference.huggingface.co/models/Corcelio/mobius"
        self.headers = {"Authorization": "Bearer REPLACE_ME"}

    @BaseMLHandler.handle_errors
    def query_hugging_face(self, payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload)
        return response.content

    @BaseMLHandler.handle_errors
    def generate_image(self, prompt):
        image_bytes = self.query_hugging_face({"inputs": prompt})
        return Image.open(io.BytesIO(image_bytes))
