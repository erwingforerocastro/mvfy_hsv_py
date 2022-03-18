from utils import constants as const, index as utils
from datetime import datetime
import math

class MvFyVisual:

    def __init__(self, *args, **kargs) -> None:
        """
        Main model builder

        constructor
            param {Object} args
            param {*} args.server - Backend server for the websocket. 
            param {Object} args.options - options for the websocket.
            param {Any|Number} args.port - Server listen port.
            param {String} args.type_service - type of the listen server.
            param {Array} args.min_date_knowledge [min_date_knowledge=null] - minimum interval to determine a known user.
            param {Number} args.min_frequency [min_frequency=0.7] - minimum frequency between days detectioned.
            param {String} args.features [features=null] - characteristics that will be saved in each detection.
            param {String} args.decoder [decoder='utf-8'] - data decoder.
            param {String} args.max_descriptor_distance [max_descriptor_distance=null] - max distance of diference between detections.
            param {String} args.type_system [type_system=null] - type of system.
            param {String} args.title [title=null] - title of system.
        /
        """
        server, options, *otherInfo = kargs
        #create or return system of bd
        
        self.type_service = kargs["type_service"] #*required
        self.port = kargs["port"]
        self.domain = "localhost"
        self.title = math.floor(datetime.now() / 1000)
        self.id = None
        self.features = None
        self.min_date_knowledge = None
        self.min_frequency = 0.7
        self.decoder = 'utf-8'
        self.max_descriptor_distance = None
        self.type_system = None
        self.execution = False
        self.type_model_detection = None
        self.display_size = { "width": 300, "height": 300 }
        self.matches = None
        self.stream_video = None
        self.interval_streaming = None
        self.stream_fps = 30
        self.__insert(otherInfo)

        if server is None or options is None:
            raise ValueError("server and options argument is required")

        io = SocketIO(server, options)

    def __insert(self, system: 'dict'):
        obj_self =  {}
        for key, item in system.items():
            self[key] = item if item is not None else self[key]
        

    