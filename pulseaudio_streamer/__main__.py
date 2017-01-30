import logging
import device
import time
import socket
import errno
from threading import Event

import ssdp
from connectionmanager import ConnectionManager
from avtransport import AVTransport
import fifowatcher
import pulseaudio

stop_running = Event()

def cleanup():
    logging.debug('Cleaning up')
    pulseaudio.cleanup()
    #fifowatcher.cleanup()
    stop_running.set()

def main(args=None):
    stop_running.clear()
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        datefmt='%I:%M:%S',
                        level=logging.INFO)
    logging.info("Starting device discovery")
    try:
        while True:
            devices = ssdp.find_devices()
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
