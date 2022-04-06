import cv2
import socketio

class Receiver:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def ip_cam_receiver(ip_cam: 'str'):
        def inside_function():
            stream = None
            try:
                print(f"conecting.... {ip_cam}")
                if stream is None:
                    stream = cv2.VideoCapture(ip_cam)
                print("init the capture of image")

                if stream is None:
                    raise Exception("Stream error")

                while stream.isOpened():
                    try:
                        yield stream.read()
                        
                        print(f"conecting.... {ip_cam}")
                        if stream is None:
                            stream = cv2.VideoCapture(ip_cam)
                    except:
                        raise Exception(
                            f"Error in stream connection {e}")

            except Exception as e:
                raise Exception(
                    f"Error in conection to {ip_cam}, {e}")

        return inside_function

    @staticmethod
    def socket_receiver(server_socket: 'tuple|str', buffer_size: float = 1024):
        def inside_function():
            sock = socketio.client()
            stream = None
            try:
                print(f"conecting.... {server_socket}")
                sock.connect(server_socket)
                print("init the capture of image")

                while True:
                    try:
                        # if stream is None:
                        #     stream = socketio.on('connect')(lambda: yield stream.read())
                        
                        print(f"conecting.... {ip_cam}")
                        if stream is None:
                            stream = cv2.VideoCapture(ip_cam)
                    except:
                        raise Exception(
                            f"Error in stream connection {e}")

            except Exception as e:
                raise Exception(
                    f"Error in conection to {ip_cam}, {e}")

        return inside_function