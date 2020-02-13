from vfssh.vfs.FileSystem import FileSystem
from abc import abstractmethod, ABC
from vfssh.vfs.error import VFSError


class Command(ABC):
    def __init__(self, cmd):
        self.cmd = cmd
        self.channel = print
        self.vfs = None
        self.param_true = []
        self.param_false = []

    def run(self, **kwargs):
        """
        I'll slap you if you override this method
        """
        takeover = kwargs.get('takeover', None)
        default = ['full', 'cmd', 'args', 'obj']
        if takeover:
            self.takeover(**kwargs)
        elif all(elem in kwargs.keys() for elem in default):
            self.process(**kwargs)
        else:
            raise VFSError.Error('Parameters Not Found')

    @abstractmethod
    def process(self, full, cmd, args):
        pass

    def arg_check(self, args: list):
        skip = False
        out = dict()

        for i in range(len(args)):
            if skip:
                skip = False
                continue

            for x in args[i][1:]:
                if x in self.param_false:
                    out[x] = True
                else:
                    raise VFSError.InvalidArgument(msg=None, arg=x)

            if args[i][1:] in self.param_true:
                skip = True
                try:
                    out[args[i][1:]] = args[i+1]
                except IndexError:
                    raise VFSError.MissingParameter(arg=out[args[i][1:]])

        return out

    def takeover(self, **kwargs):
        pass

    def set_vfs(self, vfs):
        self.vfs = vfs

    def set_channel(self, channel):
        self.channel = channel

    def write(self, data):
        if data:
            self.channel(data)

    def write_bytes(self, data):
        self.channel(data.decode())

    def handle_ctrl_c(self):
        pass

    def handle_ctrl_d(self):
        pass


# a = Command('test')
# a.write_bytes(b'data')
