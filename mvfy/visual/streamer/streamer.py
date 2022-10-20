import asyncio
import os
from abc import ABC, abstractmethod
from multiprocessing import Queue
from typing import Any, Optional, Tuple

import cv2
from flask import Response
from mvfy.visual.generator.image_generator import ImageGenerator
from pydantic.dataclasses import dataclass

from .errors import StreamTemplateNotFound


@dataclass
class Streamer(ABC):
    image_generator: ImageGenerator
    image: Optional[list] = None
    images_queue: Optional[Any] = None

    @abstractmethod
    async def start(self) -> None:
        pass 
    
    @abstractmethod
    def get_frame(self) -> None:
        pass 

@dataclass
class FlaskStreamer(Streamer):

    extension: Optional[str] = ".jpg"
    resize: Optional[Tuple[int, int]] = None

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

        return template
        
    async def start(self)-> None:
        """_summary_
        """        
        self.images_queue: Queue = Queue()

        for image in await self.image_generator:

            if image is not None:

                if self.resize is not None:

                    image = cv2.resize(image, self.resize)

                flag, buffer = cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                if not flag:
                    self.image = buffer
                    print("saving image...")
                    await self.images_queue.put(self.image)
            
    def get_frame(self) -> Response:
        """_summary_

        :return: _description_
        :rtype: _type_
        """        
        frame: bytearray = self.images_queue.get_nowait()
        images_bytes: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

        return Response(images_bytes, mimetype="multipart/x-mixed-replace; boundary=frame")
