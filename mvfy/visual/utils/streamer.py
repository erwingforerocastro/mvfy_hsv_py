import asyncio
import base64
from flask_socketio import SocketIO, emit
from flask import Flask, render_template
import multiprocessing

BUFF_SIZE = 2073600
SIZE = (1920, 1080)


class Streamer():

    def __init__(self, 
        url_server: str, 
        ip_cam: str,  
        app: 'Flask' = None,
        socket_options: 'dict' = None,
        title: str = "window",
        *args, **kargs) -> None:
        """Constructor
        
        
        Args:
            url_server (str): [description]
            ip_cam (str): [description]
        """
        self.app = Flask(__name__) if app is None else app
        self.socketio = SocketIO(self.app, **socket_options) 
        self.title = title
        self.url_server = url_server
        self.state = 0  # conection, 0 disconnect, 1 conected, 2 wait connection
        self._temp_url = None
        self.app.config['SECRET_KEY'] = 'secret'
        self.socketio.on('connect')(
            self.ws
        )
        # self.socketio.on('rcv_image')(self.ws)

    def ws(self):
        # self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        # self.server.bind((self.url_server["host"], int(self.url_server["port"])))
        
        try:
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            coroutine = self.connection_client()
            loop.run_until_complete(coroutine)

        except Exception as e:
            raise Exception(e)

    async def connection_client(self) -> None:

        try:
            # self.server.listen()
            print("conecting....")
            await self.connect(self.ip_cam)
            # msg, client_addr = self.server.recvfrom(BUFF_SIZE)
            # print(f"new connection {client_addr}")

        except Exception as e:
            raise ConnectionError(
                f"Invalid conection to {self.url_server}, {e}")

        # finally:
        #     # self.socketio.close()

    async def __trying_connection(self) -> None:
        self.state = 2
        if self._temp_url is not None:
            await self.connect(self._temp_url)
            self.state = 1
            return
        else:
            self.state = 0

        cv2.destroyAllWindows()

    async def connect(self, url: str) -> None:
        try:
            if self.stream is None:
                self.stream = cv2.VideoCapture(url)
            self._temp_url = url
            print("init the capture of image")
            await self.start()

        except Exception as e:
            raise Exception(e)

    async def start(self):

        if self.stream is None:
            raise Exception("Stream is required")

        self.state = 1

        while self.state == 1:
            try:
                _, self._img_capture = self.stream.read()
                self.send_image()
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.state = 0
            except:
                await self.__trying_connection()

    def send_image(self) -> None:
        if self._img_capture is not None:
            frame = cv2.resize(self._img_capture, SIZE)
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)

            emit('image-event', message)

            self.update_video()

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
        cv2.imshow(self.title, self._img_capture)
            

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
