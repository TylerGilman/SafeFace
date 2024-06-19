import requests
from PIL import Image
import io
from .base_ml import BaseMLHandler
from dotenv import load_dotenv
import os

load_dotenv()


class HuggingFaceHandler(BaseMLHandler):
    def __init__(self):
        super().__init__()
        self.API_URL = "https://api-inference.huggingface.co/models/Corcelio/mobius"
        self.headers = {"Authorization": "Bearer " + os.getenv("HUGGING_FACE_INFERENCE_API_KEY")}

    @BaseMLHandler.handle_errors
    def query_hugging_face(self, payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.content.decode('utf-8')}")
        return response.content

    @BaseMLHandler.handle_errors
    def generate_image(self, prompt):
        image_bytes = self.query_hugging_face({"inputs": prompt})
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return image
        except IOError:
            print(f"Received response: {image_bytes.decode('utf-8')}")
            raise Exception("Failed to generate image, received non-image response")
