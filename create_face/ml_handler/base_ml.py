import asyncio
from abc import ABC, abstractmethod
import torch

class BaseMLHandler(ABC):
    def __init__(self, max_queue_size=10):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.cancel_flag = asyncio.Event()
        self.processing_task = None

    @abstractmethod
    async def generate_image(self, prompt):
        pass

    async def add_to_queue(self, prompt):
        future = asyncio.Future()
        await self.queue.put((prompt, future))
        return await future

    async def start_processing(self):
        self.processing_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        while True:
            if self.cancel_flag.is_set():
                self.cancel_flag.clear()
                break
            try:
                prompt, future = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                try:
                    result = await self.generate_image(prompt)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self.queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def cancel_generation(self):
        self.cancel_flag.set()
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        self.processing_task = None
        
class CancellationException(Exception):
    pass