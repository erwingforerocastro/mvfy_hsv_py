import inspect
import logging
import cv2
import numpy as np
import math
import func
import asyncio
import uuid

from utils import constants as const, index as utils
from utils.detectors import Detector
from utils.streamer import Streamer
from data_access.visual_knowledge_db import SystemDB, UserDB
from datetime import datetime

class VisualKnowledge:

    def __init__(self,
    type_service: 'str',
    db_properties: dict,
    db_name: str,
    max_descriptor_distance: float,
    min_date_knowledge: float,
    min_frequency: float = 0.7,
    features: dict = {},
    type_system: str = "OPTIMIZED",
    title: str = None) -> None:
        
        """
        Main model builder

        constructor
        :Parameters:
            {String} type_service - type of the listen server.
            {Dict} db - proprties of bd see https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient.
            {String} db_name - name of db to be used.
            {Array} min_date_knowledge [min_date_knowledge=null] - minimum interval to determine a known user.
            {Number} min_frequency [min_frequency=0.7] - minimum frequency between days detectioned.
            {String} features [features=null] - characteristics that will be saved in each detection.
            {String} max_descriptor_distance [max_descriptor_distance=null] - max distance of diference between detections.
            {String} type_system [type_system=null] - type of system.
            {String} title [title=null] - title of system.

        :Returns:
            None.

        """
        #properties
        self.id = None
        self.type_service = type_service
        self.title = str(uuid.uuid4()) if title is None else title
        self.features = features
        self.min_date_knowledge = min_date_knowledge
        self.min_frequency = min_frequency
        self.max_descriptor_distance = max_descriptor_distance
        self.type_system = type_system
        
        #agents 
        self.detector = None
        self.receiver = None
        self.streamer = None
        self.stream_fps = 30

        #more info
        self.type_model_detection = None
        self.display_size = { "width": 300, "height": 300 }
        self.matches = None
        self.interval_streaming = None
        self.execution = False

        #DB
        self.db_systems = SystemDB(
            properties = db_properties,
            db = db_name,
            collection = const.COLLECTIONS["SYSTEMS"]
        )
        self.db_users = UserDB(
            properties = db_properties,
            db = db_name,
            collection = const.COLLECTIONS["USERS"]
        )
        
    def set_conf(self, 
    receiver: 'function',
    detector: 'Detector',
    streamer: 'Streamer',
    stream_fps: float = 30,
    display_size: dict = None,
    ) -> None:
        """Set configuration parameters for this instance .

        Args:
            receiver (function): provider of streaming video
            detector (Detector): face detector 
            streamer (Streamer): send result of streaming video
            stream_fps (float, optional): frame per second inside video. Defaults to 30.
            display_size (dict, optional): size of image process. Defaults to None.
        """
        self.receiver = receiver
        self.detector = detector
        self.streamer = streamer
        self.stream_fps = stream_fps

        #more info
        self.display_size = display_size if display_size is not None else self.display_size

    def get_obj(self) -> dict:
        """Get a dict of the attributes for this instance.

        Returns:
            dict: instance relevant features
        """
        return {
            "title": self. title,
            "type_service": self. type_service,
            "max_descriptor_distance": self. max_descriptor_distance,
            "min_date_knowledge": self. min_date_knowledge,
            "min_frequency": self. min_frequency,
            "features": self. features,
            "type_system": self. type_system,
            "id": self. id,
            "created_on": self. created_on,
            "modified_on": self. modified_on,
        }

    async def start(self, cb: 'function') -> None:
        
        # found or add system
        system = await func.get_system(self.get_obj(), self.db_systems)
        if system is None:
            system = await func.insert_system(self.get_obj(), self.db_users)
            if system is None:
                raise ValueError("Error to create or find system")

        #get descriptors
        users_queue = await func.load_user_descriptors(
            system_id = self.id,
            db = self.db_users
        )

        #load descriptors
        self.detector.load_encodings(encodings=users_queue)

        while True: 
            img = next(self.receiver())
            if img is not None:
                img_processed = await self.process_unknows(img)
                await self.streamer(img = img_processed, size = None, title = self.title)

    async def process_unknows(self, img: np.array, resize_factor: float = 0.25, draw_label: bool = False, labels: tuple = ("Unknown" "Know")) -> None:

        _, less_similar = await self.detector.detect_unknowns(img, (1 - self.max_descriptor_distance), resize_factor, labels)

        # Display the results
        return_size = 1 / resize_factor

        for detection in less_similar:
                
            (top, right, bottom, left) = detection["location"]
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= return_size
            right *= return_size
            bottom *= return_size
            left *= return_size

            # Draw a box around the face
            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)

            if draw_label is True:
                # Draw a label with a name below the face
                cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(img, detection["name"], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
            #save information of detection
            await self.set_detection({
                "system_id": self.id,
                "detection": "",
                "author": "",
                "detection": self.detection,
                "properties": self.properties,
                "init_date": self.init_date,
                "last_date": self.last_date,
                "knowledge": self.knowledge,
                "frequency": self.frequency,
                "author": self.author,
            })
            

    async def set_detection(self, user: dict) -> None:
        try:    
            await func.insert_user(user, self.db_users)
        except Exception as e:
            logging.error(f"set_detection error to insert detection, {e}")