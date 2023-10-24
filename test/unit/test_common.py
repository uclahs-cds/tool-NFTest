# pylint: disable=W0212
''' Test module for common functions '''

import mock
import pytest

from nftest.common import resolve_single_path

@pytest.mark.parametrize(
    'glob_return_value,case_pass',
    [
        ([], False),
        (['a', 'b'], False),
        (['a'], True)
    ]
)
@mock.patch('glob.glob')
def test_resolve_single_path(mock_glob, glob_return_value, case_pass):
    ''' Tests for proper file identification '''
    test_path = '/some/path'
    mock_glob.return_value = glob_return_value

    if case_pass:
        resolve_single_path(test_path)
    else:
        with pytest.raises(ValueError):
            resolve_single_path(test_path)
