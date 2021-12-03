from pathlib import Path
from typing import Final

# LOGGING
LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[
    str
] = "%(asctime)s [%(name)s] (%(threadName)s) <%(levelname)s> %(message)s"

# GMAIL AUTHORIZATION
GMAIL_READ_ONLY_SCOPE: Final[str] = "https://www.googleapis.com/auth/gmail.readonly"

# PATHS
OUTPUT_PATH: Final[Path] = Path("output/")
AUTH_PATH: Final[Path] = Path("auth/")

# CONCURRENCY
THREAD_POOL_MAX_WORKERS: Final[int] = 200
