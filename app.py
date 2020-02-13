from Tunnel.packetBackUp import startIntercept
from Tunnel.VirtualDevice import addNewDevice
import configparser
from xeger import Xeger
import logging.handlers
import os
from vfssh.CyderSSHServer import start_ssh_server
from connection.server_telnet import start_telnet_server
from connection.server_http import start_http_server
from multiprocessing import Process
import gconstant as gc


def main():
    #  Configparser to read configurations
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/configuration/host_config.ini')
    print("Starting Program...")

    debug = logging.getLogger('cyder-debug')

    if config.getboolean('CONFIGURATION', 'debug', fallback=False):
        debug.debug('#'*50)
        debug.debug('Starting Program...')

    #  Get Host Machine IP & MAC Address
    ip, mac_addr = config.get('HOST', 'ip', fallback=None), config.get('HOST', 'mac_address', fallback=None)
    if ip is None:
        return

    #  Services (Specified in Configuration File)
    services = dict()
    for key in config['HOST']:
        try:
            services[int(key)] = process(config['HOST'][key])
        except ValueError:
            pass

    #  SSH Server (AsyncSSH)
    if config.getboolean('HOST', 'ssh', fallback=False):
        print('SSH Enabled')
        start_service(services[22].strip(), 22, '0.0.0.0', start_ssh_server)
        del services[22]

    #  Telnet Server (Twisted)
    if config.getboolean('HOST', 'telnet', fallback=False):
        print('Telnet Enabled')
        start_service(services[23], 23, '0.0.0.0', start_telnet_server)
        del services[23]

    #  HTTP Server (Waitress)
    if config.getboolean('HOST', 'http', fallback=False):
        print('HTTP Enabled')
        start_service(services[80].strip(), 80, '0.0.0.0', start_http_server)
        del services[80]

    #  Port 2323
    start_service(services[2323], 2323, '0.0.0.0', start_telnet_server)
    del services[2323]

    #  Add Device To Subnet
    addNewDevice(name='HOST', services=services, fingerprint=config.get('HOST', 'fingerprint'),
                 ip=ip, mac_addr=mac_addr)
    # addNewDevice(name='Test', services=service, fingerprint=host['fingerprint'], ip='192.168.1.1', macAddr=mac_addr)

    print('Done Loading...')
    debug.debug('Done Loading...')
    startIntercept()


def start_service(banner, port, host, target):
    #  Function to run SSH / Telnet / HTTP in multiprocess
    mp = Process(target=target, args=(host, port, banner,))
    mp.daemon = True
    mp.start()


def process(data, limit=10, increment=100):
    #  Process Regex - Increment 150 ~ 7.9 seconds
    try:
        x = Xeger(limit)
        val = x.xeger(data)
    except ValueError:
        val = process(data, limit+increment, increment)
    return val


if __name__ == "__main__":
    main()


