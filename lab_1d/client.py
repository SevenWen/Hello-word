import playground, asyncio
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER
from playground.network.devices.vnic import connect
from asyncio import *


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



class IoTClientProtocol(asyncio.Protocol):
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
                    self.ModifyDevice()
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

            if self.state == self.end:
                self.transport.close()
            elif self.state == self.ERROR:
                self.transport.close()



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
        print("IoT Client Connection Lost because {}".format(exc))


if __name__=='__main__':
    loop = get_event_loop()
    loop.set_debug(enabled=True)
    connect = playground.getConnector().create_playground_connection (lambda:IoTClientProtocol(), '20174.1.1.1', 5555)
    transport, client = loop.run_until_complete(connect)
    client.GetDeviceList()
    loop.run_forever()
    loop.close()