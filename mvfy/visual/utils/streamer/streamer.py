import os
from abc import ABC, abstractmethod
from queue import Queue
from typing import Optional, Tuple

import cv2
from flask import Response
from mvfy.visual.utils.streamer.errors import StreamTemplateNotFound
from mvfy.visual.visual_knowledge import ImageGenerator
from pydantic import BaseModel


class Streamer(BaseModel, ABC):
    image_generator: ImageGenerator
    image: Optional[list] = None
    images_queue: Queue = Queue(30)

    @abstractmethod
    def start(self) -> None:
        pass 
    
    @abstractmethod
    def get_frame(self) -> None:
        pass 

class FlaskStreamer(Streamer):

    resize: Optional[Tuple[int, int]]
    extension: Optional[str] = ".jpg"
    
    @property
    def url_template(self) -> str:
        """_summary_

        :raises StreamTemplateNotFound: _description_
        :return: _description_
        :rtype: str
        """        
        dir_name: str = os.path.dirname(os.path.abspath(__file__))
        template_file: str = os.path.join(dir_name, "stream_flask_template.html")
        
        if not os.path.exists(template_file):
            raise StreamTemplateNotFound(path_file = template_file)
        
        return template_file
        
    async def start(self)-> None:
        """_summary_
        """        
        while True:

            image = self.image_generator()

            if image is not None:

                if self.resize is not None:

                    image = cv2.resize(image, self.resize)

                flag, buffer = cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                if not flag:
                    self.image = buffer
                    await self.images_queue.put(self.image)
            
    async def get_frame(self) -> None:
        """_summary_

        :return: _description_
        :rtype: _type_
        """        
        frame: bytearray = await self.images_queue.get()
        images_bytes: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        self.images_queue.task_done()

        return Response(images_bytes, mimetype="multipart/x-mixed-replace; boundary=frame")
