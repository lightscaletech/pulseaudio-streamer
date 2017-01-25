from pulseaudio import control
import metadata

class AVTransport:

    SERVICE = "urn:schemas-upnp-org:service:AVTransport:1"

    instance_id = '0'
    def __init__(self, dev):
        self.device = dev

    def create_req(self):
        return control.ControlRequest(self.device, self.SERVICE)

    def set_transport_url(self, url):
        md = metadata.MetaData()
        md.setTitle('UPnP Stream')
        md.setCreator('')
        md.setAlbum('')
        md.setAlbumArtURI('')
        md.setArtist('')
        md.setRes('audio/mp3', url)

        req = self.create_req()
        req.set_action('SetAVTransportURI')
        req.add_attribute('InstanceID', self.instance_id)
        req.add_attribute('CurrentURI', url)
        req.add_attribute('CurrentURIMetaData', '')
        return control.send_request(req)

    def get_transport_info(self):
        req = self.create_req()
        req.set_action('GetTransportInfo')
        req.add_attribute('InstanceID', self.instance_id)
        return control.send_request(req)

    def play(self, just_send = False):
        req = self.create_req()
        req.set_action('Play')
        req.add_attribute('InstanceID', self.instance_id)
        req.add_attribute('Speed', '1')
        return control.send_request(req, just_send)

    def stop(self):
        req = self.create_req()
        req.set_action('Stop')
        req.add_attribute('InstanceID', self.instance_id)

