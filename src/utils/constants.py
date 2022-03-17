import 
const BASE_PROJECT = path.resolve(__dirname, '../..')
const UNKNOWS_URL = path.join(BASE_PROJECT, '/unknows_url')
const ACQUAINTANCES_URL = path.join(BASE_PROJECT, '/acquaintances_url')
const MODELS_URL = path.join(BASE_PROJECT, '/src/mvfy/models')
const CONFIG_URL = path.join(BASE_PROJECT, '/config')
const PORT = process.env.PORT || 3000;

//static
HTML_STREAMER = {
    "URL": path.join(BASE_PROJECT, '/public/streamer.html'),
    "URL_TEMP": path.join(BASE_PROJECT, '/public/temp/_streamer.html'),
    "PROTOCOL_REPLACE": '<<<PROTOCOL>>>',
    "HOST_REPLACE": '<<<HOST>>>',
    "EMIT_REPLACE": '<<<EMIT>>>',
}

//system
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

def DAYS (quantity):
    quantity = Number(quantity)
    if (typeof(quantity) == 'number') {
        return Array(quantity, "days")
    } else {
        throw new TypeError("type of the quantity days is invalid")
    }

def WEEKS (quantity) :
    quantity = int(quantity)
    if (typeof(quantity) == 'number') {
        return Array(quantity, "weeks")
    } else {
        throw new TypeError("type of the quantity weeks is invalid")
    }
}

def MONTHS  (quantity) :
    quantity = int(quantity)
    if (typeof(quantity) == 'number') {
        return Array(quantity, "months")
    } else {
        throw new TypeError("type of the quantity months is invalid")
    }
}