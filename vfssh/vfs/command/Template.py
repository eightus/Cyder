from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError

"""
In order to create a plugin, create a class that extends Command.
the class 'Command' is required for all plugins.
After plugin is written, drop the file inside the ./vfs/command folder
"""


class Template(Command):
    """
    Functions:
        - process(self, **kwargs)
            - Abstract Method (Required)
        - write(self, data: str)
            - Write str to terminal
        - write_bytes(self, data: bytes)
            - Convert and write bytes to terminal
    Parameters:
        - self.cmd
            - Command to trigger plugin
        - self.vfs
            - Current Virtual File System
        - self.channel
            - The Channel that's in SSHSession
    """
    def __init__(self, vfs=None):
        """
        :param vfs: The Virtual File System To Use
        :param args: This is the command the user will type into the terminal to trigger this plugin
            - e.g. super().__init__('pwd')
        """
        super().__init__('Template')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        """
        On triggering the plugin, the process function will be called to do processing of comman
        :param kwargs: Dictionary containing 4 arguments passed by the session

        - kwargs['full']    => The entire string sent by the user
        - kwargs['cmd']     => The command used by the user
        - kwargs['args']    => The arguments set by the user (default split with shlex)
        - kwargs['obj']     => The SSHSession object

        ----------------------------------------------------------------------------------------------------------------

        kwargs['full']
            - Developer can process the kwargs['full'] to split instead of using the default kwargs['args']

        kwargs['cmd']
            - No plans for this right now. It's just the command. e.g. (cd) (ssh) (pwd)

        kwargs['args']
            - Arguments from user input. This is just a list that doesn't contain the kwargs['cmd']

        kwargs['obj']
            - Not recommended to use unless necessary
            - This is used for more advance plugins.
                - Turn off echoing
                - Takeover the shell
                - Changing Virtual File System

        :return: Not really needed to return anything. Just here for fun!

        Sample code is shown below
        """
        full, cmd, args, obj = kwargs['full'], kwargs['cmd'], kwargs['args'], kwargs['obj']

        self.write('#'*50 + '\n')
        self.write('Do remember to include NEW LINE after each write\n')
        self.write_bytes(b'You can write in bytes too!\n')

        #  Using the Virtual File System (VFS)
        self.write('VFS Username: {}\n'.format(self.vfs.username))
        self.write('VFS Hostname: {}\n'.format(self.vfs.hostname))
        self.write('VFS Present Working Directory: {}\n'.format(self.vfs.pwd))
        fobj = self.vfs.get_obj('/home/root')
        self.write('VFS List Directory (name): {}\n'.format(fobj.list_obj('name')))
        self.write('VFS List Directory (attribute): {}\n'.format(fobj.list_obj('attribute')))
        self.write('VFS List Directory (list) (dict) returns everything in its format\n')
        self.write('VFS List Directory (default) returns the obj in a list\n')
        self.write('For more VFS related, read the documentation\n')

        #  Colors
        self.write('Colors and Formatting Worked Too!: \x1b[95m\x1b[5mBlink Blink\x1b[0m\n')
        self.write('\x1b[31mRed\x1b[0m\n')
        self.write('\x1b[32mGreen\x1b[0m\n')
        self.write('\x1b[34mBlue\x1b[0m\n')
        self.write('\x1b[43mBackground Yellow\x1b[0m\n')
        self.write('For more Formatting related, read the documentation\n')

        #  Oh! You can exit from here too!
        self.write('\x1b[96mDid I mention you can force exit straight from terminal?\x1b[0m\n')
        self.write('\x1b[31mG\x1b[32mo\x1b[33mo\x1b[34md\x1b[35mB\x1b[36my\x1b[37me\n')
        self.write('#'*50 + '\n')
        obj.exit_status = True

        return None
