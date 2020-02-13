from vfssh.vfs.Command import Command


class exit(Command):
    def __init__(self, vfs=None):
        super().__init__('exit')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        obj = kwargs['obj']
        obj.exit_status = True
        return
