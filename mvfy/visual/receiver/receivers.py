from abc import ABC, abstractmethod
from typing import Iterable, Union

import cv2
from pydantic.dataclasses import dataclass


class Receiver(ABC):
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def start(self) -> None:
        pass
    

@dataclass
class ReceiverIpCam(Receiver):

    ip_cam: str

    def start(self) -> Iterable:
        def inside_function():
            stream = None
            try:
                print(f"conecting.... {self.ip_cam}")
                if stream is None:
                    stream = cv2.VideoCapture(self.ip_cam)
                print("init the capture of image")

                if stream is None:
                    raise Exception("Stream error")

                while stream.isOpened():
                    try:
                        
                        yield stream.read()
                        
                        if stream is None:
                            print(f"conecting.... {self.ip_cam}")
                            stream = cv2.VideoCapture(self.ip_cam)
                    except Exception as e:
                        raise Exception(
                            f"Error in stream connection {e}")

            except Exception as e:
                raise Exception(
                    f"Error in connection to {self.ip_cam}, {e}")

        return inside_function()

class ReceiverSocket(Receiver):
    """
    TODO: implement all properties to this class

    :param Receiver: _description_
    :type Receiver: _type_
    :raises Exception: _description_
    :raises Exception: _description_
    :return: _description_
    :rtype: _type_
    """
    server_socket: Union[tuple, str] = ""
    buffer_size: int = 1024

    def start(self):
        def inside_function():
            socketio = None
            sock = socketio.client()
            stream = None

            try:
                print(f"conecting.... {self.server_socket}")
                sock.connect(self.server_socket)
                print("init the capture of image")

                while True:
                    try:
                        if stream is None:
                            pass
                            # stream = socketio.on('connect')(lambda: yield stream.read())
                        
                        print(f"conecting....")

                    except Exception as err:
                        raise Exception(
                            f"Error in stream connection {err}")

            except Exception as err:
                raise Exception(
                    f"Error in conection to {err}")

        return inside_function