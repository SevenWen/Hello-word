import asyncio
import playground

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        print(data)
        message = data.decode()+'from server'
        print('Data received in server: {!r}'.format(message))

        print('Send: {!r}'.format(message))
        self.transport.write(message.encode())

        print('Close the client socket')
        self.transport.close()

    def connection_lost(self, exc):
        print('Closed the connection')

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = playground.getConnector().create_playground_server(EchoServerClientProtocol,
                                                          101)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
