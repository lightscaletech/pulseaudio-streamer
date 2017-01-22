from xml.dom import minidom
import cgi

class UpnpContentFlags(object):
        SENDER_PACED = 80000000
        LSOP_TIME_BASED_SEEK_SUPPORTED = 40000000
        LSOP_BYTE_BASED_SEEK_SUPPORTED = 20000000
        PLAY_CONTAINER_SUPPORTED = 10000000
        S0_INCREASING_SUPPORTED = 8000000
        SN_INCREASING_SUPPORTED = 4000000
        RTSP_PAUSE_SUPPORTED = 2000000
        STREAMING_TRANSFER_MODE_SUPPORTED = 1000000
        INTERACTIVE_TRANSFER_MODE_SUPPORTED = 800000
        BACKGROUND_TRANSFER_MODE_SUPPORTED = 400000
        CONNECTION_STALLING_SUPPORTED = 200000
        DLNA_VERSION_15_SUPPORTED = 100000

        def __init__(self, flags=None):
            self.flags = flags or []

        def __str__(self):
            return (str(sum(self.flags)).zfill(8) + ('0' * 24))

class MetaData(object):
    FILE = "upnp/url_meta_data.xml"
    CONTENT_FLAGS = str(UpnpContentFlags([
        UpnpContentFlags.STREAMING_TRANSFER_MODE_SUPPORTED,
        UpnpContentFlags.BACKGROUND_TRANSFER_MODE_SUPPORTED,
        UpnpContentFlags.CONNECTION_STALLING_SUPPORTED,
        UpnpContentFlags.DLNA_VERSION_15_SUPPORTED]))
    CONTENT_FEATURE = "DLNA.ORG_OP=00;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=" + CONTENT_FLAGS

    def __init__(self):
        self.dom = minidom.parse(self.FILE)
        self.item = self.dom.getElementsByTagName('item')[0]

    def setItemPart(self, tag, val):
        el = self.item.getElementsByTagName(tag)[0]
        node = self.dom.createTextNode(val)
        el.appendChild(node)

    def setTitle(self, val): self.setItemPart("dc:title", val)
    def setCreator(self, val): self.setItemPart('dc:creator', val)
    def setArtist(self, val): self.setItemPart('upnp:artist', val)
    def setAlbum(self, val): self.setItemPart('upnp:album', val)
    def setAlbumArtURI(self, val): self.setItemPart('upnp:albumArtURI', val)
    def setRes(self, mimeType, val):
        protoInfoContent = 'http-get:*:%s:%s' % (mimeType, self.CONTENT_FEATURE)
        protoInfo = self.dom.createAttribute('protocolInfo')
        protoInfoText = self.dom.createTextNode(protoInfoContent)
        protoInfo.appendChild(protoInfoText)
        resText = self.dom.createTextNode(val)
        res = self.item.getElementsByTagName('res')[0]
        res.appendChild(resText)

    def xml(self): self.dom.toxml()
    def xml_encoded(self): cgi.escape(self.xml)
