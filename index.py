import asyncio
import threading

from flask import Flask, render_template, render_template_string

from mvfy.utils import constants as const
from mvfy.visual.detector import DetectorUnknows
from mvfy.visual.generator import VisualKnowledge
from mvfy.visual.receiver import ReceiverIpCam
from mvfy.visual.streamer import FlaskStreamer

app = Flask(__name__)

features = [
    const.ALLOWED_FEATURES["AGE"],
    const.ALLOWED_FEATURES["GENDER"]
]

receiver = ReceiverIpCam(
    ip_cam = "rtsp://mvfysystem:mvfysystem@192.168.1.11:8080/h264_ulaw.sdp"
)

detector = DetectorUnknows()

visual = VisualKnowledge(
    receiver = receiver,
    detector = detector,
    type_service = const.TYPE_SERVICE["LOCAL"],
    db_properties="mongodb://localhost:27017/",
    db_name="mvfy",
    max_descriptor_distance=0.7,
    min_date_knowledge=const.DAYS(7),
    type_system = const.TYPE_SYSTEM["OPTIMIZED"],
    features=features,
    title="mvfy_1"
)

visual.set_conf(
    display_size = (720, 480)
)

streamer = FlaskStreamer(image_generator = visual)

@app.route("/")
def index():
    threading.Thread(target = streamer.start).start()
    return render_template_string(streamer.get_template(), title = "mvfy_visual")

@app.route("/stream_video")
def stream_video():
    return streamer.get_frame()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8001, debug=True)
