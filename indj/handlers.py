import os
import sys
import difflib
import itertools
from datetime import datetime
from indj import utils
from indj.index import DjangoIndex, DjangoSrc, DjangoJson
from indj.exceptions import (
    LookupHandlerError, ExactMatchNotFound, FuzzyMatchNotFound)


class LookupHandler(object):

    def __init__(self, settings):
        self.settings = settings

    def get_filepath(self):
        for directory in self.settings.DATA_DIRECTORIES:
            filepath = utils.data_filepath_from_version(
                directory, self.settings.DJANGO_VERSION)
            if os.path.exists(filepath):
                return filepath
        raise LookupHandlerError(
            'No data file could be found for django version `{0}`'.format(
                utils.version_as_string(self.settings.DJANGO_VERSION)))

    def get_django_json(self):
        return DjangoJson(self.get_filepath(), self.settings)

    def get_django_index(self, django_json):
        return DjangoIndex(
            data=django_json.get_index_data(),
            version=django_json.get_version(),
            created=django_json.get_created(),
            settings=self.settings)

    def exact_match(self, query, django_json, django_index):
        if query not in django_index.names:
            raise ExactMatchNotFound(
                'Exact match not found for `{0}`'.format(query))
        return django_index.data[query]

    def fuzzy_match(self, query, django_json, django_index):
        matches = difflib.get_close_matches(
            query, django_index.names, self.settings.MAX_RESULTS)
        if not matches:
            raise FuzzyMatchNotFound(
                'Fuzzy match not found for `{0}`'.format(query))
        return self._get_paths(django_index, matches)

    def _get_paths(self, django_index, matches, path_query=None):
        paths = [django_index.data[match] for match in matches]
        paths = list(itertools.chain(*paths))
        if path_query:
            paths = [
                path
                for path in paths
                if ('.'.join(path.split('.')[:-1])).endswith(path_query)]
        return paths

    def _seperate_path_from_query(self, query):
        if '.' in query:
            split_path = query.split('.')
            return '.'.join(split_path[:-1]), split_path[-1]
        return None, query

    def substring_match(self, query, django_jason, django_index):
        path_query, query = self._seperate_path_from_query(query)
        items = []
        exact_case_sensitive = []
        exact_case_insensitive = []
        substring_case_sensitive = []
        substring_case_insensitive = []

        only_lower = query.lower() == query

        for item in django_index.names:
            if item == query and item not in items:
                exact_case_sensitive.append(item)
                items.append(item)
            if only_lower and item.lower() == query.lower() and item not in items:
                exact_case_insensitive.append(item)
                items.append(item)
            if query in item and item not in items:
                substring_case_insensitive.append(item)
                items.append(item)
            if only_lower and query.lower() in item.lower() and item not in items:
                substring_case_insensitive.append(item)
                items.append(item)

        matches = list(exact_case_sensitive +
                       exact_case_insensitive +
                       substring_case_sensitive +
                       substring_case_insensitive)
        paths = self._get_paths(django_index, matches, path_query)

        #return paths[:self.settings.MAX_RESULTS]
        return paths

    def lookup(self, query):
        django_json = self.get_django_json()
        django_index = self.get_django_index(django_json)
        if self.settings.EXACT_MATCH:
            matches = self.exact_match(query, django_json, django_index)
        elif self.settings.FUZZY_MATCH:
            matches = self.fuzzy_match(query, django_json, django_index)
        else:
            matches = self.substring_match(query, django_json, django_index)

        return matches


class CreationHandler(object):

    def __init__(self, settings):
        self.settings = settings

    def get_django_src(self):
        return DjangoSrc(self.settings.DJANGO_DIRECTORY, self.settings)

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

    def create(self):
        source = self.get_django_src()
        index = self.get_django_index(source)
        index.validate()
        index.save()
        return index


class NoisyCreationHandler(CreationHandler):

    status_width = 40

    def _status(self, item, total, overwrite=True):
        if overwrite:
            sys.stdout.write("\b" * (self.status_width+6))
        sys.stdout.write('[')
        percentage = float(item) / float(total-1)
        marker = int(self.status_width * percentage)
        for i in xrange(0, max(0, marker)):
            sys.stdout.write('=')
        if marker >= 0 and item < total-1:
            sys.stdout.write('>')
        for i in xrange(0, self.status_width - marker-1):
            sys.stdout.write(' ')
        sys.stdout.write(']{:>3}%'.format(int(percentage * 100)))
        sys.stdout.flush()

    def get_definitions_generator(self, django_src):
        sys.stdout.write('collecting file paths...\n')
        sys.stdout.flush()
        filepaths = django_src.get_filepaths()
        sys.stdout.write('found {0} filepaths\n'.format(len(filepaths)))
        sys.stdout.flush()

        self._status(0, len(filepaths), overwrite=False)
        for i, path in enumerate(filepaths):
            self._status(i, len(filepaths))
            try:
                for item in django_src._get_definitions_from_file(path):
                    yield item
            except:
                pass

        sys.stdout.write('\n')
        sys.stdout.flush()

    def create(self):
        index = super(NoisyCreationHandler, self).create()
        sys.stdout.write('found {0} unique importable objects\n'.format(
            len(index)))
        sys.stdout.flush()
        return index
