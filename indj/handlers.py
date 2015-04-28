import os
import difflib
import itertools
from datetime import datetime
from indj import utils
from indj.index import DjangoIndex, DjangoSrc, DjangoJson
from indj.exceptions import (
    LookupHandlerError, ExactMatchNotFound, FuzzyMatchNotFound)


class LookupHandler(object):

    def __init__(self, version, settings):
        self.settings = settings
        self.version = version

    def get_filepath(self):
        for directory in self.settings.DATA_DIRECTORIES:
            filepath = utils.data_filepath_from_version(directory, self.version)
            if os.path.exists(filepath):
                return filepath
        raise LookupHandlerError(
            'No data file could be found for django version `{0}`'.format(
                utils.version_as_string(self.version)))

    def get_django_json(self):
        return DjangoJson(self.get_filepath(), self.settings)

    def get_django_index(self, django_json):
        return DjangoIndex(
            data=django_json.get_index_data(),
            version=django_json.get_version(),
            created=django_json.get_created(),
            settings=self.settings)

    def exact_match(self, query):
        django_json = self.get_django_json()
        django_index = self.get_django_index(django_json)
        if query not in django_index.names:
            raise ExactMatchNotFound(
                'Exact match not found for `{0}`'.format(query))
        return django_index.data[query]

    def fuzzy_match(self, query):
        django_json = self.get_django_json()
        django_index = self.get_django_index(django_json)
        matches = difflib.get_close_matches(query, django_index.names)
        if not matches:
            raise FuzzyMatchNotFound(
                'Fuzzy match not found for `{0}`'.format(query))
        paths = [django_index.data[match] for match in matches]
        return list(itertools.chain(*paths))


class CreationHandler(object):

    def __init__(self, src, settings):
        self.settings = settings
        self.src = src

    def get_django_src(self):
        return DjangoSrc(self.src, self.settings)

    def get_definitions_generator(self, django_src):
        filepaths = django_src.get_filepaths()
        generator = django_src.definitions_generator(filepaths)
        return generator

    def get_django_index(self, django_src):
        return DjangoIndex(
            data=django_src.create_index_data(
                generator=self.get_definitions_generator(django_src)
            ),
            version=django_src.get_version(),
            created=datetime.now(),
            settings=self.settings)
