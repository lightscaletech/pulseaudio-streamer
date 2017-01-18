import control

class AVTransport:

    SERVICE = "urn:schemas-upnp-org:service:AVTransport:1"

    def __init__(self, dev):
        self.device = dev

    def create_req(self):
        return control.ControlRequest(self.device, self.SERVICE)

    def set_transport_url(self, url):
        req = self.create_req()
        req.set_action('SetAVTransportURI')
        req.add_attribute('InstanceID', '0')
        req.add_attribute('CurrentURI', url)
        return control.send_request(req)
