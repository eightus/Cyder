from vfssh.vfs.fs_object import FileObject
from vfssh.vfs.error import VFSError


class FolderObject:
    def __init__(self, name, attributes, location, obj=None, size=4096, timestamp=None, owner=None):
        self.name = name
        self.attributes = attributes
        self.loc = location
        self.timestamp = timestamp
        self.owner = owner
        self.group = owner
        #  TODO: Custom Size of Directory? (Not really needed...)
        self.size = size if size else size
        self.obj = obj if obj else []

    def add_obj(self, obj):
        #  Check if File Name Exist in directory
        if any(obj.name == d.name for d in self.obj):
            raise VFSError.ObjExist
        else:
            self.obj.append(obj)
            return True

    def del_obj(self, obj):
        self.obj.remove(obj)

    def get_obj(self, name: str):
        if any(name == d.name for d in self.obj):
            a = (x for x in self.obj if name == x.name)
            for x in a:
                return x
        else:
            raise VFSError.ObjNotFound

    def list_obj(self, fmt=None):
        if fmt is None:
            return [o for o in self.obj]
        elif fmt == 'name':
            return [o.name for o in self.obj]
        elif fmt == 'attribute':
            return [o.attributes for o in self.obj]
        elif fmt == 'dict':
            return [o.to_dict() for o in self.obj]
        elif fmt == 'list':
            return [o.to_list() for o in self.obj]
        else:
            #  Unknown Format
            return False

    def to_list(self):
        return [self.name, self.attributes, self.obj]

    def to_dict(self):
        return {'name': self.name, 'attribute': self.attributes, 'type': __class__, 'data': self.obj}
