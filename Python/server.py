import asyncio

class Receiver(asyncio.Protocol):
    def __init__(self):
        self.buffer = ""
        super()

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        self.buffer += data.decode()

        while not self.buffer.find("\n") == -1:
            index = self.buffer.find("\n")
            string = self.buffer[:index + 1]
            print('Data received: {!r}'.format(string))
            self.buffer = self.buffer[index + 1:]

class Transmitter():
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        pass

loop = asyncio.get_event_loop()

# One protocol instance will be created to serve all client requests
transmit = loop.create_datagram_endpoint(Transmitter, local_addr=("0.0.0.0", 5806))
transport, protocol = loop.run_until_complete(transmit)

# Each client connection will create a new protocol instance
receive = loop.create_server(lambda: Receiver(), "", 5805)
server = loop.run_until_complete(receive)

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