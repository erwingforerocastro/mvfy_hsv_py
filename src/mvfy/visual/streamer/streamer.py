import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, Generator, Optional, Tuple

import cv2
from flask import render_template_string
import numpy as np
from mvfy.visual.func import loop_manager
from mvfy.visual.systems.image_generator import ImageGenerator
from pydantic.dataclasses import dataclass

from .errors import StreamTemplateNotFound


class Streamer(ABC):

    @abstractmethod
    def send(self, image: Any, execution_time: float)-> bytes:
        pass 

@dataclass
class FlaskStreamer(Streamer):

    dimensions: Tuple[int, int] = (720, 480)
    extension: Optional[str] = ".jpg"
    resize: Optional[Tuple[int, int]] = None
    images_queue: Optional[Any] = None
    images_queue_size: int = 0
    wait_message: str = "wait...."
    wait_image: Any = None
    framerate: int = 24
    end_time_return: float = time.time()

    def __post_init__(self):
        self.images_queue = Queue()
        self.create_wait_image()

    def get_template(self) -> str:
        """_summary_

        :raises StreamTemplateNotFound: _description_
        :return: _description_
        :rtype: str
        """        
        dir_name: str = os.path.dirname(os.path.abspath(__file__))
        template_path: str = os.path.join(dir_name, "stream_flask_template.html")
        
        if not os.path.exists(template_path):
            raise StreamTemplateNotFound(path_file = template_path)
        
        with open(template_path, "r", encoding = "utf-8") as f:
            template = f.read()

        return render_template_string(template, title = "mvfy_visual")

    def create_wait_image(self) -> None:
        """_summary_
        """
        self.wait_image = np.zeros([self.dimensions[1], self.dimensions[0], 1], dtype = np.uint8)
        center_image = (self.wait_image.shape[1] // 2, self.wait_image.shape[0] // 2)
        self.wait_image = cv2.putText(self.wait_image, self.wait_message, center_image, cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        flag, resize_image = cv2.imencode(self.extension, self.wait_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if flag:
            self.wait_image: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(resize_image) + b'\r\n'
    
    @loop_manager
    async def img2bytes(self, image, loop: 'asyncio.AbstractEventLoop') -> bytes:

        images_bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray() + b'\r\n'
        flag, resize_image = await loop.run_in_executor(None, lambda: cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80]))

        if flag:
            images_bytes: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(resize_image) + b'\r\n'
        
        return images_bytes
    
    async def save(self, batch_images: list[Any]) -> Any:

            tasks = [self.img2bytes(img) for img in batch_images]
            results = await asyncio.gather(*tasks)

            for result in results:
                await self.images_queue.put(result)
                self.images_queue_size += 1

    def send(self)-> bytes:
        """_summary_

        :return: _description_
        :rtype: _type_
        """       
        #TODO: optimize the fluency of the video
        
        try:
            
            while self.images_queue.empty():
                time.sleep(0.1)

            image_to_send = self.images_queue.get_nowait()
            self.images_queue_size -= 1

            # wait = (1 / self.framerate) - (time.time() - self.end_time_return)
            # if wait < 0:
            #     print(f'delay:{wait} ')

            delay_time = max(0, (1 / self.framerate) - (time.time() - self.end_time_return))
            time.sleep(delay_time)

            self.end_time_return = time.time()

            return image_to_send
            
        except Exception as error:
            logging.error(f"Error sending the image, {error}")
            return self.wait_image
    
    def __iter__(self):

        while self.images_queue.empty():
            print("waiting streaming...")
            while self.images_queue.empty():
                time.sleep(1)
                
        return self

    def __next__(self):

        return self.send()
        
        
