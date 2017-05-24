import os
import socket
import struct
import fcntl

LOCALHOST_IP = '127.0.0.1'

def getAllInterfaces():
    return os.listdir('/sys/class/net/')

def getInterfaceIp(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def isLocal(ip):
    return ip == LOCALHOST_IP

def getFistLanIp():
    ints = getAllInterfaces()
    ips = []

    try: ints.remove('lo')
    except ValueError: pass

    for i in ints:
        try:
            ip = getInterfaceIp(i.encode())
        except OSError: continue
        if isLocal(ip): continue
        ips.append(ip)

    return ips[0] if ips else None
