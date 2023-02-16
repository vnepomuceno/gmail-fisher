import base64
import os
from pathlib import Path

from gmail_fisher import logger


class FileUtils:
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
