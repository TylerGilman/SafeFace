import torch
from abc import ABC, abstractmethod
import asyncio

class BaseMLHandler(ABC):
    def __init__(self, max_queue_size=10):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.processing_task = asyncio.create_task(self._process_queue())

    @abstractmethod
    async def generate_image(self, prompt, cancel_flag):
        pass


    async def _process_queue(self):
        while True:
            prompt, future = await self.queue.get()
            try:
                result = await self.generate_image(prompt, self.cancel_flag)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()
            self.cancel_flag.clear()  # Reset the flag after each generation
            
    def handle_errors(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
        return wrapper