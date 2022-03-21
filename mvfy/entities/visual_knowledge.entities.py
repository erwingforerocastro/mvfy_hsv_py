from datetime import datetime
from utils.constants import TYPE_SERVICE, TYPE_SYSTEM
import numpy as np
import hashlib

class MetaUser(type):

    def __new__(cls, name, bases, dct):
        MetaUser.validate_instance(dct)
        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def validate_instance(dct: 'object'):
        if not isinstance(dct["decoder"], (str)):
            raise ValueError(
                f"Invalid decoder: {dct['decoder']}, must be a string")

        if not isinstance(dct["system_id"], (str)):
            raise ValueError(
                f"Invalid system_id: {dct['system_id']}, must be a string")

        if not isinstance(dct["author"], (str)):
            raise ValueError(
                f"Invalid author: {dct['author']}, must be a string")

        if not type(dct["detection"]) == type(np.float64):
            raise ValueError(
                f"Invalid detection: {dct['detection']}, must be a np.float64")

        if not type(dct["init_date"]) is datetime.datetime:
            raise ValueError(
                f"Invalid init_date: {dct['init_date']}, must be a datetime")

        if not type(dct["last_date"]) is datetime.datetime:
            raise ValueError(
                f"Invalid last_date: {dct['last_date']}, must be a datetime")

        if not isinstance(dct["properties"], (dict, object)) and dct["properties"] is not None:
            raise ValueError(
                f"Invalid properties: {dct['properties']}, must be a dictionary")

        if not isinstance(dct["knowledge"], (bool)) and dct["knowledge"] is not None:
            raise ValueError(
                f"Invalid knowledge: {dct['knowledge']}, must be a dictionary")

        if not isinstance(dct["frequency"], (np.number, int, float)) or dct["frequency"] <= 0 or dct["frequency"] > 1 or dct["frequency"] is not None:
            raise ValueError(
                f"Invalid frequency: {dct['frequency']}, must be a number, between o and 1")

        if type(dct["created_on"]) is not datetime.datetime and dct["created_on"] is not None:
            raise ValueError(
                f"Invalid created_on: {dct['created_on']}, must be a datetime")

        if type(dct["modified_on"]) is not datetime.datetime and dct["modified_on"] is not None:
            raise ValueError(
                f"Invalid modified_on: {dct['modified_on']}, must be a datetime")


class MetaSystem(type):

    def __new__(cls, name, bases, dct):
        MetaSystem.validate_instance(dct)
        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def validate_instance(dct: 'dict'):

        if not isinstance(dct["type_service"], (str)) or dct["type_service"] not in TYPE_SERVICE.values():
            raise ValueError(f"Invalid type_service: {dct['type_service']}")

        if not isinstance(dct["max_descriptor_distance"], (float)) or dct["max_descriptor_distance"] <= 0 or dct["max_descriptor_distance"] > 1:
            raise ValueError(
                f"Invalid max_descriptor_distance: {dct['max_descriptor_distance']}")

        if not isinstance(dct["min_date_knowledge"], (list)):
            raise ValueError(
                f"Invalid min_date_knowledge: {dct['min_date_knowledge']}")

        if not isinstance(dct["min_frequency"], (float)):
            raise ValueError(
                f"Invalid min_frequency: {dct['min_frequency']}, must be a float")

        if not isinstance(dct["features"], (dict)):
            raise ValueError(
                f"Invalid features: {dct['features']}, must be a dictionary")

        if not isinstance(dct["type_system"], (str)) or dct["type_system"] not in TYPE_SYSTEM.values():
            raise ValueError(
                f"Invalid type_system: {dct['type_system']}, must be a string")

        if not isinstance(dct["id"], (str)):
            raise ValueError(f"Invalid id: {dct['id']}, must be a string")

        if not isinstance(dct["title"], (str)):
            raise ValueError(
                f"Invalid title: {dct['title']}, must be a string")

        if type(dct["created_on"]) is not datetime.datetime and dct["created_on"] is not None:
            raise ValueError(
                f"Invalid created_on: {dct['created_on']}, must be a datetime")

        if type(dct["modified_on"]) is not datetime.datetime and dct["modified_on"] is not None:
            raise ValueError(
                f"Invalid modified_on: {dct['modified_on']}, must be a datetime")


class User(metaclass=MetaUser):
    """Entity User

    Args:
        metaclass (class, optional): Meta class of user. Defaults to MetaUser.
    """

    def __init__(self,
                 id: str,
                 system_id: str,
                 author: str,
                 detection: 'np.float64',
                 init_date: datetime,
                 last_date: datetime,
                 properties: dict = {},
                 knowledge: bool = False,
                 frequency: int = 1,
                 created_on: datetime = datetime.now(),
                 modified_on: datetime = datetime.now(),
                 ) -> None:

        self.detection = detection
        self.properties = properties
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
            "properties": self.properties,
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
                 features: dict,
                 type_system: str,
                 id: str,
                 title: str,
                 created_on: datetime = datetime.now(),
                 modified_on: datetime = datetime.now(),
                 ) -> None:

        self.type_service = type_service
        self.max_descriptor_distance = max_descriptor_distance
        self.min_date_knowledge = min_date_knowledge
        self.min_frequency = min_frequency
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
            "features": self. features,
            "type_system": self. type_system,
            "id": self. id,
            "title": self. title,
            "hash": self.get_hash(),
            "created_on": self. created_on,
            "modified_on": self. modified_on,
        }

    def get_hash(self) -> str:
        str2hash = f"{self.title}{self.type_system}"
        return hashlib.md5(str2hash.encode()).hexdigest()