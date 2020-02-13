from vfssh.vfs.Command import Command


class clear(Command):
    def __init__(self, vfs=None):
        super().__init__('clear')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        #  Courtesy of Cowrie Honeypot
        self.write('[H[J')
        return None
