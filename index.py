import asyncio
import threading
from time import time

from flask import Flask, Response, render_template_string

from mvfy.utils import constants as const, index as utils
from mvfy.visual.detector import DetectorUnknows
from mvfy.visual.generator import VisualKnowledge
from mvfy.visual.receiver import ReceiverIpCam
from mvfy.visual.streamer import FlaskStreamer

app = Flask(__name__)

receiver = ReceiverIpCam(ip_cam="rtsp://mvfy:mvfy@192.168.1.4:8080/h264_ulaw.sdp")
detector = DetectorUnknows()
streamer = FlaskStreamer()

visual = VisualKnowledge(
    detector=detector,
    receiver=receiver,
    streamer=streamer,
    type_service=const.TYPE_SERVICE["LOCAL"],
    db_properties="mongodb://localhost:27017/",  # type: ignore
    db_name="mvfy",
    max_descriptor_distance=0.7,
    min_date_knowledge=const.DAYS(7),
    type_system=const.TYPE_SYSTEM["OPTIMIZED"],
    features=[],
    title="mvfy_1",
)


@app.route("/")
def index():
    return streamer.get_template()


@app.route("/stream_video")
def stream_video() -> Response:
    return Response(visual, mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
