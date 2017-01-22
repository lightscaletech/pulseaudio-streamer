from ssdp import SSDP
from connectionmanager import ConnectionManager
from avtransport import AVTransport
import logging
import device
import pulseaudio
import time
import fifowatcher
import socket
import errno
from threading import Event

s = SSDP()
stop_running = Event()

def find_devices():
    logging.debug("Searching for devices...")
    s.scan()
    devices = device.get_devices(s.responses)
    devices = device.filter_devices_by_service_type(devices, AVTransport.SERVICE)
    devices = device.filter_devices_by_service_type(devices, ConnectionManager.SERVICE)
    return devices

def cleanup():
    logging.debug('Cleaning up')
    pulseaudio.cleanup()
    #fifowatcher.cleanup()
    stop_running.set()

def main():
    stop_running.clear()
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        datefmt='%I:%M:%S',
                        level=logging.DEBUG)
    logging.info("Starting device discovery")
    try:
        while True:
            devices = find_devices()
            pulseaudio.manage_sinks(devices)
            fifowatcher.setup_watches(stop_running, pulseaudio.mods)
            if stop_running.wait(5): break
    except KeyboardInterrupt: cleanup()
    except socket.error as err:
        print (err.errno)
        cleanup()
        raise
    except:
        cleanup()
        raise

main()
