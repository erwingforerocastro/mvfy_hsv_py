import os
from feature_flags import ENVIROMENT

BASE_PROJECT = os.path.abspath(
    os.path.join(__file__, "../../..")
) if ENVIROMENT == "DEV" else os.getcwd()

UNKNOWS_URL = os.path.join(BASE_PROJECT, '/unknows_url')
ACQUAINTANCES_URL = os.path.join(BASE_PROJECT, '/acquaintances_url')
MODELS_URL = os.path.join(BASE_PROJECT, '/src/mvfy/models')
CONFIG_URL = os.path.join(BASE_PROJECT, '/config')
PORT = 3000 if (v:=os.getenv("PORT")) is None else v

#static
HTML_STREAMER = {
    "URL": os.path.join(BASE_PROJECT, '/public/streamer.html'),
    "URL_TEMP": os.path.join(BASE_PROJECT, '/public/temp/_streamer.html'),
    "PROTOCOL_REPLACE": '<<<PROTOCOL>>>',
    "HOST_REPLACE": '<<<HOST>>>',
    "EMIT_REPLACE": '<<<EMIT>>>',
}

#system
ALLOWED_FEATURES = {
    "ALL": "all",
    "AGE_AND_GENDER": "ageandgender",
    "EXPRESSIONS": "expressions",
}
TYPE_SYSTEM = {
    "OPTIMIZED": "optimized",
    "PRECISE": "precise"
}
TYPE_SERVICE = {
    "REMOTE": "remote",
    "LOCAL": "local"
}
ACTION = {
    "INIT_SYSTEM": "INIT_SYSTEM",
    "SET_DETECTION": "SET_DETECTION",
}
REQUEST = {
    "ERROR": "ERROR",
    "GET_MODEL_FEATURES": "GET_MODEL_FEATURES",
    "GET_INITIALIZED_SYSTEM": "GET_INITIALIZED_SYSTEM",
    "SEND_DETECTION_VALIDATED": "SEND_DETECTION_VALIDATED",
    "LOCAL_IMAGE_SEND": "LOCAL_IMAGE_SEND"
}

# time
DATE_FORMAT = "DD/MM/YYYY"

def DAYS (quantity: int):
    quantity = int(quantity)
    if isinstance(quantity, (int, float)):
        return (quantity, "days")
    else:
        raise ValueError("type of the quantity days is invalid")
    

def WEEKS (quantity: int) :
    quantity = int(quantity)
    if isinstance(quantity, (int, float)):
        return (quantity, "weeks")
    else:
        raise ValueError("type of the quantity weeks is invalid")
    
def MONTHS  (quantity: int) :
    quantity = int(quantity)
    if isinstance(quantity, (int, float)):
        return (quantity, "months")
    else: 
        raise ValueError("type of the quantity months is invalid")
    