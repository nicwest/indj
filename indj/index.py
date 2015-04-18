import json
import jedi
import fnmatch
import os
import re
import datetime
from .exceptions import DjangoIndexError
from . import utils


class DjangoIndex(object):

    def __init__(self, data, version, created, settings):
        self.data = data
        self.version = version
        self.created = created
        self.settings = settings

    @property
    def names(self):
        return sorted(list(self.data.keys()))

    def validate(self):
        if not self.data:
            raise DjangoIndexError('Given index is empty or None')
        if not self.version:
            raise DjangoIndexError('No Django version given')
        if not self.created:
            raise DjangoIndexError('Index has no created date')
        if not isinstance(self.data, dict):
            raise DjangoIndexError('Data is not a dict')

    def to_dict(self):
        return {'data': self.data,
                'version': self.version,
                'created': self.created}

    @property
    def is_valid(self):
        try:
            self.validate()
        except:
            return False
        return True

    def save(self, overwrite=False):
        data_directory = self.settings.JSON_OUTPUT_DIRECTORY
        data_filepath = utils.data_filepath_from_version(
            data_directory, self.version)

        if not os.path.exists(data_directory):
            raise DjangoIndexError('Output directory does not exist')

        if os.path.exists(data_filepath) and not overwrite:
            raise DjangoIndexError('Output file already exists')

        with open(data_filepath, 'w') as fh:
            json.dump(self.to_dict(), fh, default=utils.json_serialize)


class DjangoSrc(object):

    version_finder = re.compile(r'^VERSION\s*=\s*(.*)$', re.MULTILINE)

    def __init__(self, src, settings):
        self.src = src
        self.settings = settings

    def _file_is_magic(self, path):
        return os.path.basename(path).startswith('__') and path.endswith('__.py')

    def _get_import_path(self, full_name, module_import_path):
        if full_name.startswith('django.') or full_name == 'django':
            return full_name
        return '{path}.{name}'.format(path=module_import_path, name=full_name)

    def _get_module_import_path(self, module_path):
        abs_module_path = os.path.abspath(module_path)
        abs_src = os.path.abspath(self.src)

        # if the filename is magic (i.e '__init__.py') then the import path is
        # actually the files parent directory
        if self._file_is_magic(abs_module_path):
            abs_module_path = os.path.dirname(abs_module_path)

        # relpath is the path to the module relative to the base src directory
        relpath = os.path.relpath(abs_module_path, abs_src)
        relpath, _ = os.path.splitext(relpath)

        if relpath in ['.', '..']:
            relpath = ''

        return 'django{dot}{path}'.format(
            dot='.' if relpath else '',
            path=relpath.replace(os.path.sep, '.'))

    def _get_definitions_from_file(self, path):
        with open(path, 'r') as fh:
            defs = jedi.defined_names(fh.read())
        module_import_path = self._get_module_import_path(path)
        items = [
            (d.name, self._get_import_path(d.full_name, module_import_path))
            for d in defs]
        return items

    def get_filepaths(self):
        filepaths = []
        exclude_folders_pattern = utils.join_regexp(
            self.settings.EXCLUDE_DIRECTORY_PATTERNS)
        exclude_filename_pattern = utils.join_regexp(
            self.settings.EXCLUDE_FILENAME_PATTERNS)

        for root, dirs, filenames in os.walk(self.src):
            if exclude_folders_pattern.match(os.path.basename(root)):
                continue

            for filename in fnmatch.filter(filenames, '*.py'):

                if exclude_filename_pattern.match(filename):
                    continue

                filepaths.append(os.path.join(root, filename))

        return filepaths

    def get_version(self):
        path = os.path.join(self.src, '__init__.py')
        with open(path, 'r') as fh:
            contents = fh.read()
            matches = self.version_finder.search(contents)
            version = matches.group(1)
        return eval(version)

    def definitions_generator(self, filepaths):
        for path in filepaths:
            yield self._get_definitions_from_file(path)

    def create_index_data(self, generator=None):
        if not generator:
            filepaths = self.get_filepaths()
            generator = self.definitions_generator(filepaths)
        data = {}
        for name, path, source in generator:
            if name in data:
                if path not in data[name]:
                    data[name].append(path)
            else:
                data[name] = [path]
        return data


class DjangoJson(object):

    def __init__(self, filepath, settings):
        self.filepath = filepath
        self.settings = settings
        self._data = None

    @property
    def data(self):
        if self._data is None:
            with open(self.filepath, 'r') as fh:
                self._data = json.load(fh)
        return self._data

    def get_index_data(self):
        return self.data['data']

    def get_version(self):
        return tuple(self.data['version'])

    def get_created(self):
        created = datetime.datetime.strptime(
            self.data['created'],
            '%Y-%m-%dT%H:%M:%S')
        return created
