import asyncio
import base64
import threading
import cv2

import numpy as np
from flask_socketio import SocketIO, emit
from flask import Flask, render_template
import multiprocessing


class Streamer():

    def __init__(self, *args, **kargs) -> None:
        """Constructor

        Args:
            url_server (str): [description]
            ip_cam (str): [description]
        """
        pass
        
    @staticmethod
    async def stream_socket(
        url_server: str, 
        app: 'Flask' = None,
        socket_options: 'dict' = None,
        socket_msg: 'str' = "mvfy_visual_img",
    )-> 'function':

        app = Flask(__name__) if app is None else app
        socketio = SocketIO(app, **socket_options) 
        threading.Thread(target=lambda: socketio.run(url_server)).run()

        def wraper_function(img, extension: str = ".jpg", size: tuple = (1920, 1080)):
        
            if size is not None:
                frame = cv2.resize(img, size)

            _, buffer = cv2.imencode(extension, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            data = base64.b64encode(buffer)

            socketio.emit(socket_msg, {
                "data": data
            })

        return wraper_function

    @staticmethod
    async def stream_local(self,
        img: np.array,
        size: tuple = (1920, 1080),

    ) -> None:
        if self._img_capture is not None:
            frame = cv2.resize(self._img_capture, SIZE)
            cv2.imshow(self.title, self._img_capture)

            self.update_video()

    def send_image(self) -> None:
        if self._img_capture is not None:
            

    def image(data_image):

        # sbuf = StringIO()
        # sbuf.write(data_image)
        
        # b = io.BytesIO(base64.b64decode(data_image))
        # if(str(data_image) == "data:,"):
        #     pass
        # else:
        
        # #process the image for object detetection
        # imgencode = cv2.imencode(".jpg", frame)[1]

        # stringData = base64.b64encode(imgencode).decode("utf-8")
        # b64_src = "data:image/jpg;base64,"
        # stringData = b64_src + stringData
        # emit("response_back", stringData)
        pass

    def update_video(self):
        
            

stream = Streamer(
    url_server={
        "host": "127.0.0.1",
        "port": "8088"
    },
    url_client={
        "host": "127.0.0.2",
        "port": "8089"
    },
    ip_cam='rtsp://mvfysystem:mvfysystem@192.168.1.1:8080/h264_ulaw.sdp'
)
