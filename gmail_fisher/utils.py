import base64
import logging
import os
import re
from pathlib import Path

import coloredlogs as coloredlogs

from gmail_fisher.config import LOG_FORMAT, LOG_LEVEL


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


class FileUtils:
    @classmethod
    def get_payslip_filename(cls, subject: str) -> str:
        match = re.search("[1-9]?[0-9][-][1-9][0-9][0-9][0-9]", subject).group(0)
        date = f"{match.split('-')[1]}-{match.split('-')[0]}"
        return f"PaySlip_{date}.pdf"

    @classmethod
    def save_base64_pdf(cls, base64_string: str, file_path: Path, message_id: str):
        file_data = base64.urlsafe_b64decode(base64_string.encode("UTF-8"))

        if not os.path.isdir(file_path.parent):
            os.mkdir(file_path.parent)
        file_handle = open(file_path, "wb")
        file_handle.write(file_data)
        file_handle.close()
        logger.success(
            f"Successfully saved attachment with {file_path=} and {message_id=}"
        )
