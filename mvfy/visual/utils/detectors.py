from ...utils import index as utils
from abc import ABC, abstractmethod
from typing import Iterable
import cv2
import numpy as np
import face_recognition

class Detector(ABC):
    def __init__(self) -> None:
        self.encodings = []
    
    @abstractmethod
    async def load_encodings(self):
        pass

    @abstractmethod
    async def detect_unknowns(self):
        pass

class FaceRecognition(Detector):

    async def load_encodings(self, encodings: Iterable) -> None:
        
        for encoding in encodings:
            if encoding is not None:
                self.encodings.append(encoding)
    
    async def detect_unknowns(self, img: 'np.array', min_descriptor_distance: float, resize_factor: float = 0.25, labels: tuple = ("Unknown" "Know")) -> 'tuple(utils.ThreadedGenerator, utils.ThreadedGenerator)':

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
                    "encoding": face_encoding
                })
            else:
                more_similar.append({
                    "name": labels[1],
                    "location": face_locations[idx],
                    "distance": face_distances[best_match_index],
                    "encoding": face_encoding
                })
        
        more_similar = utils.ThreadedGenerator(more_similar, daemon=True)
        less_similar = utils.ThreadedGenerator(less_similar, daemon=True)

        return more_similar, less_similar
    

    