from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import face_recognition
import numpy as np
from cv2 import Mat
from pydantic import Field

from utils import index as utils


@dataclass
class Detector(ABC):

    authors: list = Field(default_factory=list)
    encodings: list = Field(default_factory=list)
    resize_factor: Optional[float] = 0.25

    @abstractmethod
    async def detect(self, image: Mat) -> Tuple[utils.ThreadedGenerator, utils.ThreadedGenerator]:
        pass

@dataclass
class DetectorUnknows(Detector):
    """
    labels (tuple, optional): labels for unknown users and know users. Defaults to ("Unknown" "Know").
    features (list, optional): list of features to save see utils.constants. Defaults to []."""

    labels: tuple = ("Unknown", "Know")
    min_descriptor_distance: Optional[float] = 0.6
    actual_img: np.array = np.array([])

    async def detect(self, image: Mat) -> Tuple[utils.ThreadedGenerator, utils.ThreadedGenerator]:
        """Detect unkwnows in image

        Args:
            image (Mat): image with faces to compare

        Returns:
            Tuple[Tuple[Dict], Tuple[Dict]]: more_similar, less_similar
        """
        self.actual_img = image

        self.reduce_dimensions_image()
        face_locations = face_recognition.face_locations(self.actual_img)
        face_encodings = []

        if not face_locations is None and face_locations != []:
            face_encodings = face_recognition.face_encodings(self.actual_img, face_locations)

        more_similar = []
        less_similar = []

        for idx, face_encoding in enumerate(face_encodings):
            face_distances = face_recognition.face_distance(self.encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

                if face_distances[best_match_index] > self.min_descriptor_distance:
                    less_similar.append({
                        "name": self.labels[0],
                        "location": self.enlarge_dimensions(face_locations[idx]),
                        "distance": face_distances[best_match_index],
                        "encoding": face_encoding,
                        "features": []
                    })
                else:
                    more_similar.append({
                        "name": self.labels[1],
                        "location": self.enlarge_dimensions(face_locations[idx]),
                        "distance": face_distances[best_match_index],
                        "author": self.authors[best_match_index],
                        "encoding": face_encoding,
                        "features": []
                    })
            else:
                less_similar.append({
                    "name": self.labels[0],
                    "location": face_locations[idx],
                    "distance": 0,
                    "encoding": face_encoding,
                    "features": []
                })

        more_similar = utils.ThreadedGenerator(more_similar, daemon=True)
        less_similar = utils.ThreadedGenerator(less_similar, daemon=True)

        return more_similar, less_similar
    
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

        return top, right, bottom, left

    def reduce_dimensions_image(self) -> None:
        """
        Resizes the image to less dimensions"""
        self.actual_img = cv2.resize(
            self.actual_img, 
            dsize = (0, 0), 
            fx = self.resize_factor, 
            fy = self.resize_factor)

    
