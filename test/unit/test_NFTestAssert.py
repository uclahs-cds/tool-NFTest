# pylint: disable=W0212
''' Test module for NFTestAssert '''
import mock
import pytest
from nftest.NFTestAssert import NFTestAssert

@mock.patch('nftest.NFTestAssert.NFTestAssert', wraps=NFTestAssert)
def test_get_assert_method_value_error(mock_assert):
    ''' Tests value error from get_assert_method when given `method` is not supported '''
    assert_method = 'nomethod'
    mock_assert.return_value.script = None
    mock_assert.return_value.method = assert_method
    mock_assert.return_value._logger.error = lambda x, y: None

    with pytest.raises(ValueError) as val_error:
        mock_assert.get_assert_method(mock_assert())

    assert str(val_error.value) == f'assert method {assert_method} unknown.'

@mock.patch('nftest.NFTestAssert.NFTestAssert', wraps=NFTestAssert)
def test_get_assert_method_script(mock_assert):
    ''' Tests getting script function from get_assert_method '''
    script_method = 'path/to/test/script.sh'
    mock_assert.return_value.script = script_method
    mock_assert.return_value._logger.error = lambda x, y: None

    assert callable(mock_assert.get_assert_method(mock_assert()))

@mock.patch('nftest.NFTestAssert.NFTestAssert', wraps=NFTestAssert)
def test_get_assert_method_method(mock_assert):
    ''' Tests getting method function from get_assert_method '''
    mock_assert.return_value.script = None
    mock_assert.return_value.method = 'md5'
    mock_assert.return_value._logger.error = lambda x, y: None

    assert callable(mock_assert.get_assert_method(mock_assert()))

@mock.patch('nftest.NFTestAssert.Path')
@mock.patch('nftest.NFTestAssert.NFTestAssert', wraps=NFTestAssert)
def test_assert_expected_fail(mock_assert, mock_path):
    ''' Tests for failing assertion '''
    test_path = '/A/path/for/tests'
    mock_path.return_value.exists = lambda: True
    mock_assert.return_value.actual = test_path
    mock_assert.return_value.expect = test_path
    mock_assert.return_value.get_assert_method = lambda: lambda x, y: False
    mock_assert.return_value._logger.error = lambda x, y=None: None
    mock_assert.return_value.mock_assert_expected = NFTestAssert.assert_expected

    with pytest.raises(AssertionError):
        mock_assert().mock_assert_expected(mock_assert())

@mock.patch('nftest.NFTestAssert.Path')
@mock.patch('nftest.NFTestAssert.NFTestAssert', wraps=NFTestAssert)
def test_assert_expected_pass(mock_assert, mock_path):
    ''' Tests for passing assertion '''
    test_path = '/A/path/for/tests'
    mock_path.return_value.exists = lambda: True
    mock_assert.return_value.actual = test_path
    mock_assert.return_value.expect = test_path
    mock_assert.return_value.get_assert_method = lambda: lambda x, y: True
    mock_assert.return_value._logger.error = lambda x, y=None: None
    # Mock the method being tested since pytest doesn't allow attributes starting with "assert"
    mock_assert.return_value.mock_assert_expected = NFTestAssert.assert_expected

    assert mock_assert().mock_assert_expected(mock_assert()) is None
