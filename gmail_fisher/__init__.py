import logging
import os

import coloredlogs

from gmail_fisher.utils.config import LOG_LEVEL, LOG_FORMAT


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_logger(name: str) -> logging.Logger:
    coloredlogs.install()
    custom_logger = logging.getLogger(name)
    logging.SUCCESS = 25  # between WARNING and INFO
    logging.addLevelName(logging.SUCCESS, "SUCCESS")
    setattr(
        custom_logger,
        "success",
        lambda message, *args: custom_logger._log(logging.SUCCESS, message, args),
    )
    coloredlogs.install(
        level=LOG_LEVEL,
        logger=custom_logger,
        fmt=LOG_FORMAT,
    )

    return custom_logger


logger = get_logger(__name__)
