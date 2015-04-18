import os
import pytest
import json
from indj.settings import Settings
from datetime import datetime
from indj.index import DjangoIndex, DjangoSrc, DjangoJson

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
def mockjson(tmpdir):
    data = {
        'data': {
            'Thing': [
                'foobars.Thing',
                'dohickies.Thing'
            ],
            'PewPew': [
                'foobars.PewPew'
            ]
        },
        'version': (1, 2, 3, 'final', 4),
        'created': '2015-04-18T12:30:45'
    }
    filepath = os.path.join(str(tmpdir), 'django-1-2-3-final-4.json')
    with open(filepath, 'w') as fh:
        json.dump(data, fh)

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

        def __call__(self, *args):
            self.calls.append(args)
            return self.return_value

        @property
        def called(self):
            if self.calls:
                return True
            return False

        def was_called_with(self, *args):
            return all([arg_list in self.calls for arg_list in args])

    return MockMethod
