from flask import Flask, Response
from flask_cors import CORS

from src.mvfy.utils import constants as const, index as utils
from src.mvfy.visual.detector.detectors import DetectorFacesCPU
from src.mvfy.visual.systems import VisualKnowledge
from src.mvfy.visual.receiver import ReceiverIpCam
from src.mvfy.visual.streamer import FlaskStreamer

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

receiver = ReceiverIpCam(ip_cam="rtsp://mvfy:mvfy@192.168.1.6:8080/h264_ulaw.sdp")
detector_knows = DetectorFacesCPU(tolerance_comparation= 1 - 0.7)
detector_unknows = DetectorFacesCPU(tolerance_comparation= 1 - 0.7)
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
    # image = streamer.send()
    return Response(streamer, mimetype="multipart/x-mixed-replace; boundary=frame")


app.run(host="0.0.0.0", port=8001, debug=False)

