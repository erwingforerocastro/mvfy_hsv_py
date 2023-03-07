import asyncio
from queue import Queue
import threading
import time

from flask import Flask, Response, render_template_string

from mvfy.utils import constants as const, index as utils
from mvfy.visual.detector.detectors import Detector, DetectorFaces
from mvfy.visual.generator import VisualKnowledge
from mvfy.visual.receiver import ReceiverIpCam
from mvfy.visual.streamer import FlaskStreamer
from iterators import TimeoutIterator

app = Flask(__name__)

receiver = ReceiverIpCam(ip_cam="rtsp://mvfy:mvfy@192.168.1.19:8080/h264_ulaw.sdp")
detector_knows = DetectorFaces(tolerance_comparation= 1 - 0.7)
detector_unknows = DetectorFaces(tolerance_comparation= 1 - 0.7)
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


@app.route("/")
def index():
    return streamer.get_template()

@app.route("/stream_video")
def stream_video() -> Response:
    return Response(streamer, mimetype="multipart/x-mixed-replace; boundary=frame")

import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()

app.run(host="0.0.0.0", port=8001, debug=False)
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumtime')
stats.print_stats()
