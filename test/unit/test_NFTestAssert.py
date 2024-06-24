"""Test module for NFTestAssert"""

import logging
import stat
import textwrap

import pytest

from nftest.NFTestAssert import NFTestAssert, NotUpdatedError, MismatchedContentsError


@pytest.fixture(name="custom_script", params=[True, False])
def fixture_custom_script(request, tmp_path):
    """
    A fixture to control usage of a custom `script` parameter.

    The custom script will echo a sentinel value to console and call `diff`.
    """
    if not request.param:
        return None

    # Write a custom script that prints out an obvious sentinel value then
    # executes `diff`
    script = tmp_path / "testscript.sh"
    script.write_text(
        textwrap.dedent("""\
        #!/bin/bash
        set -euo pipefail

        echo "THIS_IS_THE_CUSTOM_SCRIPT"

        exec diff "$@"
        """),
        encoding="utf-8",
    )

    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


@pytest.fixture(
    name="method",
    params=[
        "md5",
    ],
)
def fixture_method(request):
    "A fixture for the NFTestAssert `method` argument."
    return request.param


@pytest.fixture(
    name="file_updated",
    params=[
        True,
        pytest.param(
            False, marks=pytest.mark.xfail(strict=True, raises=NotUpdatedError)
        ),
    ],
)
def fixture_file_updated(request):
    "A fixture for whether the actual file was modified during the test."
    return request.param


FILECOUNT_PARAMS = [
    pytest.param(0, marks=pytest.mark.xfail(strict=True, raises=ValueError)),
    1,
    pytest.param(2, marks=pytest.mark.xfail(strict=True, raises=ValueError)),
]


@pytest.fixture(name="actual_count", params=FILECOUNT_PARAMS)
def fixture_actual_count(request):
    "A fixture for the number of actual files in the directory."
    return request.param


@pytest.fixture(name="expect_count", params=FILECOUNT_PARAMS)
def fixture_expect_count(request):
    "A fixture for the number of actual files in the directory."
    return request.param


@pytest.fixture(
    name="file_contents",
    params=[
        ("", ""),
        ("matching", "matching"),
        pytest.param(
            ("something", ""),
            marks=pytest.mark.xfail(strict=True, raises=MismatchedContentsError),
        ),
        pytest.param(
            ("something", "SOMETHING"),
            marks=pytest.mark.xfail(strict=True, raises=MismatchedContentsError),
        ),
    ],
)
def fixture_file_contents(request):
    "A fixture for the contents of the expect and actual files."
    return request.param


@pytest.fixture(name="configured_test")
def fixture_configured_test(
    tmp_path,
    custom_script,
    method,
    expect_count,
    actual_count,
    file_updated,
    file_contents,
):
    """
    A fixture to set up an NFTestAssert referring to a temporary directory.
    """
    for index in range(expect_count):
        expect_file = tmp_path / f"{index}.expect"
        expect_file.write_text(file_contents[0], encoding="utf-8")

    actual_file = None

    for index in range(actual_count):
        actual_file = tmp_path / f"{index}.actual"
        actual_file.write_text(file_contents[1], encoding="utf-8")

    assertion = NFTestAssert(
        expect=str(tmp_path / "*.expect"),
        actual=str(tmp_path / "*.actual"),
        script=custom_script,
        method=method,
    )

    if file_updated and actual_file is not None:
        actual_file.write_bytes(actual_file.read_bytes())

    return assertion


def test_nftest_assert(configured_test, caplog, request):
    "Test that the file update requirement works."
    with caplog.at_level(logging.DEBUG):
        configured_test.perform_assertions()

    used_custom_script = request.getfixturevalue("custom_script") is not None
    flag_in_logs = "THIS_IS_THE_CUSTOM_SCRIPT" in caplog.text

    # The sentinel text should be in the output if and only if the custom
    # script was used
    assert used_custom_script == flag_in_logs
