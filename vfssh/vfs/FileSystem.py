from vfssh.vfs.fs_directory import FolderObject
from vfssh.vfs.fs_object import FileObject
from vfssh.vfs.error import VFSError
import time
import json
import re


class FileSystem:
    def __init__(self, fs_file=None, head=None):
        self.username = 'root'
        self.hostname = 'server'
        self.user_home = '/home/' + self.username + '/'
        self.pwd = self.user_home
        self.head = head
        self.output = 'root@server:~$ '
        self.system = FolderObject('', 'drwxrwxrwx', '/', [], timestamp=time.time(), owner=self.username)
        self.old_pwd = None
        self.fs_file = fs_file
        self.load_filesystem()

    def load_filesystem(self):
        fs = self.fs_file if self.fs_file else 'configuration/fs/default_fs.json'
        f = open(fs, 'r')
        for struct in f:
            struct = json.loads(struct)
            v_path = struct['virtual_path']
            s = v_path.split('/')[1:-1] if v_path.endswith('/') else v_path.split('/')[1:]
            counter = [v for v in range(len(s))]
            for i in counter:
                loc = '/' + '/'.join(s[:i+1])
                if i == counter[-1]:
                    if struct['data_type'] == 'path':
                        obj = FileObject(s[i], struct['attributes'], loc, data=struct['path'],
                                         memory=struct.get('save_on_memory', False),
                                         timestamp=struct.get('timestamp', time.time()),
                                         owner=struct.get('owner', self.username),
                                         size=struct.get('custom_size', False))
                    elif struct['data_type'] == 'string':
                        obj = FileObject(s[i], struct['attributes'], loc, data=struct['data'],
                                         memory=None, timestamp=struct.get('timestamp', time.time()),
                                         owner=struct.get('owner', self.username),
                                         size=struct.get('custom_size', False))

                    elif struct['data_type'] == 'folder':
                        obj = FolderObject(s[i], struct['attributes'], loc + '/',
                                           timestamp=struct.get('timestamp', time.time()),
                                           owner=struct.get('owner', self.username))
                    else:
                        raise VFSError.Error('File System Configuration Error')
                else:
                    obj = FolderObject(s[i], struct['attributes'], loc + '/',
                                       timestamp=struct.get('timestamp', time.time()),
                                       owner=struct.get('owner', self.username))

                if i == 0:
                    try:
                        self.system.add_obj(obj)
                    except VFSError.ObjExist:
                        continue
                txt = 'get_obj(s[{}]).' * i
                cmd = ('self.system.' + txt.format(*counter)) + 'add_obj(obj)'
                try:
                    eval(cmd)
                except VFSError.ObjExist:
                    pass
        self.head = self.head if self.head else self.get_obj('/home/root')
        f.close()

    def get(self, path):
        #  Condition 1
        if path == '/':
            return self.system

        #  Condition 2
        if path.startswith('/'):
            s = path.split('/')[1:-1] if path.endswith('/') else path.split('/')[1:]
        else:
            path = self.pwd + path
            s = path.split('/')[1:-1] if path.endswith('/') else path.split('/')[1:]

        txt = (('get_obj(s[{}]).' * len(s)).format(*[v for v in range(len(s))]))[:-1]
        try:
            obj = eval('self.system.' + txt)
        except AttributeError:
            #  File/Folder Does Not Exist
            raise VFSError.ObjNotFound(path)
        return obj

    def ch_dir(self, path):
        cond = self.parse_input(path)
        self.head = cond
        self.pwd = cond.loc
        self.output = self.parse_output(self.pwd)
        return True

    def get_obj(self, path, get='directory'):
        obj = self.parse_input(path, get)
        return obj

    def parse_input(self, path: str, get='directory'):
        loc = ''
        alter = path.strip()
        if path.strip() == '-':
            return self.old_pwd if self.old_pwd else False

        if path.strip().startswith('~') or path.strip().startswith('~/'):
            alter = alter.replace('~', '', 1)
            loc += self.user_home

        if './' in path.strip() and not path.strip().startswith('./'):
            alter = alter.replace('./', '/')

        if path.strip().startswith('.') and not path.strip().startswith('..'):
            try:
                if path.strip()[1].isalpha():
                    pass
            except IndexError:
                alter = alter[1:]
                loc += self.pwd

        if '../' in path.strip() and not path.strip().startswith('..'):
            #  TODO: Implementing directory traversal '..'
            pass

        if path.strip().startswith('..'):
            pos = self.pwd[:-1].split('/')
            del pos[-1]
            pos = '/'.join(pos) + '/'
            alter = alter.replace('..', '')
            loc += pos

        loc += alter
        loc = re.sub('/{2,}', '/', loc)

        #  Check File Existent
        obj = self.get(loc)
        #  Check if Type(File) or Type(Folder)

        if type(obj) == FileObject and get == 'directory':
            raise VFSError.ObjIsFile
        elif type(obj) == FolderObject and get == 'file':
            raise VFSError.ObjIsDirectory
        else:
            return obj

        #  Haven't do '..' (Reverse Directory) and Check File Exist

    def parse_output(self, path: str):
        output = self.username + '@' + self.hostname + ':'
        alter = path

        if path == '/':
            self.output = output
            return output + '/$ '

        if alter.endswith('/'):
            pass
        else:
            alter = alter + '/'

        if alter.startswith(self.user_home):
            output += '~'
            alter = alter.replace(self.user_home, '/')

        if alter.endswith('/'):
            alter = alter[:-1]
        output += alter + '$ '
        self.output = output
        return output

    def prompt(self):
        return self.output
