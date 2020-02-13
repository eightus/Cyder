from vfssh.vfs.Command import Command


class whoami(Command):
    def __init__(self, vfs=None):
        super().__init__('whoami')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        self.write(self.vfs.username + '\n')
        return None
