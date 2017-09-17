import playground
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
from client import *
from server import *
from asyncio import *
from packets import *


class PassThrough1(StackingProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(transport)
        print("PassThrough1 connection made")

    def data_received(self, data):
        self.higherProtocol().data_received(data)
        print("PassThrough1 received data.")

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost()


class PassThrough2(StackingProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(transport)
        print("PassThrough2 connection made")

    def data_received(self, data):
        self.higherProtocol().data_received(data)
        print("PassThrough2 received data.")

    def connection_lost(self, exc):
        self.higherProtocol().connection_lost()


def PassThroughTest():
    loop = get_event_loop()
    loop.set_debug(enabled=True)

    f = StackingProtocolFactory(lambda: PassThrough1(), lambda: PassThrough2())
    ptConnector = playground.Connector(protocolStack=f)
    playground.setConnector("passthrough", ptConnector)

    coro = playground.getConnector('passthrough').create_playground_server(lambda: IoTServerProtocol(), 5555)
    server = loop.run_until_complete(coro)

    connect = playground.getConnector('passthrough').create_playground_connection(lambda: IoTClientProtocol(),'20174.1.1.1', 5555)

    transport, client = loop.run_until_complete(connect)
    client.GetDeviceList()

    loop.run_forever()
    loop.close()


if __name__ == "__main__":

    PassThroughTest()


