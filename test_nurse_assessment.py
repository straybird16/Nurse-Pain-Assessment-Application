"""Focused tests for nurse-score recording and PAINAD toggle behavior."""

import csv
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from config import CSV_HEADERS
from gui import PainadRecorderApp
from painad import toggled_score
from recorder import AssessmentRecord, CsvRecorder


class _FakeVariable:
    def __init__(self, value: int | str) -> None:
        self.value = value

    def get(self) -> int | str:
        return self.value

    def set(self, value: int | str) -> None:
        self.value = value


class _FakeButton:
    def __init__(self) -> None:
        self.options: dict[str, object] = {}

    def configure(self, **options: object) -> None:
        self.options.update(options)


class _CountingRecorder:
    def __init__(self) -> None:
        self.append_calls = 0

    def append(self, _record: AssessmentRecord) -> Path:
        self.append_calls += 1
        return Path("unexpected.csv")


class PainadToggleTests(unittest.TestCase):
    def test_same_button_deselects_and_other_button_replaces_selection(self) -> None:
        self.assertEqual(1, toggled_score(None, 1))
        self.assertIsNone(toggled_score(1, 1))
        self.assertEqual(2, toggled_score(1, 2))

    def test_painad_toggle_does_not_record(self) -> None:
        app = PainadRecorderApp.__new__(PainadRecorderApp)
        app.selection_vars = {"breathing": _FakeVariable(-1)}
        app.painad_buttons = {
            "breathing": {score: _FakeButton() for score in range(3)}
        }
        app.total_var = _FakeVariable("")
        app.recorder = _CountingRecorder()

        app._toggle_painad("breathing", 1)
        self.assertEqual(1, app.selection_vars["breathing"].get())
        self.assertEqual(
            "PainadSelected.TButton",
            app.painad_buttons["breathing"][1].options["style"],
        )
        self.assertEqual(0, app.recorder.append_calls)

        app._toggle_painad("breathing", 1)
        self.assertEqual(-1, app.selection_vars["breathing"].get())
        self.assertEqual(
            "Painad.TButton",
            app.painad_buttons["breathing"][1].options["style"],
        )
        self.assertEqual(0, app.recorder.append_calls)


class RecorderTests(unittest.TestCase):
    def test_nurse_score_records_when_all_optional_fields_are_blank(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            recorder = CsvRecorder(Path(temporary_directory))
            path = recorder.append(
                AssessmentRecord(
                    subject="P001",
                    session="Visit1",
                    breathing=None,
                    negative_vocalization=None,
                    facial_expression=None,
                    body_language=None,
                    consolability=None,
                    painad_total=None,
                    estimated_pain=6.5,
                    notes="",
                ),
                recorded_at=datetime(2026, 7, 29, 14, 30, tzinfo=timezone.utc),
            )

            with path.open("r", encoding="utf-8", newline="") as csv_file:
                rows = list(csv.DictReader(csv_file))

            self.assertEqual(list(CSV_HEADERS), list(rows[0]))
            self.assertEqual("6.5", rows[0]["estimated_pain"])
            for field in (
                "breathing",
                "negative_vocalization",
                "facial_expression",
                "body_language",
                "consolability",
                "painad_total",
                "notes",
            ):
                self.assertEqual("", rows[0][field])

    def test_note_line_breaks_are_stored_as_literal_backslash_n(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            recorder = CsvRecorder(Path(temporary_directory))
            path = recorder.append(
                AssessmentRecord(
                    subject="P001",
                    session="1",
                    breathing=None,
                    negative_vocalization=None,
                    facial_expression=None,
                    body_language=None,
                    consolability=None,
                    painad_total=None,
                    estimated_pain=4.0,
                    notes="first\r\nsecond\nthird\rfourth",
                ),
                recorded_at=datetime(2026, 7, 29, 14, 30, tzinfo=timezone.utc),
            )

            with path.open("r", encoding="utf-8", newline="") as csv_file:
                rows = list(csv.DictReader(csv_file))

            self.assertEqual(r"first\nsecond\nthird\nfourth", rows[0]["notes"])
            self.assertEqual(2, len(path.read_text(encoding="utf-8").splitlines()))


if __name__ == "__main__":
    unittest.main()
