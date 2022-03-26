import inspect
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

    async def start(self) -> None:
        
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

        while True: 
            img = next(self.receiver())
            if img is not None:
                await self.process_img(img)
    
    async def process_img(img: np.array) -> None:
        pass