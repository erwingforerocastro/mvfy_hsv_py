import os
import cv2
from typing import Optional, Tuple
from abc import ABC, abstractmethod
from flask import Response
from pydantic import BaseModel
from queue import Queue
from mvfy.visual.utils.streamer.errors import StreamTemplateNotFound
from visual.utils import constants

class Streamer(BaseModel, ABC):
    image_generator: ImageGenerator
    image: Optional[Array] = None
    images_queue: Queue = Queue(30)

    @abstractmethod
    def start(self) -> None:
        pass 

class FlaskStreamer(Streamer):

    resize: Optional[Tuple[int, int]]
    extension: Optional[str] = ".jpg"
    
    @property
    def url_template(self) -> str:

        dir_name: str = os.path.dirname(os.path.abspath(__file__))
        template_file: str = os.path.join(dir_name, "stream_flask_template.html")
        
        if not os.path.exists(template_file):
            raise StreamTemplateNotFound(path_file = template_file)
        
        return template_file
        
    async def start(self)-> None:

        while True:

            image = self.image_generator()

            if image is not None:

                if self.resize is not None:

                    image = cv2.resize(image, self.resize)

                flag, buffer = cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                if not flag:
                    self.image = buffer
            
            await self.__save()
            yield await self.__send()
            

    async def __save(self) -> None:

        await self.images_queue.put(self.image)

    async def __send(self) -> None:

        frame: bytearray = await self.images_queue.get()
        images_bites: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        self.images_queue.task_done()

        return Response(images_bites, mimetype="multipart/x-mixed-replace; boundary=frame")
