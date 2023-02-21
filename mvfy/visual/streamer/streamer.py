import logging
import os
import time
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, Generator, Optional, Tuple

import cv2
from flask import render_template_string
from mvfy.visual.generator.image_generator import ImageGenerator
from pydantic.dataclasses import dataclass

from .errors import StreamTemplateNotFound


class Streamer(ABC):

    @abstractmethod
    async def send(self, image: Any)-> bytes:
        pass 

@dataclass
class FlaskStreamer(Streamer):

    extension: Optional[str] = ".jpg"
    resize: Optional[Tuple[int, int]] = None
    framerate: int = 30

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
        
  
    def send(self, image: Any)-> bytes:
        """_summary_

        :return: _description_
        :rtype: _type_
        """       
        #TODO: optimize the fluency of the video
        
        try:
            flag = False
            if image is not None:
                flag, resize_image = cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80])

            if flag:
                time.sleep(1 / self.framerate)
                images_bytes: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(resize_image) + b'\r\n'
                return images_bytes
        except Exception as error:
            logging.error(f"Error sending the image, {error}")
        
        
