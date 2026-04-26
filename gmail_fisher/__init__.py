import logging
import os

from rich.console import Console
from rich.logging import RichHandler

from gmail_fisher.utils.config import LOG_LEVEL

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
console = Console()

logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, "SUCCESS")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(message)s",
    handlers=[
        RichHandler(
            console=console,
            show_path=True,
            markup=True,
            log_time_format="[%X]",
            rich_tracebacks=True,
        )
    ],
)


def get_logger(name: str) -> logging.Logger:
    custom_logger = logging.getLogger(name)
    setattr(
        custom_logger,
        "success",
        lambda message, *args: console.print(f"  [bold green]✓[/bold green]  {message}"),
    )
    return custom_logger


logger = get_logger(__name__)
