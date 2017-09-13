from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER
from asyncio import *
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol


class GetDeviceList(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.zli.getdevicelist"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("category", STRING),
        ("number", UINT32)
    ]

class DeviceList(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.zli.devicelist"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("name", BUFFER),
        ("category", STRING),
        ("status", BUFFER)
    ]

class ModifyDevice(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.zli.modifydevice"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("operation", BUFFER)
    ]

class Respond(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.zli.respond"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("respond", BUFFER)
    ]





class IoTServerProtocol(Protocol):
    initial = 0
    wtmodifypkt = 1
    end =2
    ERROR = 9

    def __init__(self):
        self.transport = None
        self.state = None
        self.RespondPacket = None
        self._deserializer = PacketType.Deserializer()


    def connection_made(self, transport):
        print("---Server connected!---")
        self.transport = transport
        self.state = self.initial


    def data_received(self, data):
        print("---Server received data---")
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if isinstance(pkt, GetDeviceList):
                if self.state == self.initial:
                    print("Server: Received a GetDeviceList request!")
                    self.RespondPacket = DeviceList()
                    self.RespondPacket.ID = pkt.number
                    self.RespondPacket.category = pkt.category
                    self.state = self.wtmodifypkt
                else:
                    print("state error")
                    self.state = self.ERROR
            elif isinstance(pkt, ModifyDevice):
                if self.state == self.wtmodifypkt:
                    print("Server: Received a ModifyDevice request!")
                    self.RespondPacket = Respond()
                    self.RespondPacket.ID = pkt.ID
                    self.state = self.end
                else:
                    self.state == self.ERROR
            else:
                print("received error packet")
                self.state = self.end
            '''if (self.state == self.end or self.state == self.ERROR):
                self.transport.close()'''


    def DeviceList(self):
        print("Server State: {!r}".format(self.state))
        if (self.RespondPacket.category == "lamp" and self.RespondPacket.ID == 1001):
            self.RespondPacket.name = b"table lamp"
            self.RespondPacket.status = b"on"
        elif (self.RespondPacket.category == "lamp" and self.RespondPacket.ID == 1002):
            self.RespondPacket.name = b"floor lamp"
            self.RespondPacket.status = b"off"
        elif (self.RespondPacket.category == "computer" and self.RespondPacket.ID == 2001):
            self.RespondPacket.name = b"MacBook"
            self.RespondPacket.status = b"on"
        else:
            self.RespondPacket.name = b"Error"
            self.RespondPacket.status = b"None"
        print("Server: Send DeviceList   ID:{}".format(self.RespondPacket.ID) + "\n")
        self.transport.write(self.RespondPacket.__serialize__())


    def Respond(self):
        print("Server State: {!r}".format(self.state))
        if (self.RespondPacket.ID == 1001):
            self.RespondPacket.respond = b"Succeeded!"
        elif (self.RespondPacket.ID == 1002):
            self.RespondPacket.respond = b"Failed!"
        elif (self.RespondPacket.ID == 2001):
            self.RespondPacket.respond = b"Succeeded!"
        else:
            self.RespondPacket.respond = b"Error!Can not find this device!"
        print("Server: Send Response packet:{}".format(self.RespondPacket.respond) + "\n")
        self.transport.write(self.RespondPacket.__serialize__())

    def connection_lost(self, exc):
        self.transport = None
        print("IoT Server Connection Lost because {}".format(exc))


class IoTClientProtocol(Protocol):
    initial = 0
    wtrespond = 1
    end = 2
    ERROR = 9
    def __init__(self):
        self.transport = None
        self.state = None
        self.RespondPacket = None
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("---Client connected!---")
        self.transport = transport
        self.state = self.initial

    def data_received(self, data):
        print("---Client received data---")
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if isinstance(pkt, DeviceList):
                if self.state == self.initial:
                    print("Client: Received a DeviceList")
                    self.RespondPacket = ModifyDevice()
                    self.RespondPacket.ID = pkt.ID
                    self.state = self.wtrespond
                else:
                    print("state error")
                    self.state = self.ERROR
            elif isinstance(pkt, Respond):
                if self.state == self.wtrespond:
                    print("Client: Received a respond message!")
                    if (pkt.respond == b"Succeeded!"):
                        print("Congratulations! Operation Succeeded!")
                    elif (pkt.respond == b"Failed!"):
                        print("Operation Failed!")
                    self.state = self.end
                else:
                    self.state == self.ERROR
                print("Client State: {!r}".format(self.state))
            else:
                print("received error packet")
                self.state = self.end



    def ModifyDevice(self):
        print("Client State: {!r}".format(self.state))
        if (self.RespondPacket.ID == 1001):
            self.RespondPacket.operation = b"off"
        elif (self.RespondPacket.ID == 1002):
            self.RespondPacket.operation = b"on"
        elif (self.RespondPacket.ID == 1003):
            self.RespondPacket.operation = b"off"
        else:
            self.RespondPacket.operation = b"Can not identify device"
        print("Client: Sent ModifyDevice packet  ID:{}".format(self.RespondPacket.ID) + "\n")
        self.transport.write(self.RespondPacket.__serialize__())

    def GetDeviceList(self):
        print("Test start!")
        print("Client State: {!r}".format(self.state))
        self.RespondPacket = GetDeviceList()
        self.RespondPacket.category = "lamp"
        self.RespondPacket.number = 1001
        print("Client: Sent GetDeviceList packet  ID:{}".format(self.RespondPacket.number)+"\n")
        self.transport.write(self.RespondPacket.__serialize__())

    def connection_lost(self, exc):
        self.transport = None
        print("IoT Server Connection Lost because {}".format(exc))

def BasicUnitTest():
    set_event_loop(TestLoopEx())
    client = IoTClientProtocol()
    server = IoTServerProtocol()
    transportToServer = MockTransportToProtocol(myProtocol=client)
    transportToClient = MockTransportToProtocol(myProtocol=server)
    transportToServer.setRemoteTransport(transportToClient)
    transportToClient.setRemoteTransport(transportToServer)

    client.connection_made(transportToServer)
    server.connection_made(transportToClient)

    client.GetDeviceList()
    server.DeviceList()
    client.ModifyDevice()
    server.Respond()

if __name__=="__main__":
    BasicUnitTest()