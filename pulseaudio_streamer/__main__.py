import logging
import time
import socket
import errno
from threading import Event
import argparse

from pulseaudio_streamer import ssdp
from pulseaudio_streamer.connectionmanager import ConnectionManager
from pulseaudio_streamer.avtransport import AVTransport
from pulseaudio_streamer import fifowatcher
from pulseaudio_streamer import pulseaudio

stop_running = Event()

def cleanup():
    logging.debug('Cleaning up')
    pulseaudio.cleanup()
    #fifowatcher.cleanup()
    stop_running.set()

def parseArgs():
    parser = argparse.ArgumentParser(
        description="Steam audio from pulseaudio to upnp devices")

    parser.add_argument('-v', '--verbose', help='Increase output verbosity',
                        action="store_true")
    return parser.parse_args()

def main(args=None):
    args = parseArgs()

    loglev = logging.INFO
    if args.verbose: loglev = logging.DEBUG

    stop_running.clear()
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        datefmt='%I:%M:%S',
                        level=loglev)
    logging.info("Starting device discovery")
    try:
        while True:
            devices = ssdp.find_devices()
            pulseaudio.manage_sinks(devices)
            fifowatcher.setup_watches(stop_running, pulseaudio.mods)
            if stop_running.wait(5): break
    except KeyboardInterrupt: cleanup()
    except socket.error as err:
        cleanup()
        raise
    except:
        cleanup()
        raise

main()
