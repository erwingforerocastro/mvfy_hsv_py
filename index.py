import asyncio
import threading

from flask import Flask, render_template

from mvfy.utils import constants as const
from mvfy.visual import VisualKnowledge
from mvfy.visual.utils import FlaskStreamer, Receiver, DetectorUnknows

app = Flask(__name__)

features = [
    const.ALLOWED_FEATURES["AGE"],
    const.ALLOWED_FEATURES["GENDER"]
]
visual = VisualKnowledge(
    receiver= Receiver.ip_cam_receiver(
    ip_cam = "rtsp://mvfysystem:mvfysystem@192.168.1.11:8080/h264_ulaw.sdp"),
    detector = DetectorUnknows,
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
    return render_template(streamer.url_template)

@app.route("/stream")
async def stream():
    return await streamer.get_frame()

if __name__ == "__main__":
    
    asyncio.run(streamer)
    app.run(host='0.0.0.0', port = 8001, debug=True)