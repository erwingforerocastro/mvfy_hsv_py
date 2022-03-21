import cv2

class Receiver:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def ip_cam_capture(ip_cam: 'str'):
        def inside_function():
            stream = None
            try:
                print(f"conecting.... {ip_cam}")
                if stream is None:
                    stream = cv2.VideoCapture(ip_cam)
                print("init the capture of image")

                if stream is None:
                    raise Exception("Stream error")

                while True:
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

