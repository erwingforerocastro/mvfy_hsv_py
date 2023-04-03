# mvfy_visual

**Python face recognition library for detection of unknowns in a closed system**


# Tutorials

* **[basic example](#basic-example-visualknowledge)**


# Features

## Detection of Unknows

![detector-unknows](https://user-images.githubusercontent.com/92807219/194922510-7348e07a-d893-428f-a94f-ea8dc3bc16ed.png)


This process consists of detecting multiple faces, creating the encodings for all of them, over time as users become more frequent, they will be detected as knowns, while users whose detections are infrequent or have not been detected before will be detected as unknown.

* To determine if a user is known, the face identifier will be taken, this would determine the authenticity of the user and in turn said detection will serve to determine the frequency of stay, to determine if one of these users is known, it is calculated as follows:
<br><br>

![knowledge](https://user-images.githubusercontent.com/45082141/225180983-f4b0c7ae-cf3d-49ca-8ec2-d460d2d3e931.png)
<br><br>

* * Kmin -  is a umbral of minimum date to knonwn a user (example: 7 days)
<br><br>

  ![image](https://user-images.githubusercontent.com/45082141/225182436-0b1c0e17-e648-454a-bd6b-94b2f38a73fa.png)
  - typeDate - (days, months, years)
  - nType - number of typedate
  <br><br>

* * Freq -  is a frequency of all previous detections of that user
<br><br>

  ![image](https://user-images.githubusercontent.com/45082141/225183125-94356a68-bb2b-42fb-81be-f2ae5cad0e4f.png)
  - prevDays - are that previous frequencies saved
  <br><br>
* * Fmin -  is a umbral of minimum frequency
* * Δf - is the difference between the current date and the user's initial insertion date.
<br><br>

  ![Δf](https://user-images.githubusercontent.com/45082141/225182114-706b21d5-5c01-4073-beff-fa56e2467b59.png)
  - dateNow - date now
  - dateuser - first detection of that user
  <br><br>


<a name="running-the-examples"></a>

# Running the Examples

Clone the repository, and do the [installation](#installation) before:

``` bash
git clone https://github.com/erwingforerocastro/mvfy_visual
```

## Running the Flask Examples

``` bash
pipenv install
```

``` bash
cd /examples/example-flask
python main.py
```

<a name="installation"></a>

## Installation

### Requirements

  * Python 3.7+
  * Windows (linux not officially supported, but might work)

### Installation Options:

#### Installing on Windows

#### Required for OpenCv

  * For run OpenCv sometimes you need [this](https://perso.uclouvain.be/allan.barrea/opencv/building_tools.html) building tools. 

#### Installing visual studio

  * [Download visual studio](https://visualstudio.microsoft.com/es/c3e9b) (optional).

#### Installing Face Recognition

```bash
  git clone https://github.com/RvTechiNNovate/face_recog_dlib_file.git
  cd face_recog_dlib_file
```
dlib is required for face recognition library
```bash
  Python 3.7:
  pip install dlib-19.19.0-cp37-cp37m-win_amd64.whl

  Python 3.8:
  pip install dlib-19.19.0-cp38-cp38-win_amd64.whl
```

#### Installing on Mac or Linux (Beta)

First, make sure you have dlib already installed with Python bindings:

  * [How to install dlib from source on macOS or Ubuntu](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)
  
Then, make sure you have cmake installed:  
 
```brew install cmake```

Finally, install this module from pypi:

```bash
pip install mvfy_visual
```

Alternatively, you can try this library with [Docker](https://www.docker.com/), see [this section](#deployment).

If you are having trouble with installation, you can also try out a
[pre-configured VM](https://medium.com/@ageitgey/try-deep-learning-in-python-now-with-a-fully-pre-configured-vm-1d97d4c3e9b).

#### Installing on an Nvidia Jetson Nano board

 * [Jetson Nano installation instructions](https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd)
   * Please follow the instructions in the article carefully. There is current a bug in the CUDA libraries on the Jetson Nano that will cause this library to fail silently if you don't follow the instructions in the article to comment out a line in dlib and recompile it.


# Getting Started

<a name="getting-started-loading-models"></a>

## Detection of unknowns 

### Receiver

The process requires capture images to be processed, for this, the receivers allow connect with multiple sources of videos.

For capture the video of cam only use the class **<[ReceiverIpCam](#interface-receiver)>**, and pass the url:

``` python
from mvfy.visual.receiver import ReceiverIpCam

detector = ReceiverIpCam(
  ip_cam="rtsp://user:password@ip:port/h264_ulaw.sdp"
)
```

### Detector

After receive the image send by the **[Receiver](#receiver)**, the process requires one detector, you could use the classes inside the module detector.

For detect all unknown faces in an image you can use the DetectorUnknows class. Returns **<[DetectorUnknows](#interface-detector)>**:

``` python
from mvfy.visual.detector import DetectorFaces

umbral = 0.7
detector_knows = DetectorFaces(tolerance_comparation= 1 - umbral)
detector_unknows = DetectorFaces(tolerance_comparation= 1 - umbral)
```
* "tolerance_comparation" is a value to compare faces, less is more strict

### Streamer

After process the image, it will be send to the webbrowser trough the streamer.

For this example we used the FlaskStreamer, you need first install the module of [Flask](https://flask.palletsprojects.com/) to use it. Returns **[FlaskStreamer](#streamer)**:

``` python
from mvfy.visual.streamer import FlaskStreamer

streamer = FlaskStreamer()
```
* streamer is a generator of images (bytes) post-processed ready to send

## Systems 

when you have instantiated all of the above sub-instances, you simply pass them through the **[Systems](#systems)**.

For this example we used the VisualKnowlege, you need first install the module of [Flask](https://flask.palletsprojects.com/) to use it:

* for use is require the next:
* * Receiver - for getting the images
* * detector_knowns - for detect the faces of knowns users
* * detector_unknowns - for detect the faces of unknowns users
* * streamer - to send result image

``` python

from mvfy.visual.generator import VisualKnowledge

visual = VisualKnowledge(
    detector_knows=detector_knows,
    detector_unknows=detector_unknows,
    receiver=receiver,
    streamer=streamer,
    ...
)
```

<a name="basic-example-visualknowledge"></a>
A complete example:

``` python

import asyncio
import threading
from time import time

from flask import Flask, Response, render_template_string
from flask_cors import CORS

from mvfy.utils import constants as const, index as utils
from mvfy.visual.detector import DetectorFaces
from mvfy.visual.generator import VisualKnowledge
from mvfy.visual.receiver import ReceiverIpCam
from mvfy.visual.streamer import FlaskStreamer

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

receiver = ReceiverIpCam(ip_cam="rtsp://mvfy:mvfy@192.168.1.4:8080/h264_ulaw.sdp")
detector_knows = DetectorFaces(tolerance_comparation= 1 - 0.7)
detector_unknows = DetectorFaces(tolerance_comparation= 1 - 0.7)
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
    features=features,
    title="mvfy_1",
)


@app.route("/")
def index():
    return streamer.get_template()


@app.route("/stream_video")
def stream_video() -> Response:
    return Response(streamer, mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)

```
