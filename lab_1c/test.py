from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER
from asyncio import *
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol
from enum import Enum

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
    def __init__(self):
        self.transport = None
        self.state = None
        self.RespondPacket = None
        self._deserializer = PacketType.Deserializer()


    def connection_made(self, transport):
        print("---Server connected to the client---")
        self.transport = transport
        self.state = "initial"


    def data_received(self, data):
        print("---Server received data---")
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if isinstance(pkt, GetDeviceList):
                if self.state == "initial":
                    print("Server: Received a GetDeviceList request!")
                    self.RespondPacket = DeviceList()
                    self.RespondPacket.ID = pkt.number
                    self.RespondPacket.category = pkt.category
                    self.state = "wait modify packet"
                else:
                    print("state error E01")
                    self.state = "E01"
                    self.loop.stop()
            elif isinstance(pkt, ModifyDevice):
                if self.state == "wait modify packet":
                    print("Server: Received a ModifyDevice request!")
                    self.RespondPacket = Respond()
                    self.RespondPacket.ID = pkt.ID
                    self.state = "end"
                elif self.state == "initial":
                    print("state error E02")
                    self.state == "E02"
                    self.loop.stop()
                else:
                    self.state == "E01"
                    self.loop.stop()
            else:
                print("received error packet")
                self.state = "end"


    def DeviceList(self):
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
            self.RespondPacket.name = b"Can not find this device"
            self.RespondPacket.status = b"None"
        self.transport.write(self.RespondPacket.__serialize__())

    def Respond(self):
        if (self.RespondPacket.ID == 1001):
            self.RespondPacket.respond = b"Succeeded!"
        elif (self.RespondPacket.ID == 1001):
            self.RespondPacket.respond = b"Failed! Already on!"
        elif (self.RespondPacket.ID == 1002):
            self.RespondPacket.respond = b"Failed!"
        elif (self.RespondPacket.ID == 1003):
            self.RespondPacket.respond = b"Succeeded!"
        else:
            self.RespondPacket.respond = b"Error!Can not find this device!"

        self.transport.write(self.RespondPacket.__serialize__())

    def connection_lost(self, exc):
        self.transport = None
        print("IoT Server Connection Lost because {}".format(exc))


class IoTClientProtocol(Protocol):
    def __init__(self):
        self.transport = None
        self.state = None
        self.RespondPacket = None
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("---Client connected---")
        self.transport = transport
        self.state = "initial"

    def data_received(self, data):
        print("---Client received data---")
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if isinstance(pkt, DeviceList):
                if self.state == "initial":
                    print("Client: Received a DeviceList!")
                    self.RespondPacket = ModifyDevice()
                    self.RespondPacket.ID = pkt.ID
                    self.state = "wait respond packet"
                else:
                    print("state error E01")
                    self.state = "E01"
                    self.loop.stop()
            elif isinstance(pkt, Respond):
                if self.state == "wait respond packet":
                    print("Client: Received a respond message!")
                    if (pkt.respond == b"Succeeded!"):
                        print("Congratulations! Operation Succeeded!")
                    elif (pkt.respond == b"Failed!"):
                        print("Operation Failed!")
                    self.state = "end"
                elif self.state == "initial":
                    print("state error E02")
                    self.state == "E02"
                    self.loop.stop()
                else:
                    self.state == "E01"
                    self.loop.stop()
            else:
                print("received error packet")
                self.state = "end"

    def ModifyDevice(self):
        if (self.RespondPacket.ID == 1001):
            self.RespondPacket.operation = b"off"
        elif (self.RespondPacket.ID == 1002):
            self.RespondPacket.operation = b"on"
        elif (self.RespondPacket.ID == 1003):
            self.RespondPacket.operation = b"off"
        else:
            self.RespondPacket.operation = b"Can not identify device"
        self.transport.write(self.RespondPacket.__serialize__())

    def GetDeviceList(self):
        self.RespondPacket = GetDeviceList()
        self.RespondPacket.category = "lamp"
        self.RespondPacket.number = 1001
        self.transport.write(self.RespondPacket.__serialize__())

    def connection_lost(self, exc):
        self.transport = None
        print("IoT Server Connection Lost because {}".format(exc))

def BasicUnitTest():
    set_event_loop(TestLoopEx())
    client = IoTClientProtocol()
    server = IoTServerProtocol()
    transportToServer = MockTransportToProtocol(server)
    transportToClient = MockTransportToProtocol(client)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)

    client.GetDeviceList()
    server.DeviceList()
    client.ModifyDevice()
    server.Respond()


if __name__=="__main__":
    BasicUnitTest()