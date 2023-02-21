import asyncio
import logging
import time
import uuid
from asyncio import Queue
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional
from bson import ObjectId

import cv2
import numpy as np
from apscheduler.triggers.cron import CronTrigger
from data_access.visual_knowledge_db import SystemDB, UserDB
from pydantic import Field
from tzlocal import get_localzone
from mvfy.entities.visual_knowledge_entities import User
from utils import constants as const, index as utils

from mvfy.visual import func
from mvfy.visual.detector import Detector
from mvfy.visual.generator.image_generator import ImageGenerator
from mvfy.visual.receiver.receivers import Receiver
from mvfy.visual.streamer import Streamer

from . import errors


@dataclass
class VisualKnowledge(ImageGenerator):

    detector: Optional[Detector] = None
    receiver: Optional[Receiver] = None
    streamer: Optional[Streamer] = None
    type_service: Optional[str] = None
    db_properties: Optional[dict] = None
    db_name: Optional[str] = None
    max_descriptor_distance: Optional[float] = None
    min_date_knowledge: Optional[float] = None
    min_frequency: Optional[float] = 0.7
    resize_factor: Optional[float] = 0.25
    features: Optional[list] = Field(default_factory = list)
    type_system: Optional[str] = const.TYPE_SYSTEM["OPTIMIZED"]
    title: Optional[str] = str(uuid.uuid4())
    delay: int = 30

    """
    Main model builder

    constructor
    :Parameters:
        {String} type_service - type of the listen server.
        {Dict} db - proprties of bd see https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient.
        {String} db_name - name of db to be used.
        {Array} min_date_knowledge [min_date_knowledge=null] - minimum interval to determine a known user.
        {Number} min_frequency [min_frequency=0.7] - minimum frequency between days detectioned.
        {list} features [features=null] - characteristics that will be saved in each detection.
        {String} max_descriptor_distance [max_descriptor_distance=null] - max distance of diference between detections.
        {String} type_system [type_system=null] - type of system.
        {String} title [title=null] - title of system.

    :Returns:
        None.

    """
    def __post_init__(self):

        #properties
        self.id = None

        #more info
        self.execution = False
        self.date_format = const.DATE_FORMAT
        self.draw_label = True
        self.cron_reload = self.__get_cron_trigger()

        #DB
        self.db_systems = SystemDB(
            properties = self.db_properties,
            db = self.db_name,
            collection = const.COLLECTIONS["SYSTEMS"]
        )
        self.db_users = UserDB(
            properties = self.db_properties,
            db = self.db_name,
            collection = const.COLLECTIONS["USERS"]
        )

        self.images_queue: Queue = Queue()

        self._thread = utils.run_async_in_thread(self.start())
    
    def __iter__(self):
        
        while self.images_queue.empty() or self.images_queue_size < self.delay:
            print("waiting video-cam...")
            time.sleep(1)

        return self
    
    def __next__(self):
        
        _image = self.wait_image

        if not self.images_queue.empty():
            _image = asyncio.run(self.get_image())

        return self.streamer.send(_image)

    async def __preload(self) -> None:
        """ 
            Load system and users if exist

            Search the system or saved it
            Search the users of the system
        """
        print("reloading system...")
        # found or add system
        system = await func.get_system(self.get_obj(), self.db_systems)
        if system is None:
            system = await func.insert_system(self.get_obj(), self.db_systems)
            if system is None:
                raise errors.SystemNotFoundError(str(self.db_systems))

        #insert system found in instance
        self.__insert_system(system)

        #get descriptors
        await self.insert_known_users()
        await self.insert_unknown_users()

    async def insert_known_users(self, users: list[User]):
        users = await func.get_users(
            {"system_id": ObjectId(self.id), "knowledge": True},
            db = self.db_users
        )

        if users is not None:
            authors, encodings = zip(*((user.author, user.detection) for user in users))
            self.detector.authors =  authors
            self.detector.encodings =  encodings

    async def insert_unknown_users(self, users: list[User]):
        users = await func.get_users(
            {"system_id": ObjectId(self.id), "knowledge": False},
            db = self.db_users
        )

        if users is not None:
            authors, encodings = zip(*((user.author, user.detection) for user in users))
            self.detector.authors =  authors
            self.detector.encodings =  encodings

    def __get_cron_trigger(self) -> CronTrigger:
        """get crontrigger of now every day

        Returns:
            CronTrigger: trigger of action
        """
        _date = datetime.now(tz=get_localzone())
        return CronTrigger(hour=_date.hour, minute=_date.minute, second=_date.second, timezone=get_localzone())

    def __insert_system(self, system: dict) -> None:
        """Insert system inside actual instance

        Args:
            system (dict): values to be replaced in instance
        """
        self.id = system["id"]
        self.type_service = system["type_service"] if system["type_service"] is not None else self.type_service
        self.title = system["title"] if system["title"] is not None else self.title
        self.features = system["features"] if system["features"] is not None else self.features
        self.min_date_knowledge = system["min_date_knowledge"] if system["min_date_knowledge"] is not None else self.min_date_knowledge
        self.min_frequency = system["min_frequency"] if system["min_frequency"] is not None else self.min_frequency
        self.max_descriptor_distance = system["max_descriptor_distance"] if system["max_descriptor_distance"] is not None else self.max_descriptor_distance
        self.type_system = system["type_system"] if system["type_system"] is not None else self.type_system
        self.resize_factor = system["resize_factor"] if system["resize_factor"] is not None else self.resize_factor

    def set_conf(self,
    date_format: Optional[str] = None,
    draw_label: Optional[bool] = None,
    cron_reload: Optional[CronTrigger] = None,
    ) -> None:
        """_summary_

        :param date_format: _description_, defaults to None
        :type date_format: Optional[str], optional
        :param draw_label: _description_, defaults to None
        :type draw_label: Optional[bool], optional
        :param cron_reload: _description_, defaults to None
        :type cron_reload: Optional[CronTrigger], optional
        """

        #more info
        self.date_format = date_format if date_format is not None else self.date_format
        self.draw_label = draw_label if draw_label is not None else self.draw_label
        self.cron_reload = cron_reload if cron_reload is not None else self.cron_reload

    def get_obj(self) -> dict:
        """Get a dict of the attributes for this instance.

        Returns:
            dict: instance relevant features
        """
        return {
            "title": self.title,
            "type_service": self.type_service,
            "max_descriptor_distance": self.max_descriptor_distance,
            "min_date_knowledge": self.min_date_knowledge,
            "min_frequency": self.min_frequency,
            "features": self.features,
            "type_system": self.type_system,
            "resize_factor": self.resize_factor,
            "id": self.id,
        }

    async def start(self) -> None:
        
        await self.__preload()

        func.async_scheduler(job = self.__preload, trigger = self.cron_reload)
        
        images_receiver: Callable = self.receiver.start()

        while True:

            ret, img = next(images_receiver)

            if ret:
                try:
                    img_processed = await self.process_unknows(
                        img = img,
                        draw_label = self.draw_label
                        )
                    await self.put_image(img_processed)
                except Exception as error:
                    logging.error(f"Error processing image {error}")
                    await self.put_image(img)


    async def process_less_similar(self, image: np.ndarray, draw_label: bool, name: str, location: Any, encoding: np.ndarray, features: list) -> np.ndarray:
        #WARNING: programmer don't do this is a bad practice

        (top, right, bottom, left) = location

        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 1)

        if draw_label is True:
            cv2.rectangle(image, (left, bottom), (right, bottom + 20), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 10, bottom + 18), font, 0.8, (255, 255, 255), 1)
        
        new_author = str(uuid.uuid4())

        try:
            await self.set_detection({
                "system_id": self.id,
                "detection": encoding.tolist(),
                "features": features,
                "author": new_author,
                "init_date": datetime.now(),
                "last_date": datetime.now(),
                "knowledge": False,
                "frequency": 0,
            })

            self.detector.authors.append(new_author)
            self.detector.encodings.append(encoding.tolist())

        except Exception as error:
            logging.error(f"Error to insert a new user, {error}")

        return image

    async def process_more_similar(self, image: np.ndarray, draw_label: bool, name: str, location: Any, author: str) -> np.ndarray:
        
        (top, right, bottom, left) = location

        cv2.rectangle(image, (left, top), (right, bottom), (0, 128, 0), 1)

        if draw_label is True:
            cv2.rectangle(image, (left, bottom), (right, bottom + 20), (0, 128, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 10, bottom + 18), font, 0.8, (255, 255, 255), 1)

        user = await func.find_user({
                "author": author
            }, db = self.db_users)

        if user is None:
            logging.error(f"Error user not found in BD, author: {author}")

        await self.evaluate_detection(user)

        
        return image

    async def process_unknows(self, img: np.array, draw_label: bool = False) -> 'np.array':
        """Process unknowns users.

        Args:
            img (np.array): img with faces
            draw_label (bool, optional): draw labels over the faces. Defaults to False.

        Returns:
            np.array: img
        """
        face_encodings = await self.detector.get_encodings(img)

        for idx, face_encoding in enumerate(face_encodings):
            face_distances = await self.detector.compare(face_encoding)
            if face_distances.shape[0] > 0:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] > self.detector.min_descriptor_distance:
                    img = await self.process_more_similar(
                        image = img,
                        draw_label = draw_label,
                        name = self.detector.labels[1],
                        location = self.detector.enlarge_dimensions(self.detector.face_locations[idx]),
                        author = self.detector.authors[best_match_index]
                    )
                else:
                    img = await self.process_less_similar(
                        image = img,
                        draw_label = draw_label,
                        name = self.detector.labels[0],
                        location = self.detector.enlarge_dimensions(self.detector.face_locations[idx]),
                        encoding = face_encoding,
                        features = []
                    )
            else:
                img = await self.process_less_similar(
                    image = img,
                    draw_label = draw_label,
                    name = self.detector.labels[0],
                    location = self.detector.enlarge_dimensions(self.detector.face_locations[idx]),
                    encoding = face_encoding,
                    features = []
                    )

        return img

    async def evaluate_detection(self, user: dict) -> dict:
        """Evaluate the user s detection.

        Args:
            user (dict): user to be evaluated

        Returns:
            dict: user modified
        """
        prev_user = user
        diff_date = utils.get_date_diff_so_far(user.init_date, self.min_date_knowledge[1])

        if diff_date > self.min_date_knowledge[0] and user.frequency >= self.min_frequency:
            user.knowledge = True

        elif utils.get_date_diff_so_far(user.last_date, self.min_date_knowledge[1]) > 0:

            prev_days = utils.frequency(total = self.min_date_knowledge[0], percentage = 1, value = self.frequency, invert = True) 
            user.last_date = datetime.now()
            user.frequency = utils.frequency(self.min_date_knowledge[0], 1, prev_days + 1)  

        return await func.update_user({
            **user,
            "modified_on": datetime.now()
        }, self.db_users) if prev_user != user else user

    async def set_detection(self, user: dict) -> None:
        """Set the detection of a user in the database .

        Args:
            user (dict): [description]
        """
        try:    
            await func.insert_user(user, self.db_users)
        except Exception as e:
            logging.error(f"set_detection error to insert detection, {e}")
