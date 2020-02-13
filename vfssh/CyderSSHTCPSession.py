from asyncssh import SSHTCPSession
import time
import json
import base64
import gconstant as gc


class CyderSSHTCPSession(SSHTCPSession):
    def __init__(self, client, host, port):
        self.host = host
        self.port = port
        self.client = client
        self._chan = None

    def connection_made(self, chan):
        self._chan = chan

    def data_received(self, data, datatype):
        #  Logs SSH Proxy
        parse_data = base64.encodebytes(data).decode('ascii')
        log_data = {"timestamp": time.time(), 'protocol': 'direct-tcp: {}'.format(self.port), 'data': parse_data,
                    'dst_ip': self.client.getsockname()[0], 'dst_port': self.client.getsockname()[1],
                    'src_ip': self.client.getpeername()[0], 'src_port': self.client.getpeername()[1]}
        gc.LOG_CYDER.info(json.dumps(log_data))
        self._chan.write_eof()
        self._chan.close()
        self._chan.abort()
