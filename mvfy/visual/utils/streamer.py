import asyncio
import base64
import threading
import cv2

import numpy as np
from flask_socketio import SocketIO, emit
from flask import Flask, render_template
import multiprocessing


class Streamer():

    def __init__(self) -> None:
        """Constructor
        """
        
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

        async def wraper_function(img, extension: str = ".jpg", size: tuple = (1920, 1080)):
        
            if size is not None:
                frame = cv2.resize(img, size)

            _, buffer = cv2.imencode(extension, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            data = base64.b64encode(buffer)

            socketio.emit(socket_msg, {
                "data": data
            })

        return wraper_function

    @staticmethod
    async def stream_local(
        img: np.array,
        size: tuple = (1920, 1080),
        title: str = "title"
    ) -> None:
            if size is not None:
                img = cv2.resize(img, size)
            cv2.imshow(title, img)