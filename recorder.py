"""CSV persistence for PAINAD assessments."""

import csv
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config import CSV_HEADERS


@dataclass(frozen=True)
class AssessmentRecord:
    """Values collected from one assessment."""

    subject: str
    session: str
    breathing: int | None
    negative_vocalization: int | None
    facial_expression: int | None
    body_language: int | None
    consolability: int | None
    painad_total: int | None
    estimated_pain: float
    notes: str


class CsvRecorder:
    """Write one CSV per session and undo rows from the active session."""

    def __init__(self, output_directory: Path) -> None:
        self.output_directory = output_directory
        self._session_path: Path | None = None
        self._session_identity: tuple[str, str] | None = None
        self._recorded_rows = 0

    @property
    def session_path(self) -> Path | None:
        """Return the active session file, if recording has started."""
        return self._session_path

    @property
    def can_undo(self) -> bool:
        """Return whether this session has a row available to undo."""
        return self._recorded_rows > 0

    def append(
        self,
        record: AssessmentRecord,
        recorded_at: datetime | None = None,
    ) -> Path:
        """Append one assessment and return the file used."""
        timestamp = recorded_at or datetime.now().astimezone()
        if timestamp.tzinfo is None:
            timestamp = timestamp.astimezone()

        self.output_directory.mkdir(parents=True, exist_ok=True)
        identity = (record.subject, record.session)
        if self._session_identity is not None and identity != self._session_identity:
            raise ValueError("Subject ID and Session ID cannot change during a session.")

        is_new_session = self._session_path is None
        unix_ms = int(timestamp.timestamp() * 1_000)
        row = (
            unix_ms,
            timestamp.isoformat(timespec="milliseconds"),
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            record.subject,
            record.session,
            _optional_score(record.breathing),
            _optional_score(record.negative_vocalization),
            _optional_score(record.facial_expression),
            _optional_score(record.body_language),
            _optional_score(record.consolability),
            _optional_score(record.painad_total),
            f"{record.estimated_pain:.1f}",
            _single_line_notes(record.notes),
        )

        if is_new_session:
            while True:
                path = self._new_session_path(record, timestamp)
                try:
                    with path.open("x", encoding="utf-8", newline="") as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(CSV_HEADERS)
                        writer.writerow(row)
                    break
                except FileExistsError:
                    continue
        else:
            path = self._session_path
            if path is None:  # Kept explicit for type checkers.
                raise RuntimeError("Active session has no CSV path.")
            needs_header = not path.exists() or path.stat().st_size == 0
            with path.open("a", encoding="utf-8", newline="") as csv_file:
                writer = csv.writer(csv_file)
                if needs_header:
                    writer.writerow(CSV_HEADERS)
                writer.writerow(row)

        if is_new_session:
            self._session_path = path
            self._session_identity = identity
        self._recorded_rows += 1
        return path

    def undo_last(self) -> Path | None:
        """Undo the latest row recorded in the active session."""
        if self._session_path is None or self._recorded_rows == 0:
            return None
        path = self._session_path
        if not path.exists():
            raise FileNotFoundError(path)

        with path.open("r", encoding="utf-8", newline="") as csv_file:
            rows = list(csv.reader(csv_file))

        if len(rows) <= 1:
            raise ValueError(f"No data rows found in {path.name}")
        if tuple(rows[0]) != CSV_HEADERS:
            raise ValueError(f"Unexpected CSV header in {path.name}")

        temporary_path = path.with_name(f".{path.name}.tmp")
        try:
            with temporary_path.open("w", encoding="utf-8", newline="") as csv_file:
                csv.writer(csv_file).writerows(rows[:-1])
            os.replace(temporary_path, path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

        self._recorded_rows -= 1
        return path

    def end_session(self) -> Path | None:
        """Close the active session and clear its in-memory undo history."""
        path = self._session_path
        self._session_path = None
        self._session_identity = None
        self._recorded_rows = 0
        return path

    def _new_session_path(
        self,
        record: AssessmentRecord,
        timestamp: datetime,
    ) -> Path:
        subject = _filename_slug(record.subject, "unknown-subject")
        session = _filename_slug(record.session, "unknown-session")
        base_name = f"{subject}_{session}_painad_{timestamp:%Y-%m-%d_%H%M%S}"
        path = self.output_directory / f"{base_name}.csv"
        suffix = 2

        while path.exists():
            path = self.output_directory / f"{base_name}_{suffix:03d}.csv"
            suffix += 1
        return path


def _filename_slug(value: str, fallback: str) -> str:
    """Make a short cross-platform-safe filename component."""
    slug = re.sub(r"[^\w-]+", "_", value.strip()).strip("_-")
    return slug[:48] or fallback


def _optional_score(value: int | None) -> int | str:
    """Write unselected optional PAINAD values as empty CSV fields."""
    return "" if value is None else value


def _single_line_notes(notes: str) -> str:
    r"""Store note line breaks as literal ``\n`` text inside one CSV line."""
    normalized = notes.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.replace("\n", r"\n")
