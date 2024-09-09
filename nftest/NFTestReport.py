"""Test summary report."""

import datetime
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path


class DateEncoder(json.JSONEncoder):
    """Simple encoder that handles datetimes."""
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)


@dataclass
class TestReport:
    """Test summary report."""

    start: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc)
    )

    passed_tests: list[str] = field(default_factory=list)
    skipped_tests: list[str] = field(default_factory=list)
    failed_tests: list[str] = field(default_factory=list)

    def __bool__(self):
        return not self.failed_tests

    def write_report(self, reportfile: Path):
        """Write the report out to the given file."""
        data = asdict(self)

        # Add extra parameters
        data["end"] = datetime.datetime.now(tz=datetime.timezone.utc)
        data["success"] = not self.failed_tests

        with reportfile.open(mode="wt", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=2, cls=DateEncoder)
