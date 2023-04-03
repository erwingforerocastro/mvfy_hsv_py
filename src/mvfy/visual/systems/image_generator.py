from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, Optional, Tuple

import cv2
import numpy as np
from pydantic.dataclasses import dataclass


@dataclass
class ImageGenerator(ABC):

    dimensions: Tuple[int, int] = (720, 480)
    wait_message: str = "wait...."
    wait_image: Any = None
    images_queue: Any = None
    images_queue_size: int = 0

    class Config:
        arbitrary_types_allowed = True

    def create_wait_image(self) -> None:
        """_summary_
        """
        self.wait_image = np.zeros([self.dimensions[1], self.dimensions[0], 1], dtype = np.uint8)
        center_image = (self.wait_image.shape[1] // 2, self.wait_image.shape[0] // 2)
        self.wait_image = cv2.putText(self.wait_image, self.wait_message, center_image, cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

    def put_image(self, image: 'Any') -> None:
        """ put image inside queue """
        self.images_queue.put_nowait(image)
        self.images_queue_size += 1
    
    def get_image(self) -> Any:
        """get first image inside queue or wait image if empty"""
        
        if self.images_queue_size == 0:
            return self.wait_image

        _image = self.images_queue.get_nowait()
        self.images_queue_size -= 1

        return _image

    @abstractmethod
    def __iter__(self) -> None:
        pass
