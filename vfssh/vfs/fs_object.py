class FileObject:
    def __init__(self, name, attributes, location, data=None, memory=None, size=None, timestamp=None, owner=None):
        self.name = name
        self.attributes = attributes
        self.loc = location
        #  TODO: Find size of obj/file
        self.size = size if size else size
        self.memory = memory
        self.timestamp = timestamp
        self.owner = owner
        self.group = owner
        if memory is True:
            with open(data, 'r') as f:
                self._data = f.read()
        else:
            self._data = data

    def to_list(self):
        return [self.name, self.attributes, self._data]

    def to_dict(self):
        return {'name': self.name, 'attribute': self.attributes, 'type': __class__, 'data': self._data}

    @property
    def data(self):
        if self.memory is False:
            with open(self._data, 'r') as f:
                return f.read()
        else:
            return self._data
