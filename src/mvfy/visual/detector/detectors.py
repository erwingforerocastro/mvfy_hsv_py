from abc import ABC
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import time
from typing import Any, Optional, Tuple

import cv2
import face_recognition
import numpy as np
from cv2 import Mat
from mvfy.visual.func import loop_manager


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

        result = np.multiply(location, (1/self.resize_factor))

        return tuple(result) 
    
@dataclass
class DetectorFacesCPU(Detector):

    tolerance_comparation: float = 0.3
    model: str = "small"
    num_thread_pool_executors: int = 2

    @loop_manager
    async def get_encodings(self, image: Mat, loop: 'asyncio.AbstractEventLoop') -> Tuple[list, list]:
        """Detect encodings of faces in image

        Args:
            image (Mat): image with faces to compare

        Returns:
            Tuple[List, List]: [List of locations faces, List of 128-dimensional face encodings]
        """
        face_encodings, face_locations = [], []
        _time = time.time()

        reduced_image = self.reduce_dimensions_image(image)

        print(f"image resize {time.time()-_time}")
        _time = time.time()

        with ThreadPoolExecutor(self.num_thread_pool_executors) as executor:

            face_locations = await loop.run_in_executor(executor, face_recognition.face_locations, reduced_image) 

            print(f"face locations {time.time()-_time}")
            _time = time.time()

            if len(face_locations) > 0:
                face_encodings = await loop.run_in_executor(
                    executor, 
                    lambda: face_recognition.face_encodings( 
                    reduced_image, 
                    face_locations, 
                    model=self.model
                    ))
                print(f"face encodings {time.time()-_time}")
                _time = time.time()

        face_locations_resized = list(np.multiply(face_locations, (1 / self.resize_factor)).astype(int))
        
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

    
