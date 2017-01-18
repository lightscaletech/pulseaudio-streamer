import device
from ssdp import SSDP
from connectionmanager import ConnectionManager
from avtransport import AVTransport
from server import Server

server = Server()
server.start()

s = SSDP()
s.scan()
devices = device.get_devices(s.responses)
devices = device.filter_devices_by_service_type(devices, AVTransport.SERVICE)
devices = device.filter_devices_by_service_type(devices, ConnectionManager.SERVICE)

dev = None
for d in devices:
    if(d.friendly_name == "HiFiPI"): dev = d

tran = AVTransport(dev)
conn = ConnectionManager(dev)
print(conn.get_protocol_info().body()['s:Envelope']['s:Body'])
#print(tran.set_transport_url("http://192.168.1.104/"))
server.wait()
