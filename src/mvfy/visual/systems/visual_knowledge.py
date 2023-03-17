import asyncio
import logging
import threading
import time
import uuid
from asyncio import Queue
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable, List, Optional, Tuple
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
from mvfy.visual.systems.image_generator import ImageGenerator
from mvfy.visual.receiver.receivers import Receiver
from mvfy.visual.streamer import Streamer

from . import errors


@dataclass
class VisualKnowledge():

    detector_knows: Optional[Detector] = None
    detector_unknows: Optional[Detector] = None
    receiver: Optional[Receiver] = None
    streamer: Optional[Streamer] = None
    type_service: Optional[str] = None
    db_properties: Optional[dict] = None
    db_name: Optional[str] = None
    max_descriptor_distance: Optional[float] = None
    min_date_knowledge: Optional[float] = None
    min_frequency: Optional[float] = 0.7
    resize_factor: Optional[float] = 0.25
    features: Optional[list] = Field(default_factory=list)
    type_system: Optional[str] = const.TYPE_SYSTEM["OPTIMIZED"]
    title: Optional[str] = str(uuid.uuid4())
    delay: int = 30
    batch_images: int = 30
    draw_label: bool = False
    date_format: str = const.DATE_FORMAT
    cron_reload: Optional[CronTrigger] = None

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

        # properties
        self.id = None

        # more info
        if self.cron_reload is None:
            self.cron_reload = self.__get_cron_trigger()

        # DB
        self.db_systems = SystemDB(
            properties=self.db_properties, db=self.db_name, collection=const.COLLECTIONS["SYSTEMS"]
        )
        self.db_users = UserDB(
            properties=self.db_properties, db=self.db_name, collection=const.COLLECTIONS["USERS"]
        )

        self.new_users: Queue = Queue()
        self.evaluate_users: Queue = Queue()

        self._thread_receiver = utils.run_async_in_thread(self.receiver.start())
        self._thread_system = utils.run_async_in_thread(self.start())
        self._thread_insert_new_users = utils.run_async_in_thread(self.add_new_users())
        self._thread_evaluate_users = utils.run_async_in_thread(self.evaluate_detections())


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

        # insert system found in instance
        self.__insert_system(system)
        logging.info("system created")

        # get descriptors
        await self.insert_known_users()
        await self.insert_unknown_users()
        logging.info("face of users inserted")

    def __get_cron_trigger(self) -> CronTrigger:
        """get crontrigger of now every day

        Returns:
            CronTrigger: trigger of action
        """
        _date = datetime.now(tz=get_localzone())
        return CronTrigger(
            hour=_date.hour, minute=_date.minute, second=_date.second, timezone=get_localzone()
        )

    def __insert_system(self, system: dict) -> None:
        """Insert system inside actual instance

        Args:
            system (dict): values to be replaced in instance
        """
        self.id = system["id"]
        self.type_service = (
            system["type_service"] if system["type_service"] is not None else self.type_service
        )
        self.title = system["title"] if system["title"] is not None else self.title
        self.features = system["features"] if system["features"] is not None else self.features
        self.min_date_knowledge = (
            system["min_date_knowledge"]
            if system["min_date_knowledge"] is not None
            else self.min_date_knowledge
        )
        self.min_frequency = (
            system["min_frequency"] if system["min_frequency"] is not None else self.min_frequency
        )
        self.max_descriptor_distance = (
            system["max_descriptor_distance"]
            if system["max_descriptor_distance"] is not None
            else self.max_descriptor_distance
        )
        self.type_system = (
            system["type_system"] if system["type_system"] is not None else self.type_system
        )
        self.resize_factor = (
            system["resize_factor"] if system["resize_factor"] is not None else self.resize_factor
        )

    async def insert_known_users(self):

        try:
            users = await func.get_users(
                {"system_id": self.id, "knowledge": True}, db=self.db_users
            )

            if users is not None:
                authors, encodings = zip(*[[user.author, user.detection] for user in users])
                self.detector_knows.authors = np.array(authors)
                self.detector_knows.encodings = np.array(encodings)

        except Exception as error:
            logging.error(f"Failed to insert faces of known users, {error}")
        
    async def insert_unknown_users(self):

        try:

            users = await func.get_users(
                {"system_id": self.id, "knowledge": False}, db=self.db_users
            )

            if users is not None:
                authors, encodings = zip(*[[user.author, user.detection] for user in users])
                self.detector_unknows.authors = np.array(authors)
                self.detector_unknows.encodings = np.array(encodings)

        except Exception as error:
            logging.error(f"Failed to insert faces of unknown users, {error}")

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

        func.async_scheduler(job=self.__preload, trigger=self.cron_reload)
        
        print("Start - detection of users")

        if self.batch_images % 2 != 0:
                raise ValueError(f"invalid batch image size, {self.batch_images}")
        
        while True:
            
            images_batch = [self.receiver.get() for _ in range(self.batch_images)]

            try:
                images_to_process = images_batch[1::2]
                images_raw = images_batch[0::2]

                faces = await asyncio.gather(*[self.detector_unknows.get_encodings(img) for img in images_to_process], return_exceptions=True)
                batch_processed = await asyncio.gather(*[self.detect_type_user(img, face_prop) for img, face_prop in zip(images_to_process, faces)], return_exceptions=True)

                all_images = []

                for pair_images in zip(images_raw, batch_processed):
                    all_images.extend(pair_images)

                await self.streamer.save(all_images)

            except Exception as error:
                logging.error(f"Error processing image {error}")
                await self.streamer.save(images_batch)

    async def evaluate_detections(self) -> None:
        while True:
            try:
                if not self.evaluate_users.empty():
                    author = await self.evaluate_users.get()
                    user_evaludated = await self.evaluate_detection(author)
                    
                    if user_evaludated.knowledge is True:
                        self.detector_knows.authors = np.append(self.detector_knows.authors, [user_evaludated.author], axis=0)
                        self.detector_knows.encodings = np.append(self.detector_knows.encodings, np.array(user_evaludated.detection).reshape(1, -1), axis=0)

            except Exception as error:
                logging.error(f"error evaluating user, {error}")

    async def add_new_users(self) -> None:

        while True:
            try:
                if not self.new_users.empty():
                    new_user = await self.new_users.get()
                    await func.insert_user(new_user, self.db_users)

                    self.detector_unknows.authors = np.append(self.detector_unknows.authors, [new_user['author']], axis=0)
                    self.detector_unknows.encodings = np.append(self.detector_unknows.encodings, np.array(new_user['detection']).reshape(1, -1), axis=0)

            except Exception as error:
                logging.error(f"error inserting new user, {error}")

    async def save_new_unknown(self, encoding: np.ndarray, features: list) -> None:

        new_author = str(uuid.uuid4())

        try:
            await self.new_users.put(
                {
                    "system_id": self.id,
                    "detection": encoding.tolist(),
                    "features": features,
                    "author": new_author,
                    "init_date": datetime.now(),
                    "last_date": datetime.now(),
                    "knowledge": False,
                    "frequency": 0,
                }
            )

        except Exception as error:
            logging.error(f"Error to insert a new user, {error}")

    async def save_evaluate_detection(self, author: str) -> None:

        try:
            await self.evaluate_users.put(author)
        except Exception as error:
            logging.error(f"Error to insert author for evaluate, {error}")

    @func.loop_manager
    async def draw_frame(
        self,
        image: np.ndarray,
        draw_label: bool,
        name: str,
        location: Any,
        color: Tuple[int, int, int],
        loop: 'asyncio.AbstractEventLoop',
    ) -> np.ndarray:
        # WARNING: programmer don't do this is a bad practice

        (top, right, bottom, left) = location

        await loop.run_in_executor(None, lambda: cv2.rectangle(image, (left, top), (right, bottom), color, 1))

        if draw_label is True:
            cv2.rectangle(image, (left, bottom), (right, bottom + 20), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 10, bottom + 18), font, 0.8, (255, 255, 255), 1)

        return image

    async def detect_type_user(self, img: np.array, face_properties: Tuple[list, list]) -> "np.array":
        """Compare faces in image and detect knows and unkowns.

        Args:
            img (np.array): img with faces

        Returns:
            np.array: img
        """

        for face_location, face_encoding in zip(*face_properties):
            
            # location = self.detector_unknows.enlarge_dimensions(self.detector_unknows.face_locations[idx])
            known_comparations, unknown_comparations = await asyncio.gather(
                self.detector_knows.compare(face_encoding), 
                self.detector_unknows.compare(face_encoding),
                return_exceptions=True)

            if np.any(known_comparations):
                
                img = await self.draw_frame(
                    image = img,
                    draw_label = self.draw_label,
                    name = "conocido",
                    location = face_location,
                    color=(0, 128, 0),
                )

                continue

            if np.any(unknown_comparations):
                previous_authors = self.detector_unknows.authors[:len(unknown_comparations)] 
                await self.save_evaluate_detection(str(previous_authors[unknown_comparations][0]))
            else:
                await self.save_new_unknown(encoding=face_encoding, features=[])

            img = await self.draw_frame(
                    image = img,
                    draw_label = self.draw_label,
                    name = "desconocido",
                    location = face_location,
                    color=(0, 0, 255),
                )
        
        return img

    async def evaluate_detection(self, author: str) -> dict:
        """Evaluate the user s detection.

        Args:
            author (dict): author to be evaluated

        Returns:
            dict: user modified
        """
        user = await func.find_user({"author": author}, db=self.db_users)

        if user is None:
            logging.error(f"Error user not found in BD, author: {author}")
            return {}

        prev_user = user
        diff_date = utils.get_date_diff_so_far(user.init_date, self.min_date_knowledge[1])

        if diff_date > self.min_date_knowledge[0] and user.frequency >= self.min_frequency:
            
            user.knowledge = True

        elif utils.get_date_diff_so_far(user.last_date, self.min_date_knowledge[1]) > 0:

            prev_days = utils.frequency(
                total=self.min_date_knowledge[0], 
                percentage=1, 
                value=self.frequency, invert=True
            )
            user.last_date = datetime.now()
            user.frequency = utils.frequency(
                total = self.min_date_knowledge[0], 
                percentage = 1, 
                value = prev_days + 1)

        return (
            await func.update_user({**user, "modified_on": datetime.now()}, self.db_users)
            if prev_user != user
            else user
        )
