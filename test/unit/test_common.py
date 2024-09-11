# pylint: disable=W0212
"""Test module for common functions"""

import logging
import mock
import pytest

from nftest.common import validate_reference


@pytest.mark.parametrize(
    "param_name,valid_name",
    [
        ("bad name", False),
        ("good_name", True),
        ("bad#name", False),
        ("validparam", True),
    ],
)
@mock.patch("nftest.common.calculate_checksum")
def test_param_names_validate_reference(
    mock_calculate_checksum, param_name, valid_name
):
    """Tests for proper parameter name check"""
    mock_calculate_checksum.return_value = ""
    if valid_name:
        validate_reference(param_name, "", "", "")
    else:
        with pytest.raises(ValueError):
            validate_reference(param_name, "", "", "")


@mock.patch("nftest.common.calculate_checksum")
def test_warning_with_bad_checksum_validate_reference(mock_calculate_checksum, caplog):
    """Tests for warning message printed with bad checksum"""
    test_bad_checksum = "bad_checksum"
    test_param_name = "name"
    test_param_path = "path"
    test_checksum = "checksum"
    test_checksum_type = "md5"

    mock_calculate_checksum.return_value = test_bad_checksum

    with caplog.at_level(logging.DEBUG):
        validate_reference(
            test_param_name, test_param_path, test_checksum, test_checksum_type
        )

    assert (
        f"Checksum for reference file: "
        f"{test_param_name}={test_param_path} - `"
        f"{test_bad_checksum}` does not match expected "
        f"checksum of `{test_checksum}`" in caplog.text
    )


@mock.patch("nftest.common.calculate_checksum")
def test_returns_correct_tuple_validate_reference(mock_calculate_checksum):
    """Tests for correct return tuple after validation"""
    test_param_name = "name"
    test_param_path = "path"
    test_checksum = "checksum"
    test_checksum_type = "md5"

    mock_calculate_checksum.return_value = test_checksum

    validated_reference = validate_reference(
        test_param_name, test_param_path, test_checksum, test_checksum_type
    )

    assert validated_reference == (test_param_name, test_param_path)
