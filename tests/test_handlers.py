import pytest
import os
import types
from indj.index import DjangoSrc, DjangoIndex, DjangoJson
from indj.exceptions import (
    LookupHandlerError, ExactMatchNotFound, FuzzyMatchNotFound)


class TestLookupHandler:

    def test_get_filepath_returns_matching_filepath(self, lookup):
        lookup.settings.DJANGO_VERSION = (3, 2, 1, 'alpha', 0)
        filepath = lookup.get_filepath()
        package = lookup.settings.DATA_DIRECTORIES[1]
        assert filepath == os.path.join(package, 'django-3-2-1-alpha-0.json')

    def test_get_filepath_returns_first_matching_filepath(self, lookup):
        filepath = lookup.get_filepath()
        output = lookup.settings.DATA_DIRECTORIES[0]
        assert filepath == os.path.join(output, 'django-1-2-3-final-4.json')

    def test_get_filepath_raise_exception_when_file_not_found(self, lookup):
        lookup.settings.DJANGO_VERSION = (9, 9, 9, 'zeta', 9)
        with pytest.raises(LookupHandlerError) as errinfo:
            lookup.get_filepath()
        assert errinfo.value.args == (
            'No data file could be found for django version `9-9-9-zeta-9`', )

    def test_get_django_json_returns_django_json_object(self, lookup):
        assert isinstance(lookup.get_django_json(), DjangoJson)

    def test_get_django_index_returns_django_index(self, lookup):
        filepath = lookup.get_filepath()
        django_json = DjangoJson(filepath, lookup.settings)
        assert isinstance(lookup.get_django_index(django_json), DjangoIndex)

    def test_exact_match_returns_paths_that_exactly_match_query_string(self, lookup, index_data):
        django_json = lookup.get_django_json()
        django_index = lookup.get_django_index(django_json)
        expected = index_data['data']['Thing']
        assert lookup.exact_match('Thing', django_json, django_index) == expected

    def test_exact_match_raises_exception_when_key_not_found(self, lookup):
        django_json = lookup.get_django_json()
        django_index = lookup.get_django_index(django_json)
        with pytest.raises(ExactMatchNotFound) as expinfo:
            lookup.exact_match('Thong', django_json, django_index)
        assert expinfo.value.args == ('Exact match not found for `Thong`', )

    def test_fuzzy_match_returns_paths_that_roughly_match_query_string(self, lookup, index_data):
        django_json = lookup.get_django_json()
        django_index = lookup.get_django_index(django_json)
        expected = [
            path for path in
            index_data['data']['Thing'] + index_data['data']['Thang']
        ]
        assert lookup.fuzzy_match('Thong', django_json, django_index) == expected

    def test_fuzzy_match_raises_exception_when_no_matches_found(self, lookup):
        django_json = lookup.get_django_json()
        django_index = lookup.get_django_index(django_json)
        with pytest.raises(FuzzyMatchNotFound) as expinfo:
            lookup.fuzzy_match('DoHicky', django_json, django_index)
        assert expinfo.value.args == ('Fuzzy match not found for `DoHicky`', )


class TestCreationHandler:

    def test_get_django_src_returns_django_src_object(self, creation):
        assert isinstance(creation.get_django_src(), DjangoSrc)

    def test_get_definitions_generator_returns_generator(self, creation, src):
        assert isinstance(creation.get_definitions_generator(src), types.GeneratorType)

    def test_get_django_index_returns_django_index_object(self, creation, src):
        assert isinstance(creation.get_django_index(src), DjangoIndex)

    def test_get_django_index_creates_data_from_definitions_generator(self, creation, src, monkeypatch, mockmethod):
        generator = mockmethod()
        create_index_data = mockmethod()
        generator.return_value = 'generator'
        create_index_data.return_value = 'index_data'
        monkeypatch.setattr(creation, 'get_definitions_generator', generator)
        monkeypatch.setattr(src, 'create_index_data', create_index_data)
        index_data = creation.get_django_index(src)
        assert generator.called
        assert generator.was_called_with(((src, ), {}))
        assert create_index_data.called
        assert create_index_data.was_called_with(((), {'generator': 'generator'}))
        assert index_data.data == 'index_data'
