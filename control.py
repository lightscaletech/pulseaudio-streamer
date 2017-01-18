from xml.dom import minidom
import socket
import re
import xmltodict

class ControlRequest:
    FILE = "upnp/control.xml"
    def __init__(self, device, service):
        self.dom = minidom.parse(self.FILE)
        self.base_url = device.url_base
        s = device.get_service(service)
        self.service_type = service
        self.service_path = s.control_url
        self.service_url = self.base_url + self.service_path
        self.headers = {'Content-Type': 'text/xml; charset="utf-8"',
                        'SOAPAction': service,
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept':'*/*',
                        'User-Agent': 'UPnPstreamer/0.0.1',
                        'Connection': 'keep-alive'}

    def set_action(self, action):
        self.action = self.dom.createElementNS(self.service_type, 'u:' + action)
        self.action.setAttribute('xmlns:u', self.service_type)
        body = self.dom.getElementsByTagName("s:Body")[0]
        body.appendChild(self.action)

        self.headers['SOAPAction'] += '#' + action
        self.headers['SOAPAction'] = '"' + self.headers['SOAPAction'] + '"'

    def add_attribute(self, key, val):
        attr = self.dom.createElement(key)
        attr.appendChild(self.dom.createTextNode(val))
        self.action.appendChild(attr)

    def get_xml(self):
        return self.dom.toxml("utf-8")

    def get_host_port(self):
        r = re.match('([a-zA-Z0-9.]+):?([0-9]+)?', self.base_url)
        ip = r.group(1)
        port = r.group(2)
        return (ip, int(port))

class ControlResponse:
    raw_headers = None
    all_headers = None
    xml_body = None
    def  __init__(self, data):
        self.raw_response = data

    def headers_raw(self):
        if self.raw_headers == None:
            self.raw_headers = ''
            for l in self.raw_response:
                if l == '\r\n': break
                else: self.raw_headers += l
        return self.raw_headers

    def headers(self):
        if self.all_headers == None:
            lines = self.headers_raw().splitlines()
            hr = re.compile('([a-zA-Z\-\/0-9\.\ ]+):?(.+)?')
            sr = re.compile('HTTP\/\d\.\d (\d{3}) [A-Z]+')
            self.all_headers = {}
            for l in lines:
                res = hr.match(l)
                key = res.group(1)
                val = res.group(2)
                res = sr.match(key).group(1)
                if res == None: self.all_headers.update({key: val})
                else: self.status = res

        return self.all_headers

    def body(self):
        if self.xml_body == None:
            found_start = False
            data = ""
            for l in self.raw_response:
                if l == '\r\n': found_start = True
                if found_start: data += l
            self.xml_body = xmltodict.parse(data)
        return self.xml_body


def send_request(req):
    mes = req.get_xml().encode("utf-8")
    headers = req.headers
    headers.update({'Content-Length': len(mes)})

    sock = socket.socket()
    sock.connect(req.get_host_port())
    sock.send('POST %s HTTP/1.1\r\n' % req.service_path)
    for h, v in headers.items():
        sock.send('%s: %s\r\n' % (h, v))
    sock.send('\r\n')
    sock.send(mes)

    data = []
    for l in sock.makefile(): data.append(l)

    return ControlResponse(data)
