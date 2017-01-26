import subprocess
import threading
import logging
import re

cmd = "/usr/bin/pactl "
mods = []

def make_name(desc):
    return re.sub(r'([^\_\w])+', '', desc)

def create_sink(dev):
    desc = dev.friendly_name
    name = make_name(desc)
    logging.info("Creating sink: %s" % name)
    ld = "load-module module-null-sink "
    sink_name = 'sink_name="%s" ' % name
    sink_desc = 'sink_properties=device.description="%s" ' % desc.replace(' ', '_')
    command = cmd + ld + sink_name + sink_desc
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate(None)
    mid = int(out)
    mods.append({'id': mid, 'name': name, 'dev': dev})
    return mid

def remove_sink(mod, from_list = True):
    logging.info("Removing sink: %s" % mod['name'])
    ld = "unload-module "
    command = cmd + ld + str(mod['id'])
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate(None)
    if from_list: mods.remove(mod)

def remove_sink_by_id(sid):
    for m in mods:
        if sid == m['id']: return remove_sink(m)

def remove_sink_by_name(desc):
    name = make_name(desc)
    for m in mods:
        if m['name'] == name: return remove_sink(m)

def remove_all_sinks():
    for m in mods:
        remove_sink(m, False)
    del mods[:]

def cleanup(): remove_all_sinks()

def new_devices(devices):
    # Add new devices
    for dev in devices:
        found = False
        for mod in mods:
            if mod['name'] == make_name(dev.friendly_name):
                found = True
                break
        if found == False: create_sink(dev)
        else: found = False

def old_devices(devices):
    # Remove old devices
    to_remove = []
    for mod in mods:
        found = False
        for dev in devices:
            if mod['name'] == make_name(dev.friendly_name):
                found = True
                break
        if found == False:
            remove_sink(mod, False)
            to_remove.append(mod)
        else: found == False

    for mod in to_remove: mods.remove(mod)

def manage_sinks(devices):
    old_devices(devices)
    new_devices(devices)

class NotFound(Exception):
    def __init__(self):
        self.value = "Sink not found"

class SinkWatcher:
    STATE_RUNNING = 'RUNNING'
    STATE_STOPPED = 'IDLE'

    def __init__(self, mod, app_stop):
        self.mod = mod
        self.app_stop = app_stop
        self.stop_watcher = threading.Event()
        self.started = threading.Event()
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.watch)
        self.thread.start()
        self.exception = None

    def wait_till_play(self):
        self.started.wait()
        if self.exception: raise self.exception

    def wait_till_stop(self):
        self.stopped.wait()
        if self.exception: raise self.exception

    def release(self):
        self.started.set()
        self.stopped.set()
        self.stop_watcher.set()

    def stop(self):
        self.release()
        self.thread.join()

    def set_started(self):
        self.stopped.clear()
        self.started.set()

    def set_stopped(self):
        self.started.clear()
        self.stopped.set()

    def get_state(self):
        com = ['/usr/bin/pactl', 'list', 'sinks', 'short']
        proc = subprocess.Popen(com,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        lines = out.splitlines()
        res = {}
        for l in lines:
            sp = re.split('\t+', l)
            if sp[1] == self.mod['name']:
                res = {'id': int(sp[0]), 'name': sp[1], 'module': sp[2],
                       'format':sp[3], 'state': sp[4]}
                return res

        return NotFound()

    def watch(self):
        while True:
            try:
                sink = self.get_state()
            except:
                logging.debug('Error getting state of sink')
            if type(sink) is NotFound:
                self.exception = sink
                self.release()
            else:
                try:
                    if sink['state'] == self.STATE_RUNNING: self.set_started()
                    if sink['state'] == self.STATE_STOPPED: self.set_stopped()
                except:
                    self.exception = NotFound()
                    self.release()

            if self.app_stop.wait(0): return self.release()
            if self.stop_watcher.wait(1): return
