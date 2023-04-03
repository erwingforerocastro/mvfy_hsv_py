from datetime import datetime
from typing import Optional
from mvfy.utils.constants import TYPE_SERVICE, TYPE_SYSTEM
import numpy as np
import hashlib

class MetaUser(type):

    def __call__(self, 
            system_id,
            author,
            detection,
            init_date,
            last_date,
            features,
            knowledge,
            frequency,
            *args,
            **kwds):

        if not isinstance(system_id, (str)):
            raise ValueError(
                f"Invalid system_id: {system_id}, must be a string")

        if not isinstance(author, (str)):
            raise ValueError(
                f"Invalid author: {author}, must be a string")

        if not isinstance(detection, list):
            raise ValueError(
                f"Invalid detection: {detection}, must be a np.float64")

        if not type(init_date) is datetime:
            raise ValueError(
                f"Invalid init_date: {init_date}, must be a datetime")

        if not type(last_date) is datetime:
            raise ValueError(
                f"Invalid last_date: {last_date}, must be a datetime")

        if not isinstance(features, (dict, object)) and features is not None:
            raise ValueError(
                f"Invalid features: {features}, must be a dictionary")

        if not isinstance(knowledge, (bool)) and knowledge is not None:
            raise ValueError(
                f"Invalid knowledge: {knowledge}, must be a dictionary")

        if not isinstance(frequency, (np.number, int, float)) or frequency < 0 or frequency > 1 or frequency is None:
            raise ValueError(
                f"Invalid frequency: {frequency}, must be a number, between 0 and 1")

        return super().__call__(
            system_id,
            author,
            detection,
            init_date,
            last_date,
            features,
            knowledge,
            frequency,
            *args,
            **kwds)


class MetaSystem(type):

    def __call__(self, 
            type_service,
            max_descriptor_distance,
            min_date_knowledge,
            min_frequency,
            resize_factor,
            features,
            type_system,
            title,
            id,
            *args,
            **kwds):

        if not isinstance(type_service, (str)) or type_service not in TYPE_SERVICE.values():
            raise ValueError(f"Invalid type_service: {type_service}")

        if not isinstance(max_descriptor_distance, (float)) or max_descriptor_distance <= 0 or max_descriptor_distance > 1:
            raise ValueError(
                f"Invalid max_descriptor_distance: {max_descriptor_distance}")

        if not isinstance(min_date_knowledge, (list, tuple)):
            raise ValueError(
                f"Invalid min_date_knowledge: {min_date_knowledge}")

        if not isinstance(min_frequency, (float)):
            raise ValueError(
                f"Invalid min_frequency: {min_frequency}, must be a float")

        if not isinstance(resize_factor, (float)):
            raise ValueError(
                f"Invalid resize_factor: {resize_factor}, must be a float")

        if not isinstance(features, (list)):
            raise ValueError(
                f"Invalid features: {features}, must be a list")

        if not isinstance(type_system, (str)) or type_system not in TYPE_SYSTEM.values():
            raise ValueError(
                f"Invalid type_system: {type_system}, must be a string or valid TYPE SYSTEM see insert link")

        if not isinstance(title, (str)):
            raise ValueError(
                f"Invalid title: {title}, must be a string")

        return super().__call__(type_service,
                 max_descriptor_distance,
                 min_date_knowledge,
                 min_frequency,
                 resize_factor,
                 features,
                 type_system,
                 title,
                 id)
        

class User(metaclass=MetaUser):
    """Entity User

    Args:
        metaclass (class, optional): Meta class of user. Defaults to MetaUser.
    """

    def __init__(self,
                 system_id: str,
                 author: str,
                 detection: list,
                 init_date: datetime,
                 last_date: datetime,
                 features: dict = {},
                 knowledge: bool = False,
                 frequency: int = 0,
                 created_on: datetime = datetime.now(),
                 modified_on: datetime = datetime.now(),
                 id: str = None,
                 ) -> None:

        self.detection = detection
        self.features = features
        self.init_date = init_date
        self.last_date = last_date
        self.knowledge = knowledge
        self.frequency = frequency
        self.author = author
        self.created_on = created_on
        self.modified_on = modified_on
        self.system_id = system_id
        self.id = id

    def get_obj(self) -> dict:
        return {
            "detection": self.detection,
            "features": self.features,
            "init_date": self.init_date,
            "last_date": self.last_date,
            "knowledge": self.knowledge,
            "frequency": self.frequency,
            "author": self.author,
            "created_on": self.created_on,
            "modified_on": self.modified_on,
            "system_id": self.system_id,
            "id": self.id
        }


class System(metaclass=MetaSystem):

    def __init__(self,
                 type_service: str,
                 max_descriptor_distance: float,
                 min_date_knowledge: list,
                 min_frequency: float,
                 resize_factor: float,
                 features: list,
                 type_system: str,
                 title: str,
                 created_on: datetime = datetime.now(),
                 modified_on: datetime = datetime.now(),
                 id: str = None,
                 ) -> None:

        self.type_service = type_service
        self.max_descriptor_distance = max_descriptor_distance
        self.min_date_knowledge = min_date_knowledge
        self.min_frequency = min_frequency
        self.resize_factor = resize_factor
        self.features = features
        self.type_system = type_system
        self.id = id
        self.title = title
        self.created_on = created_on
        self.modified_on = modified_on

    def get_obj(self) -> dict:
        return {
            "type_service": self. type_service,
            "max_descriptor_distance": self. max_descriptor_distance,
            "min_date_knowledge": self. min_date_knowledge,
            "min_frequency": self. min_frequency,
            "resize_factor": self.resize_factor,
            "features": self. features,
            "type_system": self. type_system,
            "id": self. id,
            "title": self. title,
            "hash": self.hash,
            "created_on": self.created_on,
            "modified_on": self.modified_on,
        }
    
    @property
    def hash(self) -> str:
        str2hash = f"{self.title}{self.type_system}"
        return hashlib.md5(str2hash.encode()).hexdigest()