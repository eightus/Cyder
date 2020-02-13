class VFSError:
    """
    Error Class For VFS
    Feel Free To Override Anything Here
    """

    class ObjNotFound(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'Object Not Found'

        def __str__(self):
            return self.msg

    class FileNotFound(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'File Not Found'

        def __str__(self):
            return self.msg

    class DirectoryNotFound(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'Directory Not Found'

        def __str__(self):
            return self.msg

    class ObjIsFile(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'Object is File'

        def __str__(self):
            return self.msg

    class ObjIsDirectory(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'Object is Directory'

        def __str__(self):
            return self.msg

    class ObjExist(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'Object Exist'

        def __str__(self):
            return self.msg

    class VFSNotFound(Exception):
        def __init__(self, msg=None):
            self.msg = msg if msg else 'VFS Not Found'

        def __str__(self):
            return self.msg

    class InvalidArgument(Exception):
        def __init__(self, msg=None, **kwargs):
            self.extra = kwargs
            self.msg = msg if msg else 'Invalid Argument'

        def __str__(self):
            return self.msg

    class MissingParameter(Exception):
        def __init__(self, msg=None, **kwargs):
            self.extra = kwargs
            self.msg = msg if msg else 'Argument Specified, But No Parameter'

        def __str__(self):
            return self.msg

    class Error(Exception):
        def __init__(self, msg=None, **kwargs):
            self.extra = kwargs
            self.msg = msg if msg else 'Default Error'

        def __str__(self):
            return self.msg
