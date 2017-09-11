'''This is a simple IoT(Internet of Things) control protocol.
The ID of a device is unique.
When a client wants to turn on or turn off a device, it will send a packet to the server.
And the server will respond to the client whether the operation is successful.

1. A client sends a request packet to the server for devices list.
* client sends GetDeviceList() or GetDeviceList(type of device) to the server

2. The server will send a device list to client. The list contains four different kinds of information, device ID, device name, device category and device status.
* server sends DeviceList(ID, name, category, status) to the client

3. The client now can control devices by sending a control message.
* client sends ModifyDevice(ID or name or category, turn on or turn off) to the client

4. The server will respond to client whether the operation is successful.
* server sends Respond(yes or no) to the client'''
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER


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
        ("object", UINT32),
        ("operation", BUFFER)
    ]

class Respond(PacketType):
    DEFINITION_IDENTIFIER = "lab2b.zli.respond"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("respond", UINT32)
    ]

def UnitTest():
    # Test GetDeviceList() Packet
    packet1 = GetDeviceList()
    packet1.category = "lamp"
    packet1.number = 1
    try:
        packet1Byte = packet1.__serialize__()
        print("Packet1 serialize succeeded!")
    except:
        print("Packet1 serialize failed!")
    try:
        packet1a = GetDeviceList.Deserialize(packet1Byte)
        assert packet1a == packet1
        print("Packet1 deserialize succeeded!")
    except:
        print("Packet1 deserialize failed!")

    #Test DeviceList() Packet
    packet2 = DeviceList()
    packet2.ID = 1001
    packet2.name = b"table lamp"
    packet2.category = "lamp"
    packet2.status = b"on"
    try:
        packet2Byte = packet2.__serialize__()
        print("Packet2 serialize succeeded!")
    except:
        print("Packet2 serialize failed!")
    try:
        packet2a = DeviceList.Deserialize(packet2Byte)
        assert packet2a == packet2
        print("Packet2 deserialize succeeded!")
    except:
        print("Packet2 deserialize failed!")

    #Test ModifyDevice() Packet
    packet3 = ModifyDevice()
    packet3.object = 1001
    packet3.operation = b"off"
    try:
        packet3Byte = packet3.__serialize__()
        print("Packet3 serialize succeeded!")
    except:
        print("Packet3 serialize failed!")
    try:
        packet3a = ModifyDevice.Deserialize(packet3Byte)
        assert packet3a == packet3
        print("Packet3 deserialize succeeded!")
    except:
        print("Packet3 deserialize failed!")

    #Test Respond() Packet
    packet4 = Respond()
    packet4.respond = 1001
    try:
        packet4Byte = packet4.__serialize__()
        print("Packet4 serialize succeeded!")
    except:
        print("Packet4 serialize failed!")
    try:
        packet4a = Respond.Deserialize(packet4Byte)
        assert packet4a == packet4
        print("Packet4 deserialize succeeded!")
    except:
        print("Packet4 deserialize failed!")

    packetBytes = packet4Byte + packet3Byte + packet2Byte + packet1Byte
    deserializer = PacketType.Deserializer()
    while len(packetBytes) > 0:
        chunk, packetBytes = packetBytes[:16], packetBytes[16:]
        deserializer.update(chunk)
        print("Another 16 bytes loaded into deserializer.Left = {}".format(len(packetBytes)))
        for packet in deserializer.nextPackets():
            print("got a packet!")
            if packet == packet1:
                print("It’s packet1!")
            elif packet == packet2:
                print("It’s packet 2!")
            elif packet == packet3:
                print("It’s packet 3!")
            elif packet == packet4:
                print("It’s packet 4!")




if __name__=="__main__":

     UnitTest()

