# trace_logger.py
import logging

TRACE = logging.DEBUG - 5
# pyright: reportAttributeAccessIssue=false
class TraceLogger(logging.Logger):
    def trace(self, msg, /, *args, **kwargs):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, msg, args, **kwargs)


def install():
    logging.setLoggerClass(TraceLogger)
    logging.addLevelName(TRACE, "TRACE")
