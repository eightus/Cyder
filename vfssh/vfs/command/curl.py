from vfssh.vfs.Command import Command
from vfssh.vfs.error import VFSError
from vfssh.vfs.fs_object import FileObject
import requests


class curl(Command):
    def __init__(self, vfs=None):
        super().__init__('curl')
        self.set_vfs(vfs)

    def process(self, **kwargs):
        full, cmd, = kwargs['full'], kwargs['cmd']
        args = full[5:].split(' ')
        no_need_arg, require_arg = ['-O'], ['-o']
        skip, url, fmt_args = False, '', []
        for i in range(0, len(args)):
            if skip:
                skip = False
                continue
            if args[i] in require_arg:
                try:
                    fmt_args.append([args[i], args[i+1]])
                except IndexError:
                    fmt_args.append([args[i]])
                skip = True
            elif args[i] in no_need_arg:
                fmt_args.append([args[i]])
            else:
                url = args[i]

        for i in fmt_args:
            if any(elem in require_arg for elem in i):
                if len(i) == 1:
                    self.write('curl: option {}: requires parameter\n'.format(i[0]))
                    return

        if len(url) == 0:
            self.write('curl: no URL specified!\n')
            return

        if url.startswith('/'):
            self.write('curl: Remote file name has no length!\n')
            return

        #  -------------------------------------------------------------------------------------------------------------
        #  End of Conditions
        #  -------------------------------------------------------------------------------------------------------------

        #  TODO: VFS, HASH, Accepted
        if 'http://' not in url or 'https://' not in url:
            url = 'http://' + url

        try:
            opt = [i for i in fmt_args if '-o' in i][0]
            file_name = opt[1]
        except IndexError:
            file_name = url.split('/')[-1]

        #  Write The curl output as shown below
        """
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
          0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0

        """
        try:
            self.download(url, file_name)
        except requests.exceptions.ConnectionError:
            #  Do Some Fake Loop To Wait
            print('z')
            return
        except IsADirectoryError:
            self.write('Warning: Failed to create the file dd: Is a directory\n')
            self.write('curl: (23) Failed writing received data to disk/application\n')
            return

        head = self.vfs.head
        obj = FileObject(file_name, 'rwxrwxrwwx', head.loc + file_name)
        head.add_obj(obj)
        return None

    @staticmethod
    def download(url, file_name):
        with open(file_name, 'wb') as file:
            response = requests.get(url, verify=False, timeout=2)
            file.write(response.content)
