import control

class ConnectionManager:

    SERVICE = "urn:schemas-upnp-org:service:ConnectionManager:1"

    def __init__(self, dev):
        self.device = dev

    def create_req(self):
        return control.ControlRequest(self.device, self.SERVICE)

    def get_protocol_info(self):
        req = self.create_req()
        req.set_action('GetProtocolInfo')
        return control.send_request(req)

    def prepare_for_connection(self):
        req = self.create_req()


    def connection_complete(self):
        req = self.create_req()

