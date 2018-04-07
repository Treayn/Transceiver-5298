import asyncio

from camera import Camera
from cube_vision import CubeVision
from tape_vision import TapeVision

class Receiver(asyncio.Protocol):
    def __init__(self, events, response):
        self.buffer = ""
        self.events = events
        self.response = response
        super()

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        self.buffer += data.decode()

        while not self.buffer.find("\n") == -1:
            index = self.buffer.find("\n")
            self._parse_string(self.buffer[:index + 1])
            self.buffer = self.buffer[index + 1:]

    def _parse_string(self, string: str):
        print('Data received: {!r}'.format(string))
        request_type, vision_type, data_type = string.split("+")

        if data_type == "enableTargeting":
            self._enable_targeting(vision_type)
        elif data_type == "disableTargeting":
            self._disable_targeting(vision_type)
    
    def _enable_targeting(self, target:str):
        self.events[target].set()
    
    def _disable_targeting(self, target: str):
        self.events[target].clear()

class Transmitter():
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    events = {
        "Cube": asyncio.Event()
        "Tape": asyncio.Event()
    }

    frame_queue = asyncio.LifoQueue()

    camera = Camera(frame_queue, 0, 1080, 720)

    # One protocol instance will be created to serve all client requests
    transmit = loop.create_datagram_endpoint(Transmitter, local_addr=("0.0.0.0", 5806))
    transport, protocol = loop.run_until_complete(transmit)

    # Each client connection will create a new protocol instance
    receive = loop.create_server(lambda: Receiver(events, transport), "", 5805)
    server = loop.run_until_complete(receive)

    video = loop.run_until_complete(camera.capture_frame)



    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        for i in range(0, 10):
            print("Sending"+ str(i))
            transport.sendto(("data+Cube+"+ str(i) +"\n").encode(), ("192.168.1.173", 5806))

    # Close the server
    transport.close()
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()