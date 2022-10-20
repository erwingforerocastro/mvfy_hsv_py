from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Union

import cv2
from pydantic.dataclasses import dataclass
from . import errors
from mvfy.utils import constants


class Receiver(ABC):
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def start(self) -> Iterable :
        pass
    
@dataclass
class ReceiverIpCam(Receiver):

    ip_cam: str
    dimensions: Tuple[int, int] = constants.IMAGE_DIMENSIONS

    def start(self) -> Iterable:
        def inside_function():
            stream = None
            try:
                print(f"conecting.... {self.ip_cam}")
                if stream is None:
                    stream = cv2.VideoCapture(self.ip_cam)
                print("init the capture of image")
                
                if stream is None:
                    raise errors.FailedConnectionWithRSTP(self.ip_cam)

                while stream.isOpened():
                    try:
                        yield stream.read()
                        
                        if stream is None:
                            print(f"reconecting.... {self.ip_cam}")
                            stream = cv2.VideoCapture(self.ip_cam)

                    except Exception as error:
                        raise Exception(f"Error in stream connection {error}")

            except Exception as error:
                raise Exception(f"Error in connection to {self.ip_cam}, {error}")

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