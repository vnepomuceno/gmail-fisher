from pathlib import Path
from typing import Final

# LOGGING
LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "%(asctime)s [%(name)s] <%(levelname)s> %(message)s"

# GMAIL GATEWAY
GMAIL_READ_ONLY_SCOPE: Final[str] = "https://www.googleapis.com/auth/gmail.readonly"
LIST_MESSAGES_MAX_RESULTS: Final[int] = 1000

# PATHS
OUTPUT_PATH: Final[Path] = Path("output/")
TEMP_PATH: Final[Path] = Path("temp/")
AUTH_PATH: Final[Path] = Path("auth/")

# CONCURRENCY
THREAD_POOL_MAX_WORKERS: Final[int] = 200
