import re
import json
import datetime
import pytest
from indj import utils


def test_join_regexp_returns_valid_regexp():
    joined_regexp = utils.join_regexp(['abc', 'xyz'])
    assert isinstance(joined_regexp, re._pattern_type)


def test_join_regexp_allows_for_multiple_start_lines_end_lines():
    joined_regexp = utils.join_regexp([r'^abc.*', r'^123.*', r'.*890$', r'.*xyz$'])
    assert joined_regexp.match('abcdefg') is not None
    assert joined_regexp.match('12345') is not None
    assert joined_regexp.match('tuvwxyz') is not None
    assert joined_regexp.match('67890') is not None
    assert joined_regexp.match('asdabc') is None
    assert joined_regexp.match('67812345') is None
    assert joined_regexp.match('xyztuvw') is None
    assert joined_regexp.match('89067') is None


def test_join_regexp_allows_for_multiple_nested_groups():
    joined_regexp = utils.join_regexp([r'(abc|xyz)', r'(123|890)'])
    assert joined_regexp.match('abc') is not None
    assert joined_regexp.match('xyz') is not None
    assert joined_regexp.match('123') is not None
    assert joined_regexp.match('890') is not None
    assert joined_regexp.match('lmn') is None
    assert joined_regexp.match('456') is None


def test_join_regexp_when_given_no_regexps_returns_re_obj_that_will_only_match_empty_strings():
    joined_regexp = utils.join_regexp([])
    assert joined_regexp.match('') is not None
    assert joined_regexp.match('abc') is None


def test_version_as_string_returns_correct_string():
    version = (1, 2, 3, 'final', 4)
    assert utils.version_as_string(version) == '1-2-3-final-4'


def test_data_filepath_from_version_joins_version_tuple_and_directory():
    version = (1, 2, 3, 'final', 4)
    filepath = utils.data_filepath_from_version('/foobar', version)
    assert filepath == '/foobar/django-1-2-3-final-4.json'


def test_json_serialize_handles_datetime_objs():
    obj = {
        'datetime': datetime.datetime(2015, 4, 18, 12, 30),
    }
    result = json.dumps(obj, default=utils.json_serialize)
    assert '"datetime": "2015-04-18T12:30:00"' in result


def test_json_serialize_raises_exception_with_unkown_instance():
    class Thing():

        def __repr__(self):
            return 'pewpew'

    obj = {
        'thing': Thing(),
    }

    with pytest.raises(TypeError) as errinfo:
        json.dumps(obj, default=utils.json_serialize)

    expected_error = 'Object of type {thing_type} with value of pewpew is not JSON serializable'.format(
        thing_type=type(Thing()))

    assert errinfo.value.args == (expected_error, )
