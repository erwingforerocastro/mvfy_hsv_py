from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, Optional, Tuple

import cv2
import numpy as np
from pydantic.dataclasses import dataclass


@dataclass
class ImageGenerator(ABC):

    dimensions: Tuple[int, int] = (720, 480)
    wait_message: Optional[str] = "wait"
    wait_image: Any = None
    images_queue: Queue = Queue()
    
    class Config:
        arbitrary_types_allowed = True

    def __post_init__(self) -> None:
        self.create_wait_image()

    @abstractmethod
    def __aiter__(self) -> None:
        pass
    
    def create_wait_image(self) -> None:
        """_summary_
        """
        if self.wait_image is None:
            self.wait_image = np.zeros([*self.dimensions, 1], dtype = np.uint8)

        center_image = (self.wait_image.shape[0] // 2, self.wait_image.shape[1] // 2)
        self.wait_image = cv2.putText(self.wait_image, self.wait_message, center_image, cv2.CV_FONT_HERSHEY_SIMPLEX, 2, 255)

    async def put_wait_image(self) -> None:
        
        await self.images_queue.put(self.wait_image)
