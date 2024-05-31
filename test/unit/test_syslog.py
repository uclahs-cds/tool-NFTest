"""Test module for the syslog filter."""

import logging

from nftest.syslog import syslog_filter, LEVELS


def test_syslog_filter(caplog):
    "Test that the syslog filter works appropriately."
    caplog.set_level(logging.DEBUG)
    logging.getLogger("nextflow").addFilter(syslog_filter)

    # This is a well-formatted syslog message
    logging.getLogger("nextflow").info(
        b"<132>Jan  3 12:00:25 ip-0A125232 "
        b"nextflow: ERROR [main] Launcher - Unable..."
    )

    # A priority of 132 should correspond to a severity of 4, or WARNING
    assert 132 % 8 == 4
    assert LEVELS[4] == logging.WARNING

    assert len(caplog.records) == 1
    record = caplog.records[0]

    # The record level comes from `<132>`, not `ERROR`
    assert record.levelno == logging.WARNING
    assert record.msg == "Unable..."
    assert record.name == "nextflow"
    assert record.threadName == "main"

    # This message has a higher priority
    logging.getLogger("nextflow").info(
        b"<130>Jan  3 12:00:25 ip-0A125232 "
        b"nextflow: ERROR [main] Launcher - Unable..."
    )

    assert 130 % 8 == 2
    assert LEVELS[2] == logging.CRITICAL

    assert caplog.record_tuples[-1] == ("nextflow", logging.CRITICAL, "Unable...")


def test_syslog_filter_multline(caplog):
    "Test that the syslog filter handles multiline messages."
    caplog.set_level(logging.DEBUG)
    logging.getLogger("nextflow").addFilter(syslog_filter)

    # This is a well-formatted syslog message
    logging.getLogger("nextflow").info(
        b"<131>Jan  3 12:00:25 ip-0A125232 "
        b"nextflow: ERROR [main] Launcher - Unable\nto\nact"
    )

    assert len(caplog.records) == 1
    record = caplog.records[0]

    assert record.levelno == logging.ERROR
    assert record.msg == "Unable\nto\nact"
    assert record.name == "nextflow"
    assert record.threadName == "main"


def test_syslog_filter_nonformatted(caplog):
    "Test that the syslog filter can handle poorly formatted messages."
    caplog.set_level(logging.DEBUG)
    logging.getLogger("nextflow").addFilter(syslog_filter)

    logging.getLogger("nextflow").debug("hello")
    logging.getLogger("nextflow").debug(b"hello")

    assert caplog.record_tuples == [
        ("nextflow", logging.DEBUG, "hello"),
        ("nextflow", logging.DEBUG, str(b"hello")),
    ]


def test_syslog_filter_traceback(caplog):
    "Test that the syslog filter properly handles tracebacks."
    caplog.set_level(logging.DEBUG)
    logging.getLogger("nextflow").addFilter(syslog_filter)

    # This is a well-formatted syslog message, but not a well-formatted
    # Nextflow message. That generally means that it is a traceback.
    message = b"<132>Jan  3 12:00:25 ip-0A125232 random message"

    logging.getLogger("nextflow").debug(message)

    assert len(caplog.records) == 1
    record = caplog.records[0]

    assert record.levelno == logging.WARNING
    assert record.msg == "random message"
    assert record.threadName == "traceback"
