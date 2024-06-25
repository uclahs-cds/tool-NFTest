"Local plugin to intelligently combine xfail marks."

import pytest


def pytest_configure(config):
    "Hook to add in the custom marker."
    config.addinivalue_line(
        "markers",
        "xfailgroup(ExceptionClass): Mark that the test is expected to fail with "
        "the given exception type. If xfailgroup is applied multiple times, the "
        "test will pass if it raises any of the exception types.",
    )


@pytest.hookimpl(trylast=True)
def pytest_runtest_setup(item):
    "Merge all of the xfailgroup markers into a single xfail marker."
    failure_types = {mark.args[0] for mark in item.iter_markers(name="xfailgroup")}
    if failure_types:
        item.add_marker(pytest.mark.xfail(raises=tuple(failure_types)))
