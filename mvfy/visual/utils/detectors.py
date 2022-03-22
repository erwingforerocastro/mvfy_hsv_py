import cv2
import numpy as np
import face_recognition

class Detector:
    def __init__(self) -> None:
        self.encodings = []
    
    async def load_encodings(self, encodings: list) -> None:
        
        for encoding in encodings:
            if encoding is not None:
                self.encodings.append(encoding)
    
    async def detect_unknowns(self, img: 'np.array', min_descriptor_distance: float, resize_factor: float = 0.25, labels: tuple = ("Unknown" "Know")) -> 'tuple(list, list)':

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
                    "distance": face_distances[best_match_index]
                })
            else:
                less_similar.append({
                    "name": labels[1],
                    "location": face_locations[idx],
                    "distance": face_distances[best_match_index]
                })

        return more_similar, less_similar
    
class FaceRecognition(Detector):
    pass
    

    