"""Logger Module."""
import logging
from logging import Logger

import niceshare

""" Logger Module"""

class RelativeSeconds(logging.Formatter):
    """Logger formaating overwrite to display seconds (instead of miliseconds)."""
    def format(self, record):
        """Convert miliseconds to seconds.

        Args:
            record: Time in miliseconds
        """
        record.relativeCreated = record.relativeCreated // 1000
        return super().format(record)


formatter = RelativeSeconds(
    "%(relativeCreated)ds %(levelname)s %(name)s.%(module)s.%(funcName)s: %(message)s"
    )

# Get Logger and set log level
logging.basicConfig()
LOGGER: Logger = logging.getLogger(name=niceshare.__name__)
LOGGER.root.handlers[0].setFormatter(formatter)
