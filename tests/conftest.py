import os
import pytest
import json
from indj.config import Settings
from datetime import datetime
from indj.index import DjangoIndex, DjangoSrc, DjangoJson
from indj.handlers import LookupHandler, CreationHandler

try:
    import django  # NOQA
    has_django = True
except ImportError:
    has_django = False

needs_django = pytest.mark.skipif(
    has_django is False,
    reason='django is required')
no_django = pytest.mark.skipif(
    has_django is True,
    reason='django is installed')


@pytest.fixture
def index_settings():
    settings = Settings()
    return settings


@pytest.fixture
def data():
    return {
        'DjangoThing': [
            'django.things.DjangoThing',
            'django.shortcuts.DjangoThing'
        ],
        'DjangoWotsit': [
            'django.things.DjangoWotsit',
            'django.shortcuts.DjangoWotsit'
        ]
    }


@pytest.fixture
def index(index_settings, data):
    version = '3.0.5'
    created = datetime(2015, 3, 24, 23, 59, 59)
    return DjangoIndex(data, version, created, index_settings)


@pytest.fixture
def src(index_settings):
    fakesrc = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'mockdjango')
    return DjangoSrc(fakesrc, index_settings)


@pytest.fixture
def index_data():
    index_data = {
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
        'version': (1, 2, 3, 'final', 4),
        'created': '2015-04-18T12:30:45.00000'
    }
    return index_data


@pytest.fixture
def mockjson(tmpdir, index_data):
    filepath = os.path.join(str(tmpdir), 'django-1-2-3-final-4.json')
    with open(filepath, 'w') as fh:
        json.dump(index_data, fh)
    return filepath


@pytest.fixture
def djson(mockjson, index_settings):
    djson = DjangoJson(mockjson, index_settings)
    return djson


@pytest.fixture
def mockmethod():
    class MockMethod(object):
        calls = []

        def __init__(self):
            self.calls = []
            self.return_value = None

        def __call__(self, *args, **kwargs):
            self.calls.append((args, kwargs, ))
            return self.return_value

        @property
        def called(self):
            if self.calls:
                return True
            return False

        def was_called_with(self, *args):
            return all([arg_list in self.calls for arg_list in args])

    return MockMethod


@pytest.fixture
def lookup(index_settings, data_files):
    output, package = data_files
    index_settings.DATA_DIRECTORIES = [output, package]
    index_settings.DJANGO_VERSION = (1, 2, 3, 'final', 4)
    lookup = LookupHandler(index_settings)
    return lookup


@pytest.fixture
def creation(index_settings):
    test_dir = os.path.dirname(__file__)
    index_settings.DJANGO_DIRECTORY = os.path.join(test_dir, 'mockdjango')
    return CreationHandler(index_settings)


@pytest.fixture
def data_files(tmpdir, index_data):
    output = os.path.join(str(tmpdir), 'output')
    package = os.path.join(str(tmpdir), 'package')
    os.mkdir(output)
    os.mkdir(package)
    with open(os.path.join(output, 'django-1-2-3-final-4.json'), 'w') as fh:
        json.dump(index_data, fh)
    with open(os.path.join(package, 'django-1-2-3-final-4.json'), 'w') as fh:
        json.dump(index_data, fh)
    index_data['version'] = (3, 2, 1, 'alpha', 0)
    with open(os.path.join(package, 'django-3-2-1-alpha-0.json'), 'w') as fh:
        json.dump(index_data, fh)

    return (output, package, )


@pytest.fixture
def mock_args(monkeypatch):
    import sys

    def set_args(args):
        monkeypatch.setattr(sys, 'argv', ['indj'] + args)

    return set_args


@pytest.fixture
def args():
    class Args(object):
        exact = False
        django_version = None
        names_only = False
        create = False
        source = None
        silent = False

    return Args()
