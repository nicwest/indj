import os

DEFAULT_DJANGO_VERSION = (1, 8, 1, 'final', 0)

try:
    from django import VERSION as django_version
    ENV_DJANGO_VERSION = django_version
except ImportError:
    ENV_DJANGO_VERSION = None

try:
    from django import __file__ as django_directory
    ENV_DJANGO_DIRECTORY = os.path.dirname(django_directory)
except ImportError:
    ENV_DJANGO_DIRECTORY = None


class Settings(object):
    HOME_DIRECTORY = os.path.expanduser('~')
    SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

    OUTPUT_DATA_DIRECTORY = os.path.join(HOME_DIRECTORY, '.indj', 'data')
    PACKAGE_DATA_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, 'data')
    DATA_DIRECTORIES = [
        OUTPUT_DATA_DIRECTORY,
        PACKAGE_DATA_DIRECTORY,
    ]

    DJANGO_VERSION = ENV_DJANGO_VERSION if ENV_DJANGO_VERSION else DEFAULT_DJANGO_VERSION
    DJANGO_DIRECTORY = ENV_DJANGO_DIRECTORY

    EXCLUDE_DIRECTORY_PATTERNS = [
        r'^LC_MESSAGES',
    ]
    EXCLUDE_FILENAME_PATTERNS = [
        r'^[^/]*\.pyc$',  # pyc files
        r'^test_[^/]*$',  # test files
        r'^\d{4}_[^/]*\.py$',  # migrations
    ]

    OVERWRITE = False
    EXACT_MATCH = False
