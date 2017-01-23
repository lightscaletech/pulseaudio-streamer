import threading
import logging
import time
import server
import avtransport
import encoder
import pulseaudio

watchers = []

class Watch:
    def __init__(self, stop_running, m):
        logging.debug("Created watcher for: %s" % m['name'])

        self.stop_running = stop_running
        self.mod = m

        self.sinkwatch = pulseaudio.SinkWatcher(self.mod, self.stop_running)
        self.avtran = avtransport.AVTransport(self.mod['dev'])
        self.encoder = encoder.Encoder(self.mod)
        self.server = server.Server(self.encoder)

        self.thread = threading.Thread(target=self.watch)
        self.thread.start()

    def __del__(self):
        if not self.server.stop_streaming.wait(0):
            self.server.stop()
        self.sinkwatch.stop()

    def start_playback(self):
        self.avtran.stop()
        self.avtran.set_transport_url('http://%s:%i' % (self.server.ip, self.server.port))
        self.server.start()
        self.avtran.play()

    def stop_playback(self):
        self.avtran.stop()
        self.server.stop()

    def watch(self):
        logging.debug('Started watching: %s' % self.mod['name'])

        try:
            while True:
                logging.debug('Waiting for playback')
                self.sinkwatch.wait_till_play()

                self.start_playback()

                logging.debug('Waiting till stop')
                self.sinkwatch.wait_till_stop()

                self.stop_playback()
                logging.debug('Playback stopped')

                if self.stop_running.wait(1): break

            self.sinkwatch.stop()
        except pulseaudio.NotFound:
            logging.debug("Sink no longer exists")
            self.server.stop()

def setup_watches(stop_running, mods):
    for m in mods:
        found = False
        for w in watchers:
            if w.mod['id'] == m['id']:
                found = True
                break
        if not found: watchers.append(Watch(stop_running, m))
        else: found = False

    to_delete = []
    for index, w in enumerate(watchers):
        found = False
        for m in mods:
            if w.mod['id'] == m['id']:
                found = True
                break
        if not found: to_delete.append(index)
        else: found = True

    for i in to_delete: del watchers[i]

