from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
import time
from typing import Any, Optional, Tuple

import cv2
import face_recognition
import numpy as np
from cv2 import Mat
from mvfy.entities.visual_knowledge_entities import User
from mvfy.visual.func import loop_manager
from utils import index as utils


@dataclass
class Detector(ABC):

    authors: list = field(default=np.empty((0)))
    encodings: list = field(default=np.empty((0, 128)))
    resize_factor: Optional[float] = 0.25

    def reduce_dimensions_image(self, image: Any) -> Mat:
        """
        Resizes the image to less dimensions"""
        return cv2.resize(
            image, 
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
class DetectorFacesCPU(Detector):

    tolerance_comparation: float = 0.3

    @loop_manager
    async def get_encodings(self, image: Mat, loop: 'asyncio.AbstractEventLoop') -> Tuple[list, list]:
        """Detect encodings of faces in image

        Args:
            image (Mat): image with faces to compare

        Returns:
            Tuple[List, List]: [List of locations faces, List of 128-dimensional face encodings]
        """
        face_encodings, face_locations = [], []
        reduced_image = self.reduce_dimensions_image(image)

        face_locations = await loop.run_in_executor(None, face_recognition.face_locations, reduced_image) 

        if len(face_locations) > 0:
            face_encodings = await loop.run_in_executor(
                None, 
                face_recognition.face_encodings, 
                reduced_image, 
                face_locations, 
                {"model": "large"}
                )

        face_locations_resized = await loop.run_in_executor(
            None, 
            lambda: list(map(self.enlarge_dimensions, face_locations)))

        return face_locations_resized, face_encodings

    @loop_manager
    async def compare(self, encoding: np.ndarray, loop: 'asyncio.AbstractEventLoop') -> list[bool]:
        res = await loop.run_in_executor(
            None, 
            lambda: face_recognition.compare_faces(
                self.encodings, 
                encoding, 
                tolerance = self.tolerance_comparation))
        
        return res
    
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

        reduced_image = self.reduce_dimensions_image(image)
        self.face_locations = face_recognition.face_locations(self.actual_img)
        face_encodings = []

        if not (self.face_locations is None and self.face_locations != []):
            face_encodings = face_recognition.face_encodings(self.actual_img, self.face_locations)

        return face_encodings

    async def compare(self, encoding: np.ndarray) -> np.ndarray:

        return face_recognition.face_distance(self.encodings, encoding)

    
