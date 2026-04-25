from pathlib import Path
from typing import Final

# LOGGING
LOG_LEVEL: Final[str] = "INFO"

# GMAIL GATEWAY
GMAIL_READ_ONLY_SCOPE: Final[str] = "https://www.googleapis.com/auth/gmail.readonly"
LIST_MESSAGES_MAX_RESULTS: Final[int] = 1000

# PATHS
OUTPUT_PATH: Final[Path] = Path("output/")
TEMP_PATH: Final[Path] = Path("temp/")
AUTH_PATH: Final[Path] = Path("auth/")

# CONCURRENCY
THREAD_POOL_MAX_WORKERS: Final[int] = 50  # Reduced from 200 to avoid overwhelming the API

# API RESILIENCE
REQUEST_TIMEOUT: Final[int] = 30  # Timeout for individual API requests in seconds
MAX_RETRIES: Final[int] = 3  # Maximum number of retries for failed requests
RETRY_DELAY: Final[float] = 1.0  # Initial delay between retries in seconds
RETRY_BACKOFF_FACTOR: Final[float] = 2.0  # Exponential backoff multiplier
