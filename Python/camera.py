import asyncio
import cv2

class Camera(object):
    def __init__(self, queue: asyncio.Queue, port: int, width: int, height: int, period=0.04: float):
        # Set camera port.
        self.camera = cv2.VideoCapture(port)
        
        # Set camera resolution.
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Center of camera is our target position.
        self.target_position = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

        self.queue = queue

        self.period = period
    
    async def capture_frame():
        while True:
            _, frame = self.camera.read()
            self.queue.put_nowait(frame)
            await asyncio.sleep(period)
