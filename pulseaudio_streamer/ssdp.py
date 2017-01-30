import socket
import sys
import logging

if sys.version_info >= (3, 0):
    import http.client as httplib
    from io import BytesIO as StringIO
elif sys.version_info < (3, 0):
    import httplib
    from StringIO import StringIO


from pulseaudio_streamer import device
from pulseaudio_streamer.avtransport import AVTransport
from pulseaudio_streamer.connectionmanager import ConnectionManager

class SSDP:
    HOST = ("239.255.255.250", 1900)
    MX = 2
    message = '\r\n'.join(
        ['M-SEARCH * HTTP/1.1',
         'HOST: {0}:{1}',
         'MAN: "ssdp:discover"',
         'ST: {st}',
         'MX: {mx}',
         '',''])
    responses = []

    def __init__(self, service = "upnp:rootdevice"):
      self.service = service
      self.message = self.message.format(*self.HOST,
                                         st=service,
                                         mx=self.MX).encode('latin-1')

    def receive(self, sock):
        res = SSDP_Response(sock.recv(2048))
        self.responses.append(res)

    def scan(self):
        logging.debug("Searching for devices...")
        self.responses = []
        socket.setdefaulttimeout(3)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(self.message, self.HOST)

        while True:
            try:self.receive(sock)
            except socket.timeout as to: break

        sock.close()

class SSDP_Response(object):
    class _StringSock(StringIO):
        def makefile(self, *arg, **kw):
            return self

    def __init__(self, data):
        res = httplib.HTTPResponse(self._StringSock(data))
        res.begin()
        self.location = res.getheader('LOCATION')
        self.usn = res.getheader('USN')
        self.st = res.getheader('ST')

    def __str__(self):
        return ("SSDP_Response: location: %s, usn: %s, st: %s" %
                (self.location, self.usn, self.st))

s = SSDP()

def find_devices():
    s.scan()
    devices = device.get_devices(s.responses)
    devices = device.filter_devices_by_service_type(devices, AVTransport.SERVICE)
    devices = device.filter_devices_by_service_type(devices, ConnectionManager.SERVICE)
    return devices
