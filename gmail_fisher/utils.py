import base64
import logging
import os
import re

import coloredlogs as coloredlogs

from gmail_fisher.config import OUTPUT_PATH, LOG_FORMAT, LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    coloredlogs.install()
    custom_logger = logging.getLogger(name)
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
    def save_base64_pdf(cls, base64_string: str, file_name: str, message_id: str):
        file_data = base64.urlsafe_b64decode(base64_string.encode("UTF-8"))

        if not os.path.isdir(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        filepath = OUTPUT_PATH / file_name
        file_handle = open(filepath, "wb")
        file_handle.write(file_data)
        file_handle.close()
        logger.info(f"Successfully saved attachment with {filepath=} and {message_id=}")
