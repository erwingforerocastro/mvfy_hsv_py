from dataclasses import dataclass
import logging

import cv2
import numpy as np
from cv2 import Mat
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional, Tuple
from deepface import DeepFace
import face_recognition

from ....utils import index as utils

@dataclass
class Detector(ABC):

    authors: list = []
    encodings: list = []
    resize_factor: Optional[float] = 0.25

    @abstractmethod
    async def detect(self, image: Mat):
        pass

@dataclass
class DetectorUnknows(Detector):

    labels: Optional[tuple] = ("Unknown" "Know")
    min_descriptor_distance: Optional[float] = 0.6
    actual_img: Optional[np.array] = np.array([])

    async def detect(self, image: Mat) -> Tuple[Tuple[Dict], Tuple[Dict]]:
        """Detect unkwnows in image

        Args:
            image (Mat): image with faces to compare

        Returns:
            Tuple[Tuple[Dict], Tuple[Dict]]: more_similar, less_similar
        """
        self.actual_img = image

        self.redim_image()
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
                        "location": face_locations[idx],
                        "distance": face_distances[best_match_index],
                        "encoding": face_encoding,
                        "features": []
                    })
                else:
                    more_similar.append({
                        "name": self.labels[1],
                        "location": face_locations[idx],
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
        
    def redim_image(self) -> None:

        self.actual_img = cv2.resize(
            self.actual_img, 
            disize = (0, 0), 
            fx = self.resize_factor, 
            fy = self.resize_factor)

        self.actual_img = self.actual_img[:, :, ::-1]  # BGR to RBG
    
