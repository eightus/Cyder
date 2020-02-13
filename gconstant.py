from vfssh.vfs.FileSystem import FileSystem
from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError
import pkgutil
import inspect
import logging.handlers
import configparser
import os
import subprocess
from scapy.all import conf
from Crypto.PublicKey import RSA


def logger_config(name, addr='127.0.0.1', port=514, method='rsyslog', path=None):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    if method == 'rsyslog':
        handler = logging.handlers.SysLogHandler((addr, port))
        formatter = logging.Formatter('%(message)s\n')
    else:
        if not path.endswith('/'):
            path += '/'
        handler = logging.FileHandler(path + name + '.json')
        formatter = logging.Formatter('%(message)s')

    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def get_plugins():
    global PLUGIN
    PLUGIN = dict()
    imported_package = __import__('vfssh.vfs.command', fromlist=[''])
    for _, plugin_name, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
        plugin_module = __import__(plugin_name, fromlist=[''])
        all_klass = inspect.getmembers(plugin_module, inspect.isclass)
        for _, cls in all_klass:
            if issubclass(cls, Command) & (cls is not Command):
                load = cls()
                PLUGIN[load.cmd] = load


def get_vfs():
    global VFS, HOST_MACHINE
    VFS = dict()
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/configuration/host_config.ini')
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/configuration/virtual_config.ini')
    for k, v in config.items():
        if k == 'CONFIGURATION' or k == 'DEFAULT':
            continue
        ip = config.get(k, 'ip', fallback=None)
        vfs = config.get(k, 'file_system', fallback=None)
        if ip is None:
            raise VFSError.Error('Configuration File Error')
        VFS[ip] = FileSystem(vfs)
    HOST_MACHINE = config.get('HOST', 'ip', fallback=None)


def get_credentials():
    global CREDENTIALS
    CREDENTIALS = list()
    with open(os.path.dirname(os.path.realpath(__file__)) + '/configuration/credentials.txt') as f:
        for line in f:
            line = line.strip()
            CREDENTIALS.append(line.split(':'))


def get_interface():
    global INTERFACE, SOCKET_INTERFACE
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/configuration/host_config.ini')
    iface_ = config.get('CONFIGURATION', 'interface', fallback='ens33')

    try:
        INTERFACE = iface_
        SOCKET_INTERFACE = conf.L3socket(iface=iface_)
    except OSError:
        print('NOPE')
        raise VFSError.Error('Interface Not Found')


def get_ssh_key():
    global VFS

    key_path = os.path.dirname(os.path.realpath(__file__)) + '/configuration/key'

    #  Key Folder
    if not os.path.exists(key_path):
        os.mkdir(key_path)

    for i in VFS.keys():
        if not os.path.exists(f'{key_path}/{i}'):
            os.mkdir(f'{key_path}/{i}')

        if os.path.exists(f'{key_path}/{i}/private.key') and os.path.exists(f'{key_path}/{i}/public.key'):
            continue
        key = RSA.generate(2048)
        with open(f'{key_path}/{i}/private.key', 'wb') as content_file:
            os.chmod(f'{key_path}/{i}/private.key', 0o600)
            content_file.write(key.exportKey('PEM'))
        with open(f'{key_path}/{i}/public.key', 'wb') as content_file:
            content_file.write(key.publickey().exportKey('OpenSSH'))


def start_tcpdump():
    global INTERFACE
    global TCPDUMP
    global LOG_LOCATION
    pcap_loc = os.path.join(LOG_LOCATION, 'pcap')
    if not os.path.exists(pcap_loc):
        os.mkdir(pcap_loc)
    file_path = os.path.join(pcap_loc, 'capture.pcap')
    command = f'tcpdump -i {INTERFACE} -C 100 -w {file_path}'
    TCPDUMP = subprocess.Popen(command, shell=True)


def log_location():
    global LOG_LOCATION
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/configuration/host_config.ini')
    log_path = config.get('CONFIGURATION', 'log_path', fallback='/var/log/cyder')
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    return log_path


if os.geteuid() != 0:
    print('You need to have root privileges to run Cyder')
    exit(0)

"""
Usage of "gconstant":
    - import gconstant as gc
    
***********************************************
Please do not use "from gconstant import xxx"
This will cause gconstant to be reloaded, and
the variables will be None
***********************************************

Dynamic/Static Global Constant Should Be Placed Below
"""


LOG_LOCATION = log_location()
LOG_CYDER = logger_config('cyder', method='local', path=LOG_LOCATION)
LOG_PACKET = logger_config('packet', method='local', path=LOG_LOCATION)
LOG_DEBUG = logger_config('debug', method='local', path=LOG_LOCATION)

INTERFACE = None
SOCKET_INTERFACE = None
TCPDUMP = None
HOST_MACHINE = None
VFS = None
CREDENTIALS = None
PLUGIN = None

get_interface()
start_tcpdump()
get_credentials()
get_plugins()
get_vfs()
get_ssh_key()
