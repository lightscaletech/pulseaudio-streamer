import urllib
import re
from xml.etree import ElementTree

class Device(object):
    def __init__(self, data):
        tree = ElementTree.ElementTree(ElementTree.fromstring(data))
        self.doc = tree.getroot()
        self.ns = {'ns': self.get_xml_namespace()}
        print(self.xpath_get_first("./ns:friendlyName"))

    def get_xml_namespace(self):
        m = re.match('\{(.*)\}', self.doc.tag)
        return m.group(1) if m else ''

    def xpath_get_first(self, path):
        res = self.doc.findall(path, namespaces=self.ns)
        if(len(res) > 0):
            res[0].text
        else:
            ''

def get_device(res):
    url = res.location
    con = urllib.urlopen(url)
    return Device(con.read())

def get_devices(resources):
    result = []
    for r in resources:
        result.append(get_device(r))

    return result
