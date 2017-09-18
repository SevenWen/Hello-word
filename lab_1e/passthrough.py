import playground
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory

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
        self.higherProtocol().connection_lost(exc)


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
        self.higherProtocol().connection_lost(exc)




