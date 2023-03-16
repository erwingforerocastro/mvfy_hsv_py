from abc import ABC, abstractmethod
from asyncio import Queue
import asyncio
import time
from typing import Any, Iterable, Optional, Tuple, Union

import cv2
import numpy as np
from pydantic.dataclasses import dataclass
from . import errors
from mvfy.utils import constants


class Receiver(ABC):
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def get(self) -> bytes:
        pass

@dataclass
class ReceiverIpCam(Receiver):

    ip_cam: str
    dimensions: Tuple[int, int] = constants.IMAGE_DIMENSIONS
    stream: Any = None
    framerate: int = 30
    detections_failed: int = 0
    time_to_wait: int = 1
    images_queue: Optional[Any] = None
    images_queue_size: int = 0

    def __post_init__(self):
        
        self.images_queue = Queue()

    def __init_stream(self) -> None:

        print(f"conecting.... {self.ip_cam}")

        self.stream = cv2.VideoCapture(self.ip_cam)
        
        if self.stream is None:
            raise errors.FailedConnectionWithRSTP(self.ip_cam)
        
    async def start(self) -> None:

        try:
            self.__init_stream()

            while self.stream.isOpened():
                try:
                    ret, img = self.stream.read()
                    if ret:
                        await self.images_queue.put(img)
                        self.images_queue_size += 1
                        self.detections_failed = 0
                    else:
                        self.detections_failed += 1
                    if self.stream is None or self.detections_failed > self.framerate:
                        print(f"reconecting.... {self.ip_cam}")
                        self.__init_stream()

                except StopIteration:
                    print(f"reconecting.... {self.ip_cam}")
                    self.__init_stream()
                
                except Exception as error:
                    raise Exception(f"Error in stream connection {error}")

        except Exception as error:
            raise Exception(f"Error in connection to {self.ip_cam}, {error}")

    
    def get(self) -> np.array:

        # while self.images_queue.empty():
            # print('waiting ip cam ...')
        while self.images_queue.empty():
                time.sleep(time_to_wait)

        image = self.images_queue.get_nowait()
        self.images_queue_size -= 1

        return image
    
    def __iter__(self):

        return self

    def __next__(self):

        return self.get()
    
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