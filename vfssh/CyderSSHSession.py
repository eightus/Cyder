import asyncssh
import shlex
import time
import json
from gconstant import VFS, PLUGIN
from vfssh.vfs.error import VFSError
import gconstant as gc


class CyderSSHSession(asyncssh.SSHServerSession):

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.command = PLUGIN.copy()
        self._input = ''
        self._total = 0
        self._chan = None
        self.exit_status = False
        self.vfs = gc.VFS[gc.HOST_MACHINE]
        self.takeover = None
        self.remote_exc = {'status': False, 'cmd': ''}

    def set_vfs(self, ip):
        vfs = VFS.get(ip)
        if vfs is None:
            raise VFSError.VFSNotFound
        else:
            self.vfs = vfs
            for v in self.command.values():
                v.set_vfs(self.vfs)
        return True

    def connection_made(self, chan):
        self._chan = chan

    def exec_requested(self, command):
        self.remote_exc['status'] = True
        self.remote_exc['cmd'] = command
        return True

    def session_started(self):
        #  TODO: Use Try/Except Type Error to load plugin only when used.
        for v in self.command.values():
            v.set_vfs(self.vfs)
            v.set_channel(self._chan.write)
        try:
            self._chan.register_key('\x1a', self.key_ctrlz)
        except AttributeError:
            pass

        if self.remote_exc['status']:
            self.data_received(self.remote_exc['cmd'], None)
            self.soft_eof_received()
            return
        self._chan.write(self.vfs.prompt())

    def shell_requested(self):
        return True

    def signal_received(self, signal):
        if signal == 'CtrlZ':
            self.soft_eof_received()

    def data_received(self, data, datatype):
        log_data = {'timestamp': time.time(), 'protocol': 'SSH', 'command': data,
                    'dst_ip': self.client.getsockname()[0], 'dst_port': self.client.getsockname()[1],
                    'src_ip': self.client.getpeername()[0], 'src_port': self.client.getpeername()[1]}
        gc.LOG_CYDER.info(json.dumps(log_data))
        if self.takeover:
            self.command[self.takeover].run(full=data.strip(), obj=self, takeover=True)
            return

        user_input = list(shlex.shlex(data.strip(), posix=True, punctuation_chars=True))

        if len(user_input) == 0:
            #  No Input From User
            self._chan.write(self.vfs.prompt())
            return

        if ';' in user_input or '&&' in user_input:
            #  TODO: For Loop run multiple command
            return

        cmd = user_input[0]
        if cmd in self.command:
            args = user_input[1:]
            self.command[cmd].run(full=data.strip(), cmd=cmd, args=args, obj=self)
        else:
            self._chan.write('{}: command not found\n'.format(data.strip()))

        if self.exit_status:
            self._chan.exit(0)
            return

        if self.remote_exc['status']:
            return

        self._chan.write(self.vfs.prompt())
        return

    def eof_received(self):
        gc.LOG_DEBUG.debug('EOF Received')
        self._chan.exit(0)

    def break_received(self, msec):
        gc.LOG_DEBUG.debug('Break Received: {}'.format(msec))
        self.eof_received()

    def soft_eof_received(self):
        gc.LOG_DEBUG.debug('Soft Exit Detected')
        self._chan.exit(0)

    def key_ctrlz(self, line, pos):
        return self.signal_received('CtrlZ'), 0