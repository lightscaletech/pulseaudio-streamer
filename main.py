import device
from ssdp import SSDP

desired_service = "urn:schemas-upnp-org:service:AVTransport:1"

s = SSDP()
s.scan()
devices = device.filter_devices_by_service_type(
    device.get_devices(s.responses), desired_service)

for d in devices:
    print(d.friendly_name)

