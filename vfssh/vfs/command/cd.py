from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError


class cd(Command):
    def __init__(self, vfs=None):
        super().__init__('cd')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        full, cmd, args = kwargs['full'], kwargs['cmd'], kwargs['args']

        if len(args) == 0:
            self.vfs.ch_dir(self.vfs.user_home)
            return
        elif len(args) > 1:
            self.write('bash: cd: too many arguments\n')
            return

        path = args[0]
        try:
            self.vfs.ch_dir(path)
        except VFSError.ObjNotFound:
            self.write('bash: cd: {}: No such file or directory\n'.format(path))
        except VFSError.ObjIsFile:
            self.write('bash: cd: {}: Not a directory\n'.format(path))

        return None
