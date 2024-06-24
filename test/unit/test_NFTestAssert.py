# pylint: disable=W0212
"""Test module for NFTestAssert"""

import datetime

import mock
import pytest

from nftest.NFTestAssert import NFTestAssert


@mock.patch("nftest.NFTestAssert.NFTestAssert", wraps=NFTestAssert)
def test_get_assert_method_value_error(mock_assert):
    """Tests value error from get_assert_method when given `method` is not supported"""
    # Make an NFTestAssert object
    NFTestAssert("", "")

    assert_method = "nomethod"
    mock_assert.return_value.script = None
    mock_assert.return_value.method = assert_method
    mock_assert.return_value._logger.error = lambda x, y: None

    with pytest.raises(ValueError) as val_error:
        mock_assert.get_assert_method(mock_assert())

    assert str(val_error.value) == f"assert method {assert_method} unknown."


@mock.patch("nftest.NFTestAssert.NFTestAssert", wraps=NFTestAssert)
def test_get_assert_method_script(mock_assert):
    """Tests getting script function from get_assert_method"""
    script_method = "path/to/test/script.sh"
    mock_assert.return_value.script = script_method
    mock_assert.return_value._logger.error = lambda x, y: None

    assert callable(mock_assert.get_assert_method(mock_assert()))


@mock.patch("nftest.NFTestAssert.NFTestAssert", wraps=NFTestAssert)
def test_get_assert_method_method(mock_assert):
    """Tests getting method function from get_assert_method"""
    mock_assert.return_value.script = None
    mock_assert.return_value.method = "md5"
    mock_assert.return_value._logger.error = lambda x, y: None

    assert callable(mock_assert.get_assert_method(mock_assert()))


@mock.patch("nftest.NFTestAssert.NFTestAssert", wraps=NFTestAssert)
def test_assert_exists(mock_assert):
    """Tests the functionality of the assert_exists method"""
    # assert_exists() should raise an AssertionError if either or both of
    # actual and expect do not exist.
    # Tuples of (actual.exists(), expect.exists(), raises AssertionError)
    cases = (
        (True, True, False),
        (False, True, True),
        (True, False, True),
        (False, False, True),
    )

    for case in cases:
        mock_assert.return_value.actual.exists.return_value = case[0]
        mock_assert.return_value.expect.exists.return_value = case[1]

        if case[2]:
            with pytest.raises(FileNotFoundError):
                NFTestAssert.assert_exists(mock_assert())
        else:
            NFTestAssert.assert_exists(mock_assert())


@mock.patch("nftest.NFTestAssert.NFTestAssert", wraps=NFTestAssert)
def test_assert_updated(mock_assert):
    """Tests for failing assertion"""
    timestamp = 1689805542.4275217

    mock_assert.return_value.startup_time = datetime.datetime.fromtimestamp(
        timestamp, tz=datetime.timezone.utc
    )

    # Test expected to fail with a time before the start time
    mock_assert.return_value.actual.stat.return_value.st_mtime = timestamp - 1
    with pytest.raises(AssertionError):
        NFTestAssert.assert_updated(mock_assert())

    # Test expected to fail with a time equal to the start time
    mock_assert.return_value.actual.stat.return_value.st_mtime = timestamp
    with pytest.raises(AssertionError):
        NFTestAssert.assert_updated(mock_assert())

    # Test expected to pass with a time after to the start time
    mock_assert.return_value.actual.stat.return_value.st_mtime = timestamp + 1
    NFTestAssert.assert_updated(mock_assert())


@mock.patch("nftest.NFTestAssert.NFTestAssert", wraps=NFTestAssert)
def test_assert_expected(mock_assert):
    """Tests for passing assertion"""
    mock_assert.return_value._logger.error = lambda x, y=None: None

    # A passing test should not raise an error
    mock_assert.return_value.get_assert_method = lambda: lambda x, y: True
    NFTestAssert.assert_expected(mock_assert())

    # A failing test should raise an error
    mock_assert.return_value.get_assert_method = lambda: lambda x, y: False
    with pytest.raises(AssertionError):
        NFTestAssert.assert_expected(mock_assert())


@pytest.mark.parametrize(
    "glob_return_value,case_pass", [([], False), (["a", "b"], False), (["a"], True)]
)
@mock.patch("glob.glob")
@mock.patch("nftest.NFTestAssert.NFTestENV")
@mock.patch("logging.getLogger")
def test_identify_assertions_files(
    mock_getlogger, mock_env, mock_glob, glob_return_value, case_pass
):
    """Tests for proper file identification"""

    mock_glob.return_value = glob_return_value
    mock_env.return_value = None
    mock_getlogger.return_value = lambda x: None

    test_assert = NFTestAssert("", "")

    if case_pass:
        test_assert.identify_assertion_files()
    else:
        with pytest.raises(ValueError):
            test_assert.identify_assertion_files()
