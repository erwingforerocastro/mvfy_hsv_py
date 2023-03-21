from flask import Flask, Response
from flask_cors import CORS
import threading

from mvfy.utils import constants as const, index as utils
from mvfy.visual.detector import DetectorFacesCPU
from mvfy.visual.systems import VisualKnowledge
from mvfy.visual.receiver import ReceiverIpCam
from mvfy.visual.streamer import FlaskStreamer

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

receiver = ReceiverIpCam(ip_cam="rtsp://mvfy:mvfy@192.168.1.7:8080/h264_ulaw.sdp")
detector_knows = DetectorFacesCPU(tolerance_comparation= 1 - 0.8)
detector_unknows = DetectorFacesCPU(tolerance_comparation= 1 - 0.8)
streamer = FlaskStreamer()

visual = VisualKnowledge(
    detector_knows=detector_knows,
    detector_unknows=detector_unknows,
    receiver=receiver,
    streamer=streamer,
    type_service=const.TYPE_SERVICE["LOCAL"],
    db_properties="mongodb://localhost:27017/",  # type: ignore
    db_name="mvfy",
    max_descriptor_distance=0.6,
    min_date_knowledge=const.DAYS(7),
    type_system=const.TYPE_SYSTEM["OPTIMIZED"],
    features=[],
    title="mvfy_1",
    draw_label = False,
)

thread_lock = threading.Lock()

def video_generator():
    while True:
        
        thread_lock.acquire()
        img = next(streamer)
        thread_lock.release()

        yield img

@app.route("/")
def index():
    return streamer.get_template()

@app.route("/stream_video")
def stream_video() -> Response:
    # image = streamer.send(
    return Response(video_generator(), mimetype="multipart/x-mixed-replace; boundary=frame")


app.run(host="0.0.0.0", port=8001, debug=False)

