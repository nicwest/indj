import pytest
import os
import types
from conftest import needs_django, no_django
from indj.settings import DEFAULT_DJANGO_VERSION
from indj.index import DjangoSrc, DjangoIndex, DjangoJson
from indj.exceptions import LookupHandlerError


class TestLookupHandler:

    def test_get_filepath_returns_matching_filepath(self, data_files, lookup):
        output, package = data_files
        lookup.settings.DATA_DIRECTORIES = [output, package]
        lookup.version = (3, 2, 1, 'alpha', 0)
        filepath = lookup.get_filepath()
        assert filepath == os.path.join(package, 'django-3-2-1-alpha-0.json')

    def test_get_filepath_returns_first_matching_filepath(self, data_files, lookup):
        output, package = data_files
        lookup.settings.DATA_DIRECTORIES = [output, package]
        lookup.version = (1, 2, 3, 'final', 4)
        filepath = lookup.get_filepath()
        assert filepath == os.path.join(output, 'django-1-2-3-final-4.json')

    def test_get_filepath_raise_exception_when_file_not_found(self, data_files, lookup):
        output, package = data_files
        lookup.settings.DATA_DIRECTORIES = [output, package]
        lookup.version = (9, 9, 9, 'zeta', 9)
        with pytest.raises(LookupHandlerError) as errinfo:
            lookup.get_filepath()
        assert errinfo.value.args == (
            'No data file could be found for django version `9-9-9-zeta-9`', )


    #def test_version_returns_tuple(self, lookup):
    #    assert isinstance(lookup.version, tuple)

    @needs_django
    def test_version_returns_env_django_version_when_django_installed(self, lookup):
        from django import VERSION as django_version
        assert lookup.version == django_version

    @no_django
    def test_version_returns_default_version_when_no_django_installed(self, lookup):
        assert lookup.version == DEFAULT_DJANGO_VERSION


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
