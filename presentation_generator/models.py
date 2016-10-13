import json, yaml, jinja2, os
import logging

class Source(str):

    def __init__(self, source):
        self._source = source
        self._current_line = 0
        if isinstance(source, list):
            self.lines = source
        else:
            self.lines = source.splitlines(keepends=True)
        super(str).__init__()

    def __iter__(self):
        return iter(self.lines)

    def __next__(self):
        self._current_line += 1
        if self._current_line > len(self.lines):
            raise StopIteration

        return self.lines[self._current_line]

    # PROPERTIES (maybe split this up in source loaders module
    @property
    def source(self):
        return ''.join(self.lines)

    @property
    def json(self):
        return json.loads(self.source)

    @property
    def yaml(self):
        return yaml.load(self.source)

    @property
    def template(self):
        return jinja2.Template(self.source)

    # BUILTINS
    def _slice(self, start, stop):
        return Source(self.lines[start: stop])

    def __str__(self):
        return self.source

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self._slice(item.start, item.stop)


    @classmethod
    def from_json(cls, json_object):
        return cls(json.dumps(json_object))

    @classmethod
    def from_yaml(cls, yaml_object):
        return cls(yaml.dump(yaml_object, default_flow_style=True))


class SourceFile():

    def __init__(self, name: str, path: str, source : str= None):
        self.name = name
        self.path = os.path.realpath(path)
        if source is None:
            self._source = self._load_source(self.path)
        else:
            self._source = source


    @classmethod
    def from_path(cls, path):

        return cls(name=os.path.basename(path), path=path)


    @classmethod
    def _load_source(cls, path: str):
        with open(path) as f:

            try:
                source = f.read()
            except UnicodeDecodeError:
                source= 'IMAGE'

            return source

    @property
    def folder(self):
        return os.path.realpath(self.dirname)

    @property
    def extension(self):
        return self.filename.split('.')[-1]

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def source(self):
        return Source(self._source)


    #helper to acces source attributes
    def __getattr__(self, attr):
        logging.debug('gettting attribute {0} from source file, passing it to the child source object'.format(attr))
        return getattr(self.source, attr)

    def __len__(self):
        return len(self.source)


class Folder():
    def __init__(self, path):
        self.path = os.path.realpath(path)
        if os.path.isfile(path):
            raise Exception('trying to get folder using filename')
        self.items = [(i, os.path.join(path, i)) for i in os.listdir(path) if not i.startswith('.')]



    @property
    def files(self):
        return list(filter(lambda x: not os.path.isdir(x[1]), self.items))

    @property
    def dirs(self):
        return list(filter(lambda x: os.path.isdir(x[1]), self.items))

    def __getattr__(self, name):
        items_starting_with = [i for i in self.items if i[0].startswith(name)]

        if len(items_starting_with) > 1:
            raise Exception('multiple items with same name')
        if len(items_starting_with) == 0:
            raise AttributeError('no items with found with name {0} at path: {1}'.format(name, self.path))

        match_item = items_starting_with[0]
        logging.info('get item: {0}'.format(match_item))

        if os.path.isfile(match_item[1]):
            return SourceFile.from_path(match_item[1])
        else:
            return Folder(match_item[1])


    def get_folder(self, name):
        items_starting_with = [i for i in self.dirs if i[0].startswith(name)]
        if len(items_starting_with) > 1:
            raise Exception('multiple items with same name')
        if len(items_starting_with) == 0:
            raise AttributeError('no items with found with name {0}'.format(name))

        match_item = items_starting_with[0]
        return Folder(match_item[1])

    def get_file(self, name):
        items_starting_with = [i for i in self.files if i[0].startswith(name)]

        if len(items_starting_with) > 1:
            raise Exception('multiple items with same name')
        if len(items_starting_with) == 0:
            raise AttributeError('no items with found with name {0}'.format(name))

        match_item = items_starting_with[0]
        return SourceFile.from_path(match_item[1])

    @property
    def children(self):
        return [Folder(i[1]) for i in self.dirs]

    @property
    def parent(self):
        parent_path, current = os.path.split(self.path)
        return Folder(parent_path)


    def has_dir(self, name):
        try:
            self.get_folder(name)
            return True
        except AttributeError:
            return False

    def has_file(self, name):
        try:
            self.get_file(name)
            return True
        except AttributeError:
            return False

    def __repr__(self):
        return '[dir: >> {0} <<, {1} items]'.format(os.path.basename(self.path), len(self.items))


