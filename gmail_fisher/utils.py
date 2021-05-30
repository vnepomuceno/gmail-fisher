import base64
import logging
import os
import re


class FileUtils:
    __OUTPUT_DIRECTORY = "gmail_fisher/output/"

    @classmethod
    def get_payslip_filename(cls, subject: str) -> str:
        match = re.search("[1-9]?[0-9][-][1-9][0-9][0-9][0-9]", subject).group(0)
        date = f"{match.split('-')[1]}-{match.split('-')[0]}"
        return f"PaySlip_{date}.pdf"

    @classmethod
    def save_base64_pdf(cls, base64_string: str, file_name: str, message_id: str):
        file_data = base64.urlsafe_b64decode(base64_string.encode("UTF-8"))

        if not os.path.isdir(cls.__OUTPUT_DIRECTORY):
            os.mkdir(cls.__OUTPUT_DIRECTORY)
        file_handle = open(f"{cls.__OUTPUT_DIRECTORY}{file_name}", "wb")
        file_handle.write(file_data)
        file_handle.close()
        logging.info(
            f"Successfully saved attachment with filename='{file_name}' and message_id='{message_id}'"
        )
