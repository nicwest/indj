import pytest
import argparse
from indj.config import Settings
from indj.main import get_args, get_settings


class TestGetArgs:

    def test_returns_argparse_namespace(self):
        args = get_args(['foo'])
        assert isinstance(args, argparse.Namespace)

    def test_exits_with_no_arguments(self):
        with pytest.raises(SystemExit):
            get_args([])

    def test_exact(self):
        args = get_args(['fooo'])
        assert args.exact is False

        args = get_args(['-e', 'fooo'])
        assert args.exact is True

        args = get_args(['--exact', 'fooo'])
        assert args.exact is True

    def test_django_version(self):
        args = get_args(['fooo'])
        assert args.django_version is None

        with pytest.raises(SystemExit):
            args = get_args(['--django-version', 'fooo'])

        args = get_args(['--django-version', '1.2.3-final.4', 'fooo'])
        assert args.django_version == (1, 2, 3, 'final', 4)

        args = get_args(['--django-version', '1-2-beta-4', 'fooo'])
        assert args.django_version == (1, 2, 'beta', 4)

    def test_names_only(self):
        args = get_args(['fooo'])
        assert args.names_only is False

        args = get_args(['-n', 'fooo'])
        assert args.names_only is True

        args = get_args(['--names-only', 'fooo'])
        assert args.names_only is True

    def test_create(self):
        args = get_args(['fooo'])
        assert args.create is False

        args = get_args(['-c', 'fooo'])
        assert args.create is True

        args = get_args(['--create', 'fooo'])
        assert args.create is True

    def test_source(self):
        args = get_args(['fooo'])
        assert args.source is None

        with pytest.raises(SystemExit):
            args = get_args(['--source', 'fooo'])

        args = get_args(['--source', 'path/to/django', 'fooo'])
        assert args.source == 'path/to/django'

    def test_silent(self):
        args = get_args(['fooo'])
        assert args.names_only is False

        args = get_args(['-n', 'fooo'])
        assert args.names_only is True

        args = get_args(['--names-only', 'fooo'])
        assert args.names_only is True


class TestGetSettings:

    def test_returns_settings_object(self, args):
        settings = get_settings(args)
        assert isinstance(settings, Settings)

    def test_adjusts_settings_if_django_version_is_in_args(self, args):
        args.django_version = (1, 2, 3, 'final', 4)
        settings = get_settings(args)
        assert settings.DJANGO_VERSION == (1, 2, 3, 'final', 4)

    def test_adjusts_settings_if_cource_is_in_args(self, args):
        args.source = 'path/to/django'
        settings = get_settings(args)
        assert settings.DJANGO_DIRECTORY == 'path/to/django'
