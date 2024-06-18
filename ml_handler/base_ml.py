import torch
from abc import ABC, abstractmethod

class BaseMLHandler(ABC):
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @abstractmethod
    def generate_image(self, prompt):
        pass

    def handle_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
        return wrapper
