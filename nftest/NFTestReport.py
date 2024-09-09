"""Test summary report."""

import datetime
import json
import os

from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path

from nftest.common import TestResult
from nftest.NFTestCase import NFTestCase


class DateEncoder(json.JSONEncoder):
    """Simple encoder that handles datetimes."""
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)


@dataclass
class NFTestReport:
    """Test summary report."""

    start: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc)
    )

    passed_tests: dict[str, float] = field(default_factory=dict)
    skipped_tests: dict[str, float] = field(default_factory=dict)
    errored_tests: dict[str, float] = field(default_factory=dict)
    failed_tests: dict[str, float] = field(default_factory=dict)

    def __bool__(self):
        return not self.failed_tests

    @contextmanager
    def track_test(self, test: NFTestCase):
        """Context manager to track test statuses and runtimes."""
        start_time = datetime.datetime.now()

        result_map = {
            TestResult.PASSED: self.passed_tests,
            TestResult.SKIPPED: self.skipped_tests,
            TestResult.ERRORED: self.errored_tests,
            TestResult.FAILED: self.failed_tests,
            TestResult.PENDING: {}
        }

        try:
            yield
        finally:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            result_map[test.status][test.name] = duration

    def write_report(self, reportfile: Path):
        """Write the report out to the given file."""
        data = asdict(self)

        # Add extra parameters
        data["cpus"] = os.cpu_count()
        data["end"] = datetime.datetime.now(tz=datetime.timezone.utc)
        data["success"] = not self.failed_tests and not self.errored_tests

        with reportfile.open(mode="wt", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=2, cls=DateEncoder)
