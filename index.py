import asyncio
from mvfy.visual import VisualKnowledge
from mvfy.visual.utils import Streamer, Receiver, FaceRecognition
from mvfy.utils import constants as const

if __name__ == "__main__":

    features = [
        const.ALLOWED_FEATURES["AGE"],
        const.ALLOWED_FEATURES["GENDER"]
    ]
    visual = VisualKnowledge(
        type_service = const.TYPE_SERVICE["LOCAL"],
        db_properties = "mongodb://localhost:27017/",
        db_name = "mvfy",
        max_descriptor_distance = 0.7,
        min_date_knowledge = const.DAYS(7),
        type_system=const.TYPE_SYSTEM["OPTIMIZED"],
        features = features,
        title = "mvfy_1"
    )

    visual.set_conf(
        detector=FaceRecognition,
        receiver=Receiver.ip_cam_receiver(ip_cam="https://192.168.1.2:8080"),
        streamer=Streamer.stream_local
    )
    
    asyncio.run(visual.start())



    