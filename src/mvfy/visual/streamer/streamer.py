import asyncio
import logging
import os
import pickle
import struct
import threading
import time
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Any, Generator, Optional, Tuple

import cv2
import socket
from flask import render_template_string
import numpy as np
from mvfy.visual.func import loop_manager
from mvfy.visual.systems.image_generator import ImageGenerator
from pydantic.dataclasses import dataclass

from .errors import StreamSocketInsufficientSlots, StreamTemplateNotFound


class Streamer(ABC):

    @abstractmethod
    def send(self)-> bytes:
        pass 

@dataclass
class FlaskStreamer(Streamer):

    dimensions: Tuple[int, int] = (720, 480)
    extension: Optional[str] = ".jpg"
    images_queue: Optional[Any] = None
    images_queue_size: int = 0
    wait_message: str = "wait...."
    wait_image: Any = None
    framerate: int = 24
    time_to_wait: int = 1
    end_time_return: float = time.time()

    def __post_init__(self):
        self.images_queue = Queue()
        self._thread_lock = threading.Lock()
        self.__create_wait_image()

    def __create_wait_image(self) -> None:
        """_summary_
        """
        self.wait_image = np.zeros([self.dimensions[1], self.dimensions[0], 1], dtype = np.uint8)
        center_image = (self.wait_image.shape[1] // 2, self.wait_image.shape[0] // 2)
        self.wait_image = cv2.putText(self.wait_image, self.wait_message, center_image, cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        flag, resize_image = cv2.imencode(self.extension, self.wait_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if flag:
            self.wait_image: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(resize_image) + b'\r\n'

    def get_template(self) -> str:
        """_summary_

        :raises StreamTemplateNotFound: _description_
        :return: _description_
        :rtype: str
        """        
        dir_name: str = os.path.dirname(os.path.abspath(__file__))
        template_path: str = os.path.join(dir_name, "stream_flask_template.html")
        
        if not os.path.exists(template_path):
            raise StreamTemplateNotFound(path_file = template_path)
        
        with open(template_path, "r", encoding = "utf-8") as f:
            template = f.read()

        return render_template_string(template, title = "mvfy_visual")
    
    @loop_manager
    async def img2bytes(self, image, loop: 'asyncio.AbstractEventLoop') -> bytes:

        
        images_bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray() + b'\r\n'
        flag, resize_image = await loop.run_in_executor(None, lambda: cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80]))

        if flag:
            images_bytes: bytes = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(resize_image) + b'\r\n'
            
        return images_bytes
    
    async def save(self, batch_images: list[Any]) -> Any:

            tasks = [self.img2bytes(img) for img in batch_images]
            results = await asyncio.gather(*tasks)

            for result in results:
                await self.images_queue.put(result)
                self.images_queue_size += 1

            print(self.images_queue_size)
            
    def send(self)-> bytes:
        """_summary_

        :return: _description_
        :rtype: _type_
        """       
        #TODO: optimize the fluency of the video
        
        try:
            while self.images_queue.empty():
                print("waiting streaming...")
                while self.images_queue.empty():
                    time.sleep(self.time_to_wait)

            image_to_send = self.images_queue.get_nowait()
            self.images_queue_size -= 1

            # wait = (1 / self.framerate) - (time.time() - self.end_time_return)
            # if wait < 0:
            #     print(f'delay:{wait} ')

            delay_time = max(0, (1 / self.framerate) - (time.time() - self.end_time_return))
            time.sleep(delay_time)

            self.end_time_return = time.time()

            return image_to_send
                
        except Exception as error:
            logging.error(f"Error sending the image, {error}")
            return self.wait_image
    
    def __iter__(self):
                
        return self

    def __next__(self):

        return self.send()
        
@dataclass
class SocketStreamer():
    host: str
    port: str
    slots: int = 10
    socket_args: Tuple = (socket.AF_INET, socket.SOCK_STREAM)
    dimensions: Tuple[int, int] = (720, 480)
    extension: Optional[str] = ".jpg"
    images_queue_size: int = 0
    wait_message: str = "wait...."
    wait_image: Any = None

    def __post_init__(self):
        self.__running: bool = False
        self.__server_socket = socket.socket(*self.socket_args)
        self.__server_socket.bind((self.host, self.port))
        self.__images_queue = Queue()
        self.__create_wait_image()

    def __server_listening(self):
        """
        Listens for new connections.
        """
        self.__server_socket.listen(self.slots)   
        print(f"stream socket listening in: {(self.host, self.port)}")

        while self.__running: 

            connection, address = self.__server_socket.accept()
            print(f"stream socket new connection in: {address}")
            self.__client_connection(connection)

    def __client_connection(self, connection: socket.socket):

        while self.__images_queue.empty():
            time.sleep(0.1)

        image_to_send = self.__images_queue.get_nowait()
        self.images_queue_size -= 1
    
        message = struct.pack("Q", len(image_to_send)) + image_to_send

        try:
            connection.sendall(message)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as error:
            logging.error(f"Stream socket connection error: {error}")
            self.stop()

    def __create_wait_image(self) -> None:
        """_summary_
        """
        self.wait_image = np.zeros([self.dimensions[0], self.dimensions[1], 1], dtype = np.uint8)
        center_image = (self.wait_image.shape[1] // 2, self.wait_image.shape[0] // 2)
        self.wait_image = cv2.putText(self.wait_image, self.wait_message, center_image, cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        flag, resize_image = cv2.imencode(self.extension, self.wait_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if flag:
            self.wait_image: bytes = pickle.dumps(resize_image)
    
    @loop_manager
    async def __img2bytes(self, image, loop: 'asyncio.AbstractEventLoop') -> bytes:

        images_bytes = b''
        flag, resize_image = await loop.run_in_executor(None, lambda: cv2.imencode(self.extension, image, [cv2.IMWRITE_JPEG_QUALITY, 80]))

        if flag:
            images_bytes: bytes = pickle.dumps(resize_image)
        
        return images_bytes

    def start(self):
        if self.__running:
            print("Server is already running")
        else:
            self.__running = True
            server_thread = threading.Thread(target=self.__server_listening)
            server_thread.start()
    
    def stop(self):
        """
        Stops the server and closes all connections
        """
        if self.__running:
            self.__running = False
            self.__server_socket.close()
        else:
            print("Server not running!")

    async def save(self, batch_images: list[Any]) -> Any:

        tasks = [self.__img2bytes(img, loop=None) for img in batch_images]
        results = await asyncio.gather(*tasks)

        for result in results:
            await self.__images_queue.put(result)
            self.images_queue_size += 1