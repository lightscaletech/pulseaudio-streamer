import sys
import socket
import errno
import re
import xmltodict
import logging
if sys.version_info >= (3, 0):
    from urllib import request
elif sys.version_info < (3, 0):
    import urllib as request

import urllib

class Service(object):
    def __init__(self, data):
        self.service_type = data['serviceType']
        self.service_id = data['serviceId']
        self.scpd_url = data['SCPDURL']
        self.control_url = data['controlURL']
        self.event_url = data['eventSubURL']

class Device(object):
    def __init__(self, url, data):
        doc = xmltodict.parse(data)
        device = doc['root']['device']
        service = device['serviceList']['service']

        self.friendly_name = device['friendlyName']
        self.manufacturer = device['manufacturer']
        self.model_name = device['modelName']
        self.model_description = device['modelDescription']
        self.url_base = url
        self.services = []

        if(type(service) is list):
            for s in service: self.services.append(Service(s))
        else: self.services.append(Service(service))

    def get_service(self, type):
        for s in self.services:
            if(s.service_type == type): return s
        return None

    def has_service(self, type):
        if(self.get_service(type) == None): return False
        else: return True

def get_base_url(path):
    m = re.match('https?\:\/\/([a-zA-Z0-9.:]+)\/', path)
    return m.group(1)

def get_device(res):
    url = res.location
    try:
        con = request.urlopen(url)
        return Device(get_base_url(url), con.read())

    except OSError as err: pass

def get_devices(resources):
    result = []
    for r in resources:
        dev = get_device(r)
        if dev: result.append(dev)
    return result

def filter_devices_by_service_type(devices, type):
    result = []
    for d in devices:
        if(d.has_service(type)): result.append(d)
    return result
