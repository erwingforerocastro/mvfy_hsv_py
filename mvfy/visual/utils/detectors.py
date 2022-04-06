import logging
from ...utils import index as utils
from abc import ABC, abstractmethod
from typing import Iterable
from deepface import DeepFace
import cv2
import numpy as np
import face_recognition

class Detector(ABC):
    def __init__(self) -> None:
        self.authors = []
        self.encodings = []

    @abstractmethod
    async def load_users(self):
        pass

    @abstractmethod
    async def detect_unknowns(self):
        pass

class FaceRecognition(Detector):

    async def load_users(self, users: Iterable) -> None:
        
        for user in users:
            if user is not None: 
                #{"detection": ..., "author": ...}
                self.authors.append(user["author"])
                self.encodings.append(user["detection"])

    async def detect_unknowns(self, img: 'np.array', min_descriptor_distance: float, resize_factor: float = 0.25, labels: tuple = ("Unknown" "Know"), features: list = []) -> 'tuple(utils.ThreadedGenerator, utils.ThreadedGenerator)':

        small_img = cv2.resize(img, (0, 0), fx=resize_factor, fy=resize_factor) 
        rgb_small_img = small_img[:, :, ::-1] #BGR to RBG

        face_locations = face_recognition.face_locations(rgb_small_img)
        face_encodings = face_recognition.face_encodings(rgb_small_img, face_locations)

        more_similar = []
        less_similar = []

        for idx, face_encoding in enumerate(face_encodings):
            face_distances = face_recognition.face_distance(self.encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if face_distances[best_match_index] > min_descriptor_distance:
                less_similar.append({
                    "name": labels[0],
                    "location": face_locations[idx],
                    "distance": face_distances[best_match_index],
                    "encoding": face_encoding,
                    "features": await self.analyze(rgb_small_img, features) #pendiente
                })
            else:
                more_similar.append({
                    "name": labels[1],
                    "location": face_locations[idx],
                    "distance": face_distances[best_match_index],
                    "author": self.authors[best_match_index],
                    "encoding": face_encoding,
                    "features": await self.analyze(rgb_small_img, features)
                })
        
        more_similar = utils.ThreadedGenerator(more_similar, daemon=True)
        less_similar = utils.ThreadedGenerator(less_similar, daemon=True)

        return more_similar, less_similar
    
    async def analyze(img: np.array, features: list) -> dict:
        """Analyze img face detection

        Args:
            img (np.array): img with face
            features (list): list of features to extract, see `utils.constants` 

        Returns:
            dict: result of analyze
        """
        result = {}
        try:
            result = DeepFace.analyze(img, features)
        except Exception as e:
            logging.error(f"Detector - analyze - error to analyze img {e}")

        return result