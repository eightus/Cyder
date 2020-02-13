from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError


class cat(Command):
    def __init__(self, vfs=None):
        super().__init__('cat')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        full, cmd, args = kwargs['full'], kwargs['cmd'], kwargs['args']
        if len(args) == 0:
            return None
        try:
            obj = self.vfs.get_obj(args[0], get='file')
            self.write(obj.data + '\n')
        except VFSError.ObjIsDirectory:
            self.write(f'cat: {args[0]} Is a directory\n')
        except VFSError.ObjNotFound:
            self.write(f'cat: {args[0]}: No such file or directory\n')
        return None
