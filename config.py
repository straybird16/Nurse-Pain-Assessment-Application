"""Application-wide constants."""

from pathlib import Path

APP_TITLE = "PAINAD Recorder"
APP_DIRECTORY = Path(__file__).resolve().parent
RECORDS_DIRECTORY = APP_DIRECTORY / "records"

CSV_HEADERS = (
    "unix_ms",
    "iso_time",
    "local_time",
    "subject",
    "session",
    "breathing",
    "negative_vocalization",
    "facial_expression",
    "body_language",
    "consolability",
    "painad_total",
    "estimated_pain",
    "notes",
)
