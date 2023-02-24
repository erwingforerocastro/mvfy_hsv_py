from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple

import cv2
import face_recognition
import numpy as np
from cv2 import Mat
from mvfy.entities.visual_knowledge_entities import User
from utils import index as utils


@dataclass
class Detector(ABC):

    authors: list = field(default_factory=list)
    encodings: list = field(default_factory=list)
    resize_factor: Optional[float] = 0.25

    
    def reduce_dimensions_image(self) -> None:
        """
        Resizes the image to less dimensions"""
        self.actual_img = cv2.resize(
            self.actual_img, 
            dsize = (0, 0), 
            fx = self.resize_factor, 
            fy = self.resize_factor)

    def enlarge_dimensions(self, location: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Enlarges the location to the image size"""

        return_size = 1 / self.resize_factor
        (top, right, bottom, left) = location

        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= return_size
        right *= return_size
        bottom *= return_size
        left *= return_size

        return tuple(map(int, (top, right, bottom, left))) 
    
@dataclass
class DetectorFaces(Detector):

    actual_img: np.ndarray = np.array([])
    face_locations: list = field(default_factory=list)
    
    async def get_encodings(self, image: Mat) -> list:
        """Detect encodings of faces in image

        Args:
            image (Mat): image with faces to compare

        Returns:
            List: List of 128-dimensional face encodings
        """
        self.actual_img = image

        self.reduce_dimensions_image()
        self.face_locations = face_recognition.face_locations(self.actual_img)
        face_encodings = []

        if not (self.face_locations is None and self.face_locations != []):
            face_encodings = face_recognition.face_encodings(self.actual_img, self.face_locations)
        
        return face_encodings

    async def compare(self, encoding: list[np.ndarray]) -> np.ndarray:

        return face_recognition.face_distance(self.encodings, encoding)
    

    
