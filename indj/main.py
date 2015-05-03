import sys
import argparse
from indj.config import Settings
from indj.utils import version_as_tuple
from indj.handlers import CreationHandler, LookupHandler, NoisyCreationHandler


class DjangoVersionAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, version_as_tuple(values))


def get_args(argv):
    parser = argparse.ArgumentParser(
        description='command line lookup for django objects')

    # lookup options
    parser.add_argument('-e', '--exact', action='store_true', dest='exact',
                        help='only return exact matches')
    parser.add_argument('--django-version', metavar='X.Y.Z',
                        dest='django_version', action=DjangoVersionAction,
                        help='query specific version of django, defaults to installed or latest version')
    parser.add_argument('-n', '--names-only', action='store_true',
                        dest='names_only',
                        help='only return index names')

    # create options
    parser.add_argument('-c', '--create', action='store_true',
                        dest='create',
                        help='creates new index file')
    parser.add_argument('--source', metavar='/path/to/django',
                        dest='source',
                        help='specify source directory')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        dest='overwrite',
                        help='overwrite existing data file when necessary')
    parser.add_argument('--output-dir', action='store_true',
                        dest='output_dir',
                        help='change default output directory')

    # general
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-s', '--silent', action='store_true', dest='silent',
                        help='silence all non essential stdout and stderr')
    parser.add_argument('query', nargs='?')

    args = parser.parse_args(argv)

    return args


def get_settings(args):
    settings = Settings()
    if args.django_version:
        settings.DJANGO_VERSION = args.django_version
    if args.source:
        settings.DJANGO_DIRECTORY = args.source
    if args.exact:
        settings.EXACT_MATCH = True
    if args.overwrite:
        settings.OVERWRITE = True
    if args.output_dir:
        settings.OUTPUT_DATA_DIRECTORY = args.output_dir
    return settings


def main(*args, **kwargs):
    args = get_args(sys.argv[1:])
    settings = get_settings(args)
    if args.create:
        handler_class = CreationHandler if args.silent else NoisyCreationHandler
        handler = handler_class(settings)
        handler.create()
    else:
        handler = LookupHandler(settings)
        matches = handler.lookup(args.query)
        for match in matches:
            sys.stdout.write('{}\n'.format(match))
        sys.stdout.flush()


if __name__ == '__main__':
    main()
