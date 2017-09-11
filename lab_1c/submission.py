# This is

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
    def __init__(self):
        self.transport = None
        self.RespondPacket = None
        self._deserializer = PacketType.Deserializer()


    def connection_made(self, transport):
        print("---Server connected to the client---")
        self.transport = transport


    def data_received(self, data):
        print("---Server received data---")
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if isinstance(pkt, GetDeviceList):
                print("Server: Received a GetDeviceList request!")
                self.RespondPacket = DeviceList()
                self.RespondPacket.ID = pkt.number
                self.RespondPacket.category = pkt.category
                if (pkt.category == "lamp" and pkt.number == 1001):
                    self.RespondPacket.name = b"table lamp"
                    self.RespondPacket.status = b"on"
                elif (pkt.category == "lamp" and pkt.number == 1002):
                    self.RespondPacket.name = b"floor lamp"
                    self.RespondPacket.status = b"off"
                elif (pkt.category == "computer" and pkt.number == 2001):
                    self.RespondPacket.name = b"MacBook"
                    self.RespondPacket.status = b"on"
                else:
                    self.RespondPacket.name = b"Can not find this device"
                    self.RespondPacket.status = b"None"
                self.transport.write(self.RespondPacket.__serialize__())
            if isinstance(pkt, ModifyDevice):
                print("Server: Received a ModifyDevice request!")
                self.RespondPacket = Respond()
                self.RespondPacket.ID = pkt.ID
                if (pkt.ID == 1001 and pkt.operation == b"off"):
                    self.RespondPacket.respond = b"Succeeded!"
                elif (pkt.ID == 1001 and pkt.operation == b"on"):
                    self.RespondPacket.respond = b"Failed! Already on!"
                elif (pkt.ID == 1002 and pkt.operation == b"on"):
                    self.RespondPacket.respond = b"Failed!"
                elif (pkt.ID == 1003):
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
        self.RespondPacket = None
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        print("---Client connected---")
        self.transport= transport

    def data_received(self, data):
        print("---Client received data---")
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
            if isinstance(pkt, DeviceList):
                print("Client: Received a DeviceList!")
                self.RespondPacket = ModifyDevice()
                self.RespondPacket.ID = pkt.ID
                if (pkt.ID == 1001):
                    self.RespondPacket.operation = b"off"
                elif (pkt.ID == 1002):
                    self.RespondPacket.operation = b"on"
                elif (pkt.ID == 1003):
                    self.RespondPacket.operation = b"off"
                else:
                    self.RespondPacket.operation = b"Can not identify device"
                self.transport.write(self.RespondPacket.__serialize__())

            if isinstance(pkt, Respond):
                print("Server: Received a respond message!")
                if (pkt.respond == b"Succeeded!"):
                    print("Congratulations! Operation Succeeded!")
                elif (pkt.respond == b"Failed!"):
                    print("Error!")
                else:
                    print("Unknown Error!")

                #self.transport.write(self.RespondPacket.__serialize__())

    def connection_lost(self, exc):
        self.transport = None
        print("Server stopped!")

    def send(self, packet):
        packetBytes = packet.__serialize__()
        self.transport.write(packetBytes)



def BasicUnitTest():
    set_event_loop(TestLoopEx())
    client = IoTClientProtocol()
    server = IoTServerProtocol()
    transportToServer = MockTransportToProtocol(server)
    transportToClient = MockTransportToProtocol(client)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)
    packet_test = GetDeviceList()
    packet_test.category = "lamp"
    packet_test.number = 1001
    client.send(packet_test)


if __name__=="__main__":
    BasicUnitTest()







































