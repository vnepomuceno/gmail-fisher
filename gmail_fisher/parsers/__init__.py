from gmail_fisher.utils import logger


def print_header(title):
    box_size = 40
    box_char = ":"

    logger.info(box_char * 40)
    logger.info(
        f"{box_char * 2} {title.upper()}{' ' * (box_size - len(title) - 5)}{box_char * 2}"
    )
    logger.info(box_char * 40)
