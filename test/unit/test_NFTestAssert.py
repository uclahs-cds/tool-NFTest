"""Test module for NFTestAssert"""

import datetime
import logging
import stat
import textwrap
import time
from collections import namedtuple

import pytest

from nftest.NFTestAssert import NFTestAssert, NotUpdatedError, MismatchedContentsError


@pytest.fixture(name="custom_script")
def fixture_custom_script(request, tmp_path):
    """
    A fixture to control usage of a custom `script` parameter.

    The fixture returns the tuple (script_path, sentinel_value).

    The custom script will echo a sentinel value to console and call `diff`.
    """
    Script = namedtuple("Script", ["script", "sentinel"])

    if not request.param:
        return Script(None, None)

    sentinel = "THIS_IS_THE_CUSTOM_SCRIPT"

    # Write a custom script that prints out an obvious sentinel value then
    # executes `diff`
    script = tmp_path / "testscript.sh"
    script.write_text(
        textwrap.dedent(f"""\
        #!/bin/bash
        set -euo pipefail

        echo "{sentinel}"

        exec diff "$@"
        """),
        encoding="utf-8",
    )

    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return Script(script, sentinel)


@pytest.fixture(name="method")
def fixture_method(request):
    "A fixture for the NFTestAssert `method` argument."
    return request.param


@pytest.fixture(name="file_contents")
def fixture_file_contents(request):
    """
    A fixture for the contents of the expect and actual files.

    Returns the tuple (actual_text, expect_text).
    """
    return request.param


FileList = namedtuple("FileList", ["paths", "glob"])


@pytest.fixture(name="actual_files")
def fixture_actual_files(request, file_contents, tmp_path):
    """
    A fixture to create 'actual' files in the temporary directory.

    These files are explicitly created before the NFTestAssert object is
    instantiated.

    The fixture returns the tuple (list-of-files, glob).
    """
    files = []
    for index in range(request.param):
        actual_file = tmp_path / f"{index}.actual"
        actual_file.write_text(file_contents[0], encoding="utf-8")
        files.append(actual_file)

    return FileList(files, str(tmp_path / "*.actual"))


@pytest.fixture(name="expect_files")
def fixture_expect_files(request, file_contents, tmp_path):
    """
    A fixture to create 'expect' files in the temporary directory.

    The fixture returns the tuple (list-of-files, glob).
    """
    files = []
    for index in range(request.param):
        expect_file = tmp_path / f"{index}.expect"
        expect_file.write_text(file_contents[1], encoding="utf-8")
        files.append(expect_file)

    return FileList(files, str(tmp_path / "*.expect"))


@pytest.fixture(name="configured_test")
def fixture_configured_test(
    custom_script,
    method,
    expect_files,
    actual_files,
):
    """
    A fixture to set up an NFTestAssert referring to a temporary directory.

    The NFTestAssert is instantiated after the actual files, so by default
    perform_assertions() should fail with a NotUpdatedError.
    """
    assertion = NFTestAssert(
        expect=expect_files.glob,
        actual=actual_files.glob,
        script=custom_script.script,
        method=method,
    )

    return assertion


# Parameterization for the number of expected and actual files matching the
# globs. Failure is expected for anything except 1.
FILECOUNT_PARAMS = [
    pytest.param(0, marks=pytest.mark.xfailgroup.with_args(ValueError)),
    1,
    pytest.param(2, marks=pytest.mark.xfailgroup.with_args(ValueError)),
]


# Parameterization for the contents of the expected and actual files. Failure
# is expected if the contents do not match.
FILECONTENT_PARAMS = [
    ("", ""),
    ("matching", "matching"),
    pytest.param(
        ("something", ""),
        marks=pytest.mark.xfailgroup.with_args(MismatchedContentsError),
    ),
    pytest.param(
        ("something", "SOMETHING"),
        marks=pytest.mark.xfailgroup.with_args(MismatchedContentsError),
    ),
]

# Parameterization for whether the actual file was updated since the creation
# of the NFTestAssert. Failure is expected if this is false.
FILEUPDATED_PARAMS = [
    True,
    pytest.param(False, marks=pytest.mark.xfailgroup.with_args(NotUpdatedError)),
]


@pytest.mark.parametrize("file_updated", FILEUPDATED_PARAMS)
@pytest.mark.parametrize("custom_script", [True, False], indirect=True)
@pytest.mark.parametrize(
    "method",
    [
        "md5",
    ],
    indirect=True,
)
@pytest.mark.parametrize("expect_files", FILECOUNT_PARAMS, indirect=True)
@pytest.mark.parametrize("actual_files", FILECOUNT_PARAMS, indirect=True)
@pytest.mark.parametrize("file_contents", FILECONTENT_PARAMS, indirect=True)
def test_nftest_assert(
    configured_test, caplog, custom_script, actual_files, file_updated
):
    "Test that assertions appropriately pass or fail based on the parameters."
    if file_updated:
        # Wait up to 1 second for each file's mtime to update before aborting
        acceptable_wait = datetime.timedelta(seconds=1)

        for actual_file in actual_files.paths:
            wall_time = datetime.datetime.now()
            prior_time = datetime.datetime.fromtimestamp(
                actual_file.stat().st_mtime, tz=datetime.timezone.utc
            )

            while True:
                actual_file.touch()

                updated_time = datetime.datetime.fromtimestamp(
                    actual_file.stat().st_mtime, tz=datetime.timezone.utc
                )

                if updated_time > prior_time:
                    break

                if datetime.datetime.now() - wall_time > acceptable_wait:
                    raise RuntimeError("Filesystem timings broken")

                # Sleep for 50 milliseconds before trying again
                time.sleep(0.05)

    with caplog.at_level(logging.DEBUG):
        configured_test.perform_assertions()

    used_custom_script = custom_script.script is not None
    flag_in_logs = (
        custom_script.sentinel is not None and custom_script.sentinel in caplog.text
    )

    # The sentinel text should be in the output if and only if the custom
    # script was used
    assert used_custom_script == flag_in_logs
