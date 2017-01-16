import device
from ssdp import SSDP

s = SSDP()
s.scan()
device.get_devices(s.responses)

