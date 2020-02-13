from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError
from vfssh.vfs.Observer import Event
import os
import configparser


class ssh(Command):
    def __init__(self, vfs=None):
        super().__init__('ssh')
        self.set_vfs(vfs)
        self.config = None
        self.use_config()

    def use_config(self):
        self.config = []
        file = os.path.dirname(os.path.realpath(__name__)) + '/sub.ini'
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(file)
        for sec in cfg.sections():
            name = sec
            ip = cfg.get(sec, 'ip', raw=True, fallback=None)
            mac = cfg.get(sec, 'mac', raw=True, fallback=None)
            service = []
            for key in cfg[sec]:
                try:
                    service.append(int(key))
                except ValueError:
                    pass
            self.config.append({'name': name, 'ip': ip, 'mac': mac, 'service': service})

    def process(self, **kwargs):
        full, cmd, args, obj = kwargs['full'], kwargs['cmd'], kwargs['args'], kwargs['obj']
        try:
            obj.set_vfs('192.168.1.2')
        except VFSError.VFSNotFound:
            pass
        #  TODO: Finish up SSH Process

        obj.takeover = 'ssh'
        return None

    def takeover(self, **kwargs):
        pass
