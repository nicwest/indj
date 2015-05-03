import pytest
import os
import types
from datetime import datetime
from indj.exceptions import DjangoIndexError


class TestDjangoIndex:

    def test_names(self, index):
        assert index.names == ['DjangoThing', 'DjangoWotsit']

    def test_validate_raises_exception_with_no_data(self, index):
        index.data = None
        with pytest.raises(DjangoIndexError) as exceptinfo:
            index.validate()
        assert isinstance(exceptinfo.value, DjangoIndexError)
        assert exceptinfo.value.args == ('Given index is empty or None', )

    def test_validate_raises_exception_with_empty_data(self, index):
        index.data = {}
        with pytest.raises(DjangoIndexError) as exceptinfo:
            index.validate()
        assert isinstance(exceptinfo.value, DjangoIndexError)
        assert exceptinfo.value.args == ('Given index is empty or None', )

    def test_validate_raises_exception_with_non_dict_data(self, index):
        index.data = ['Not a dict']
        with pytest.raises(DjangoIndexError) as exceptinfo:
            index.validate()
        assert isinstance(exceptinfo.value, DjangoIndexError)
        assert exceptinfo.value.args == ('Data is not a dict', )

    def test_validate_raises_exception_with_no_version(self, index):
        index.version = None
        with pytest.raises(DjangoIndexError) as exceptinfo:
            index.validate()
        assert isinstance(exceptinfo.value, DjangoIndexError)
        assert exceptinfo.value.args == ('No Django version given', )

    def test_validate_raises_exception_with_no_created(self, index):
        index.created = None
        with pytest.raises(DjangoIndexError) as exceptinfo:
            index.validate()
        assert isinstance(exceptinfo.value, DjangoIndexError)
        assert exceptinfo.value.args == ('Index has no created date', )

    def test_to_dict_returns_dict(self, index):
        assert isinstance(index.to_dict(), dict)

    def test_to_dict_contains_data(self, index, data):
        assert 'data' in index.to_dict()
        assert index.to_dict()['data'] == data

    def test_to_dict_contains_version(self, index):
        assert 'version' in index.to_dict()
        assert index.to_dict()['version'] == '3.0.5'

    def test_to_dict_contains_created(self, index):
        assert 'created' in index.to_dict()
        assert index.to_dict()['created'] == datetime(2015, 3, 24, 23, 59, 59)

    def test_is_valid_returns_false_with_invalid_data(self, index):
        index.data = None
        assert not index.is_valid

    def test_is_valid_returns_true_with_valid_data(self, index):
        assert index.is_valid

    def test_save_throws_error_if_output_directory_doesnt_exist(self, index, tmpdir):
        index.settings.OUTPUT_DATA_DIRECTORY = str(tmpdir)
        tmpdir.remove()
        with pytest.raises(DjangoIndexError) as errinfo:
            index.save()
        assert errinfo.value.args == ('Output directory does not exist', )

    def test_save_throws_error_when_data_filepath_exists(self, index, tmpdir):
        index.settings.OUTPUT_DATA_DIRECTORY = str(tmpdir)
        index.version = (1, 2, 3, 'final', 4)
        filepath = os.path.join(str(tmpdir), 'django-1-2-3-final-4.json')
        open(filepath, 'w').write('foo')
        with pytest.raises(DjangoIndexError) as errinfo:
            index.save()
        assert errinfo.value.args == ('Output file already exists', )

    def test_save_doesnt_throw_error_when_data_filepath_exists_and_overwite_true(self, index, tmpdir, monkeypatch, mockmethod):
        index.settings.OUTPUT_DATA_DIRECTORY = str(tmpdir)
        index.settings.OVERWRITE = True
        index.version = (1, 2, 3, 'final', 4)
        mocked = mockmethod()
        monkeypatch.setattr(index, 'to_dict', mocked)

        filepath = os.path.join(str(tmpdir), 'django-1-2-3-final-4.json')
        open(filepath, 'w').write('foo')
        index.save()
        assert mocked.called

    def test_save_calls_to_dict_when_writing_file(self, index, tmpdir, monkeypatch, mockmethod):
        index.settings.OUTPUT_DATA_DIRECTORY = str(tmpdir)
        index.settings.DJANGO_VERSION = (1, 2, 3, 'final', 4)
        mocked = mockmethod()
        monkeypatch.setattr(index, 'to_dict', mocked)

        index.save()
        assert mocked.called


class TestDjangoSrc:

    def test_get_filepaths_returns_list_of_filepaths(self, src):
        filepaths = src.get_filepaths()
        assert isinstance(filepaths, list)
        assert len(filepaths) == 4
        assert all([os.path.exists(filepath) for filepath in filepaths])

    def test_get_filepaths_returns_only_python_files(self, src):
        filepaths = src.get_filepaths()
        assert all([filepath[-3:] == '.py' for filepath in filepaths])

    def test_get_filepaths_exludes_folders_in_settings_exclude_directory_patterns(self, src):
        src.settings.EXCLUDE_DIRECTORY_PATTERNS = [
            r'foobar',
        ]
        filepaths = src.get_filepaths()
        assert all([filepath[-28:] != 'mockdjango/foobars/models.py'
                    for filepath in filepaths])

    def test_get_filepaths_exludes_filename_in_settings_exclude_filename_patterns(self, src):
        src.settings.EXCLUDE_FILENAME_PATTERNS = [
            r'^pewpew.py',
        ]
        filepaths = src.get_filepaths()
        assert all([filepath[-28:] != 'mockdjango/foobars/pewpew.py'
                    for filepath in filepaths])

    def test__get_import_path_with_just_django(self, src):
        assert src._get_import_path('django', '') == 'django'

    def test__get_import_path_with_django_full_name(self, src):
        assert src._get_import_path('django.things', '') == 'django.things'

    def test__get_import_path_with_relative_import_module_name(self, src):
        assert src._get_import_path('thing', 'django.things') == 'django.things.thing'

    def test__file_is_magic(self, src):
        assert src._file_is_magic('foobar/__init__.py') is True
        assert src._file_is_magic('foobar/__foo.py') is False
        assert src._file_is_magic('foobar/__foo__.txt') is False
        assert src._file_is_magic('foobar/boshlol.py') is False

    def test__get_module_import_path_with_file_path(self, src):
        module_import_path = src._get_module_import_path(
            'tests/mockdjango/foobar/models.py')
        assert module_import_path == 'django.foobar.models'

    def test__get_module_import_path_with_magic_file_path(self, src):
        module_import_path = src._get_module_import_path(
            'tests/mockdjango/foobar/__init__.py')
        assert module_import_path == 'django.foobar'

    def test__get_module_import_path_with_root_init_file(self, src):
        module_import_path = src._get_module_import_path(
            'tests/mockdjango/__init__.py')
        assert module_import_path == 'django'

    def test__get_definitions_from_file_with_file_path(self, src):
        defs = src._get_definitions_from_file('tests/mockdjango/foobars/models.py')
        assert len(defs) == 2
        name, import_path = defs[0]
        assert name == 'processor_thing'
        assert import_path == 'django.foobars.models.processor_thing'
        name, import_path = defs[1]
        assert name == 'Thing'
        assert import_path == 'django.foobars.models.Thing'

    def test__get_definitions_from_file_with_magic_file_path(self, src):
        defs = src._get_definitions_from_file('tests/mockdjango/foobars/__init__.py')
        assert len(defs) == 1
        name, import_path = defs[0]
        assert name == 'That'
        assert import_path == 'django.foobars.That'

    def test_version_finder_matches_python_version_definition(self, src):
        version = src.version_finder.search("VERSION = (1, 2, 3, 'final', 4)")
        assert version is not None
        assert version.group(1) == "(1, 2, 3, 'final', 4)"

    def test_version_finder_matches_python_version_definition_mutilple_lines(self, src):
        version = src.version_finder.search(
            "bar = True\nVERSION = (1, 2, 3, 'final', 4)\nfoo = False")
        assert version is not None
        assert version.group(1) == "(1, 2, 3, 'final', 4)"

    def test_get_version_returns(self, src):
        assert src.get_version() == (1, 2, 3, 'final', 4)

    def test_definitions_generator_returns_generator(self, src):
        assert isinstance(
            src.definitions_generator(['file.path']),
            types.GeneratorType)

    def test_definitions_generator_gets_definitions_from_file(self, src, monkeypatch, mockmethod):
        mocked = mockmethod()
        mocked.return_value = []
        monkeypatch.setattr(src, '_get_definitions_from_file', mocked)
        generator = src.definitions_generator(['file.path', 'foo.bar'])
        [_ for _ in generator]
        assert mocked.was_called_with((('file.path', ), {}), (('foo.bar', ), {}))

    def test_create_index_data_without_generator_calls_filepaths(self, src, monkeypatch, mockmethod):
        mocked = mockmethod()
        mocked.return_value = []
        monkeypatch.setattr(src, 'get_filepaths', mocked)
        src.create_index_data()
        assert mocked.called

    def test_create_index_data_without_generator_calls_definition_generator_with_return_path(self, src, monkeypatch, mockmethod):
        mocked_generator = mockmethod()
        mocked_filepaths = mockmethod()
        mocked_generator.return_value = []
        mocked_filepaths.return_value = ['foo.py', 'bar.py']
        monkeypatch.setattr(src, 'definitions_generator', mocked_generator)
        monkeypatch.setattr(src, 'get_filepaths', mocked_filepaths)
        src.create_index_data()
        assert mocked_generator.was_called_with(((['foo.py', 'bar.py'], ), {}))

    def test_create_index_data_with_generator_does_not_get_new_generator(self, src, monkeypatch, mockmethod):
        mocked_generator = mockmethod()
        mocked_generator.return_value = []
        monkeypatch.setattr(src, 'definitions_generator', mocked_generator)
        fake_generator = (_ for _ in [])
        src.create_index_data(fake_generator)
        assert not mocked_generator.called

    def test_create_index_data_returns_dict(self, src):
        fake_generator = (_ for _ in [])
        data = src.create_index_data(fake_generator)
        assert isinstance(data, dict)

    def test_create_index_data_adds_definition_to_dict(self, src):
        fake_generator = (_ for _ in [
            ('Thing', 'foobars.Thing')])
        data = src.create_index_data(fake_generator)
        assert 'Thing' in data
        assert data['Thing'] == ['foobars.Thing']

    def test_create_index_data_adds_multiple_definitions_to_dict(self, src):
        fake_generator = (_ for _ in [
            ('Thing', 'foobars.Thing'),
            ('Foo', 'foobars.Foo')
        ])
        data = src.create_index_data(fake_generator)
        assert 'Thing' in data
        assert data['Thing'] == ['foobars.Thing']
        assert 'Foo' in data
        assert data['Foo'] == ['foobars.Foo']

    def test_create_index_data_adds_import_path_to_existing_definition_in_dict(self, src):
        fake_generator = (_ for _ in [
            ('Thing', 'foobars.Thing'),
            ('Thing', 'dohickies.Thing')
        ])
        data = src.create_index_data(fake_generator)
        assert 'Thing' in data
        assert data['Thing'] == ['foobars.Thing', 'dohickies.Thing']

    def test_create_index_data_ignores_repeated_import_path(self, src):
        fake_generator = (_ for _ in [
            ('Thing', 'foobars.Thing'),
            ('Thing', 'foobars.Thing')
        ])
        data = src.create_index_data(fake_generator)
        assert 'Thing' in data
        assert data['Thing'] == ['foobars.Thing']


class TestDjangoJson:
    data = {
        'data': {
            'Thing': [
                'foobars.Thing',
                'dohickies.Thing'
            ],
            'Thang': [
                'dat.Thang',
            ],
            'PewPew': [
                'foobars.PewPew'
            ]
        },
        'version': [1, 2, 3, 'final', 4],
        'created': '2015-04-18T12:30:45.00000'
    }

    def test_data_loads_json(self, djson):
        assert djson._data is None
        data = djson.data
        assert djson._data is not None
        assert data == djson._data
        assert data == self.data

    def test_get_index_data_returns_data(self, djson):
        assert djson.get_index_data() == self.data['data']

    def test_get_version_returns_tuple(self, djson):
        expected_version = (1, 2, 3, 'final', 4)
        version = djson.get_version()
        assert isinstance(version, tuple)
        assert expected_version == version

    def test_get_created_returns_datetime(self, djson):
        expected_created = datetime(2015, 4, 18, 12, 30, 45, 0)
        created = djson.get_created()
        assert isinstance(created, datetime)
        assert expected_created == created
