import re
import os


def join_regexp(regexps):
    if not regexps:
        return re.compile('^$')
    joined_regexp = '|'.join(regexps)
    return re.compile('{joined_regexp}'.format(joined_regexp=joined_regexp))


def version_as_string(version):
    return '-'.join("{0}".format(item) for item in version)


def data_filepath_from_version(data_directory, version):
    version_string = version_as_string(version)
    data_filename = os.path.join(
        data_directory,
        'django-{version}.json'.format(version=version_string))
    return data_filename


def json_serialize(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError(
            'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))


def version_as_tuple(version):
    split = re.split(r'[\.-]', version)
    return tuple(int(x) if hasattr(x, 'isdigit') and x.isdigit() else x
                 for x in split)
