"""
Module for a system to capture Nextflow logs via syslog.
"""
import logging
import re
import socketserver


LEVELS = [
    logging.CRITICAL,   # 0 = Emergency
    logging.CRITICAL,   # 1 = Alert
    logging.CRITICAL,   # 2 = Critical
    logging.ERROR,      # 3 = Error
    logging.WARNING,    # 4 = Warning
    logging.INFO,       # 5 = Notice
    logging.INFO,       # 6 = Info
    logging.DEBUG,      # 7 = Debug
]

SYSLOG_RE = re.compile(r"""
    ^                               # Start of line
    <(?P<priority>\d+)>             # Priority
    (?P<month>\w{3})\s              # Month
    (?P<day>(?:\s|\d)\d)\s          # Day (with optional leading space)
    (?P<time>\d{2}:\d{2}:\d{2})\s   # Time
    (?P<hostname>\S+)\s             # Hostname
    (?P<message>.*)                 # Message
    $                               # End of line
    """, re.VERBOSE | re.DOTALL)
MESSAGE_RE = re.compile(r"^nextflow:\s+\w+\s+\[(?P<thread>.+?)\] \S+ - ")


def syslog_filter(record):
    """
    Logging filter to update syslogs from Nextflow with embedded information.
    """
    if not isinstance(record.msg, bytes):
        # This isn't a well-formatted syslog message - don't modify it
        return record

    # Nextflow uses BSD-style syslog messages
    # https://datatracker.ietf.org/doc/html/rfc3164
    # Format / example:
    # <PRI>Mmm dd hh:mm:ss HOSTNAME MESSAGE"
    # <134>Jan  3 12:00:25 ip-0A125232 nextflow: INFO  [main] more...
    # Ignore the embedded date for simplicity

    syslog_match = SYSLOG_RE.match(record.msg.strip().decode("utf-8"))

    if not syslog_match:
        # This isn't a well-formatted syslog message - don't modify it
        return record

    syslog_priority = int(syslog_match.group("priority")) % 8

    # The priority is 8 * facility + level - we only care about the level
    record.levelno = LEVELS[syslog_priority]
    record.levelname = logging.getLevelName(record.levelno)

    # For most messages, nextflow seems to have a format of:
    # nextflow: LEVEL [THREAD] MODULE - MESSAGE
    #
    # nextflow: DEBUG [main] ConfigBuilder - User config file...
    # nextflow: INFO  [main] DefaultPluginStatusProvider - Enabled...
    # nextflow: ERROR [main] Launcher - Unable...

    # Strip off everything before the module if possible
    message = syslog_match.group("message")

    thread_match = MESSAGE_RE.match(message)
    if thread_match:
        record.msg = MESSAGE_RE.sub("", message)
        record.threadName = thread_match.group("thread")
    else:
        record.msg = message
        record.threadName = "traceback"

    return record


class SyslogServer(socketserver.ThreadingUDPServer):
    "A UDPServer that logs itself starting up and shutting down."
    @classmethod
    def make_server(cls):
        "Create a server with a random port to handle syslogs."
        return cls(
            server_address=("127.0.0.1", 0),
            RequestHandlerClass=SyslogHandler
        )

    def serve_forever(self, poll_interval=0.5):
        logging.getLogger(__name__).debug(
            "Syslog server at %s:%d starting up",
            *self.server_address
        )
        return super().serve_forever(poll_interval)

    def shutdown(self):
        logging.getLogger(__name__).debug(
            "Syslog server at %s:%d shutting down",
            *self.server_address
        )
        return super().shutdown()


class SyslogHandler(socketserver.BaseRequestHandler):
    "A simple syslog-like server to capture formatted logs from Nextflow."
    def handle(self):
        # This is a syslog message from Nextflow
        logging.getLogger("nextflow").info(self.request[0])
