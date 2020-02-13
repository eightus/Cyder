from vfssh.vfs.Command import Command


class pwd(Command):
    def __init__(self, vfs=None):
        super().__init__('pwd')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        if self.vfs.pwd == '/':
            self.write(self.vfs.pwd + '\n')
        else:
            self.write(self.vfs.pwd[:-1] + '\n')
        return None
