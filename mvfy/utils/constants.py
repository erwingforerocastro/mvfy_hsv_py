import os
from typing import Dict, Tuple
from .feature_flags import ENVIROMENT

BASE_PROJECT = os.path.abspath(
    os.path.join(__file__, "../../..")
) if ENVIROMENT == "DEV" else os.getcwd()

UNKNOWS_URL = os.path.join(BASE_PROJECT, 'unknows_url')
ACQUAINTANCES_URL = os.path.join(BASE_PROJECT, 'acquaintances_url')
MODELS_URL = os.path.join(BASE_PROJECT, 'src/mvfy/models')
CONFIG_URL = os.path.join(BASE_PROJECT, 'config')
PORT = 3000 if (v:=os.getenv("PORT")) is None else v

#static
COLLECTIONS: Dict[str, str] = {
    "USERS": "users",
    "SYSTEMS": "systems"
}

#system
ALLOWED_FEATURES: Dict[str, str] = {
    "AGE": "age",
    "GENDER": "gender",
    "RACE": "race",
    "EMOTION": "emotion"
}
TYPE_SYSTEM: Dict[str, str] = {
    "OPTIMIZED": "optimized",
    "PRECISE": "precise"
}
TYPE_SERVICE: Dict[str, str] = {
    "REMOTE": "remote",
    "LOCAL": "local"
}
ACTION: Dict[str, str] = {
    "INIT_SYSTEM": "INIT_SYSTEM",
    "SET_DETECTION": "SET_DETECTION",
}
REQUEST: Dict[str, str] = {
    "ERROR": "ERROR",
    "GET_MODEL_FEATURES": "GET_MODEL_FEATURES",
    "GET_INITIALIZED_SYSTEM": "GET_INITIALIZED_SYSTEM",
    "SEND_DETECTION_VALIDATED": "SEND_DETECTION_VALIDATED",
    "LOCAL_IMAGE_SEND": "LOCAL_IMAGE_SEND"
}

HTML_STREAMER: Dict[str, str] = {
    "URL": os.path.join(BASE_PROJECT, '/public/streamer.html'),
    "URL_TEMP": os.path.join(BASE_PROJECT, '/public/temp/_streamer.html'),
    "PROTOCOL_REPLACE": '<<<PROTOCOL>>>',
    "HOST_REPLACE": '<<<HOST>>>',
    "EMIT_REPLACE": '<<<EMIT>>>',
}

# time
DATE_FORMAT: str = "DD/MM/YYYY"

        
def DAYS (quantity: int) -> Tuple[int, str]:
    quantity = int(quantity)
    if isinstance(quantity, int):
        return (quantity, "days")
    else:
        raise ValueError("type of the quantity days is invalid")
    

def WEEKS (quantity: int) -> Tuple[int, str]:
    quantity = int(quantity)
    if isinstance(quantity, int):
        return (quantity, "weeks")
    else:
        raise ValueError("type of the quantity weeks is invalid")
    
def MONTHS  (quantity: int) -> Tuple[int, str]:
    quantity = int(quantity)
    if isinstance(quantity, int):
        return (quantity, "months")
    else: 
        raise ValueError("type of the quantity months is invalid")
    