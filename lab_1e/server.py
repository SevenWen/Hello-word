import playground, asyncio
from playground.network.packet import PacketType
from asyncio import *
from packets import *
from passthrough import *


class IoTServerProtocol(asyncio.Protocol):
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
                    self.DeviceList()
                    self.state = self.wtmodifypkt

                else:
                    print("state error")
                    self.state = self.ERROR
            elif isinstance(pkt, ModifyDevice):
                if self.state == self.wtmodifypkt:
                    print("Server: Received a ModifyDevice request!")
                    self.RespondPacket = Respond()
                    self.RespondPacket.ID = pkt.ID
                    self.Respond()
                    self.state = self.end
                else:
                    self.state == self.ERROR
            else:
                print("received error packet")
                self.state = self.end

            if self.state == self.end:
                self.transport.close()
            elif self.state == self.ERROR:
                self.transport.close()


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







if __name__=='__main__':

    loop = get_event_loop()
    loop.set_debug(enabled=True)
   # coro = playground.getConnector().create_playground_server(lambda:IoTServerProtocol(),5555)
   # coro = playground.getConnector(‘passthrough’).create_playground_server(lambda:IoTServerProtocol(),5555)
    server= loop.run_until_complete(coro)
    loop.run_forever()
    server.close()
    loop.close()


