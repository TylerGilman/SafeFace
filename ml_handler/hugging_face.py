from PIL import Image
import io
from .base_ml import BaseMLHandler

API_URL = "https://api-inference.huggingface.co/models/Corcelio/mobius"
headers = {"Authorization": "Bearer REPLACE_ME"}

class HuggingFaceHandler(BaseMLHandler):
    @BaseMLHandler.handle_errors
    def query_hugging_face(self, payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.content

    @BaseMLHandler.handle_errors
    def generate_image(self, prompt):
        image_bytes = self.query_hugging_face({"inputs": prompt})
        return Image.open(io.BytesIO(image_bytes))
