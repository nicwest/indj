import os
import pytest
import re
from indj import config
from conftest import needs_django, no_django


@needs_django
def test_env_django_version_gets_installed_django_version():
    from django import VERSION as django_version
    assert config.ENV_DJANGO_VERSION == django_version


@no_django
def test_env_django_version_is_none_with_no_django_installed():
    assert config.ENV_DJANGO_VERSION is None


@needs_django
def test_env_django_directory_gets_installed_django_location():
    from django import __file__ as django_directory
    assert config.ENV_DJANGO_DIRECTORY == os.path.dirname(django_directory)


@no_django
def test_env_django_directory_is_none_with_no_django_installed():
    assert config.ENV_DJANGO_DIRECTORY is None


class TestSettings:

    def test_excludes_pyc_files(self):
        pattern = config.Settings.EXCLUDE_FILENAME_PATTERNS[0]
        assert re.match(pattern, 'thing.pyc')
        assert re.match(pattern, 'foo.pyc')
        assert not re.match(pattern, 'thing.py')
        assert not re.match(pattern, 'thing.txt')

    def test_excludes_test_files(self):
        pattern = config.Settings.EXCLUDE_FILENAME_PATTERNS[1]
        assert re.match(pattern, 'test_thing.py')
        assert re.match(pattern, 'test_foo.py')
        assert not re.match(pattern, 'test.py')
        assert not re.match(pattern, 'tests.py')
        assert not re.match(pattern, 'testthing.py')

    def test_excludes_migration_files(self):
        pattern = config.Settings.EXCLUDE_FILENAME_PATTERNS[2]
        assert re.match(pattern, '0001_auto_thing.py')
        assert re.match(pattern, '9999_pewpepewpewpewe.py')
        assert not re.match(pattern, '0_foo.py')
        assert not re.match(pattern, '00000_foo.py')
        assert not re.match(pattern, 'foo.py')
        assert not re.match(pattern, '0000_thing.md')

    def test_excludes_translation_directories(self):
        pattern = config.Settings.EXCLUDE_DIRECTORY_PATTERNS[0]
        assert re.match(pattern, 'LC_MESSAGES')
        assert not re.match(pattern, 'VLC_MESSAGES')

