from utils import constants as const, index as utils
from utils.detectors import Detector
from utils.streamer import Streamer
from datetime import datetime
import math
import asyncio

class VisualKnowledge:

    def __init__(self,
    type_service: 'str',
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
            {Any|Number} port - Server listen port.
            {String} type_service - type of the listen server.
            {Array} min_date_knowledge [min_date_knowledge=null] - minimum interval to determine a known user.
            {Number} min_frequency [min_frequency=0.7] - minimum frequency between days detectioned.
            {String} features [features=null] - characteristics that will be saved in each detection.
            {String} decoder [decoder='utf-8'] - data decoder.
            {String} max_descriptor_distance [max_descriptor_distance=null] - max distance of diference between detections.
            {String} type_system [type_system=null] - type of system.
            {String} title [title=null] - title of system.

        :Returns:
            None.

        """

        self.id = None
        self.type_service = type_service
        self.title = math.floor(datetime.now() / 1000) if title is None else title
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

        self.type_model_detection = None
        self.display_size = { "width": 300, "height": 300 }
        self.matches = None
        self.interval_streaming = None
        self.execution = False

    def __insert(self, system: 'dict'):
        obj_self =  {}
        for key, item in system.items():
            self[key] = item if item is not None else self[key]
        
    def set_conf(self, 
    receiver: 'function',
    detector: 'Detector',
    streamer: 'Streamer',
    stream_fps: float = 30, 
    ) -> None:
       self.receiver = receiver
       self.detector = detector
       self.streamer = streamer
       self.stream_fps = stream_fps

    async def start(self) -> None:
        
        while True:
            img = self.receiver()
