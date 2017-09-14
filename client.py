import asyncio
import playground

class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        self.transport=transport
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

loop = asyncio.get_event_loop()
message = 'Hello World!'
coro = playground.getConnector().create_playground_connection(lambda: EchoClientProtocol(message, loop),'20174.1.1.1',
                                                              38635)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()
