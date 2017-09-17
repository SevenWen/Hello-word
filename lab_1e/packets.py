from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER
from playground.network.packet import PacketType

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