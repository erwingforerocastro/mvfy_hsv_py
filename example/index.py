from mvfy.visual import VisualKnowledge
from mvfy.visual.utils import Streamer, Receiver, FaceRecognition

if __file__ == "__main__":

    visual = VisualKnowledge(
        
    )

    visual.set_conf(
        detector=FaceRecognition,
        receiver=Receiver.ip_cam_capture(ip_cam=""),
        streamer=Streamer
    )



    