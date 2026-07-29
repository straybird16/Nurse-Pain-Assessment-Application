"""Tkinter interface for the PAINAD recorder."""

import csv
import math
import textwrap
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from config import APP_TITLE
from painad import PAINAD_ITEMS, toggled_score
from recorder import AssessmentRecord, CsvRecorder

BACKGROUND = "#F3F6FA"
CARD = "#FFFFFF"
TEXT = "#172033"
MUTED = "#52606D"
BORDER = "#C9D5E2"
PRIMARY = "#1D4ED8"
PRIMARY_ACTIVE = "#1E40AF"
SECONDARY = "#475569"
SECONDARY_ACTIVE = "#334155"
END_SESSION = "#9A3412"
END_SESSION_ACTIVE = "#7C2D12"
SCORE_BACKGROUND = "#E8F0FE"
SUCCESS = "#166534"
PAINAD_SELECTED = "#DCFCE7"
PAINAD_SELECTED_ACTIVE = "#BBF7D0"
PAINAD_SELECTED_TEXT = "#14532D"
DEFAULT_SESSION_ID = "1"


class PainadRecorderApp:
    """Build and coordinate the application's single window."""

    def __init__(self, root: tk.Tk, recorder: CsvRecorder) -> None:
        self.root = root
        self.recorder = recorder
        self.selection_vars: dict[str, tk.IntVar] = {}
        self.painad_buttons: dict[str, dict[int, ttk.Button]] = {}
        self.estimate_buttons: dict[int, ttk.Button] = {}
        self.mode_buttons: dict[str, ttk.Button] = {}
        self.status_var = tk.StringVar()
        self.file_var = tk.StringVar(value="CSV: created with the first record")
        self.total_var = tk.StringVar(value="— (0/5 selected)")
        self.estimated_var = tk.DoubleVar(value=0.0)
        self.estimated_display_var = tk.StringVar(value="0.0")
        self.estimated_mode_var = tk.StringVar(value="buttons")
        self._status_timer: str | None = None

        self._configure_window()
        self._build_interface()
        self._bind_shortcuts()

    def _configure_window(self) -> None:
        self.root.title(APP_TITLE)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(980, max(800, screen_width - 100))
        window_height = min(900, max(720, screen_height - 80))
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(min(900, window_width), min(810, window_height))
        self.root.configure(background=BACKGROUND)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        default_font = tkfont.nametofont("TkDefaultFont")
        text_font = tkfont.nametofont("TkTextFont")
        default_font.configure(size=13)
        text_font.configure(size=13)
        font_family = str(default_font.actual("family"))
        self.painad_button_font = tkfont.Font(
            root=self.root,
            family=font_family,
            size=10,
        )
        self.root.option_add("*TCombobox*Listbox.font", default_font)

        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("App.TFrame", background=BACKGROUND)
        style.configure("App.TLabel", background=BACKGROUND, foreground=TEXT)
        style.configure("Card.TFrame", background=CARD)
        style.configure(
            "Title.TLabel",
            background=BACKGROUND,
            foreground=TEXT,
            font=(font_family, 24, "bold"),
        )
        style.configure(
            "Card.TLabelframe",
            background=CARD,
            bordercolor=BORDER,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Card.TLabelframe.Label",
            background=CARD,
            foreground=TEXT,
            font=(font_family, 13, "bold"),
        )
        style.configure("Card.TLabel", background=CARD, foreground=TEXT)
        style.configure("Score.TFrame", background=SCORE_BACKGROUND)
        style.configure(
            "ScoreTitle.TLabel",
            background=SCORE_BACKGROUND,
            foreground=TEXT,
            font=(font_family, 14, "bold"),
        )
        style.configure(
            "Score.TLabel",
            background=SCORE_BACKGROUND,
            foreground=PRIMARY,
            font=(font_family, 34, "bold"),
        )
        style.configure(
            "Field.TEntry",
            padding=7,
            fieldbackground=CARD,
            foreground=TEXT,
        )
        style.map(
            "Field.TEntry",
            fieldbackground=[("readonly", "#EDF2F7")],
            foreground=[("readonly", TEXT)],
        )
        style.configure(
            "PainadTotal.TLabel",
            background=CARD,
            foreground=PRIMARY,
            font=(font_family, 12, "bold"),
        )
        style.configure(
            "Painad.TButton",
            background="#F8FAFC",
            foreground=TEXT,
            font=self.painad_button_font,
            padding=(6, 5),
            bordercolor=BORDER,
            borderwidth=1,
            relief="solid",
            anchor="center",
            justify="center",
        )
        style.map(
            "Painad.TButton",
            background=[("pressed", "#DBEAFE"), ("active", "#EFF6FF")],
            foreground=[("!disabled", TEXT)],
        )
        style.configure(
            "PainadSelected.TButton",
            background=PAINAD_SELECTED,
            foreground=PAINAD_SELECTED_TEXT,
            font=self.painad_button_font,
            padding=(6, 5),
            bordercolor="#86EFAC",
            borderwidth=1,
            relief="sunken",
            anchor="center",
            justify="center",
        )
        style.map(
            "PainadSelected.TButton",
            background=[
                ("pressed", PAINAD_SELECTED_ACTIVE),
                ("active", PAINAD_SELECTED_ACTIVE),
                ("!disabled", PAINAD_SELECTED),
            ],
            foreground=[("!disabled", PAINAD_SELECTED_TEXT)],
        )
        style.configure(
            "EstimateValue.TLabel",
            background=SCORE_BACKGROUND,
            foreground=PRIMARY,
            font=(font_family, 48, "bold"),
        )
        style.configure(
            "EstimateTitle.TLabel",
            background=SCORE_BACKGROUND,
            foreground=TEXT,
            font=(font_family, 15, "bold"),
        )
        style.configure(
            "EstimateHint.TLabel",
            background=SCORE_BACKGROUND,
            foreground=MUTED,
            font=(font_family, 11),
        )
        style.configure(
            "Mode.TButton",
            background="#E2E8F0",
            foreground=TEXT,
            font=(font_family, 11, "bold"),
            padding=(10, 6),
            borderwidth=1,
        )
        style.map(
            "Mode.TButton",
            background=[("pressed", "#CBD5E1"), ("active", "#CBD5E1")],
        )
        style.configure(
            "ModeSelected.TButton",
            background=PRIMARY,
            foreground="#FFFFFF",
            font=(font_family, 11, "bold"),
            padding=(10, 6),
            borderwidth=1,
        )
        style.map(
            "ModeSelected.TButton",
            background=[("pressed", PRIMARY_ACTIVE), ("active", PRIMARY_ACTIVE)],
            foreground=[("!disabled", "#FFFFFF")],
        )
        style.configure(
            "Estimate.TButton",
            background="#F8FAFC",
            foreground=TEXT,
            font=(font_family, 12, "bold"),
            padding=(4, 8),
            borderwidth=1,
        )
        style.map(
            "Estimate.TButton",
            background=[("pressed", "#DBEAFE"), ("active", "#EFF6FF")],
        )
        style.configure(
            "EstimateSelected.TButton",
            background=PRIMARY,
            foreground="#FFFFFF",
            font=(font_family, 12, "bold"),
            padding=(4, 8),
            borderwidth=1,
        )
        style.map(
            "EstimateSelected.TButton",
            background=[("pressed", PRIMARY_ACTIVE), ("active", PRIMARY_ACTIVE)],
            foreground=[("!disabled", "#FFFFFF")],
        )
        self._configure_button_style(
            style, "Record.TButton", PRIMARY, PRIMARY_ACTIVE, font_family
        )
        self._configure_button_style(
            style,
            "Secondary.TButton",
            SECONDARY,
            SECONDARY_ACTIVE,
            font_family,
        )
        self._configure_button_style(
            style,
            "End.TButton",
            END_SESSION,
            END_SESSION_ACTIVE,
            font_family,
        )
        style.configure("Status.TLabel", background=BACKGROUND, foreground=SUCCESS)
        style.configure("File.TLabel", background=BACKGROUND, foreground=MUTED)

    @staticmethod
    def _configure_button_style(
        style: ttk.Style,
        name: str,
        background: str,
        active_background: str,
        font_family: str,
    ) -> None:
        style.configure(
            name,
            background=background,
            foreground="#FFFFFF",
            font=(font_family, 13, "bold"),
            padding=(14, 10),
            borderwidth=0,
        )
        style.map(
            name,
            background=[
                ("disabled", "#A8B3C2"),
                ("pressed", active_background),
                ("active", active_background),
            ],
            foreground=[("disabled", "#EEF2F6"), ("!disabled", "#FFFFFF")],
        )

    def _build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=16, style="App.TFrame")
        main.grid(sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        header = ttk.Frame(main, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        identity = ttk.LabelFrame(
            main,
            text="Session",
            padding=10,
            style="Card.TLabelframe",
        )
        identity.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        identity.columnconfigure(1, weight=1)
        identity.columnconfigure(3, weight=1)

        ttk.Label(identity, text="Subject ID", style="Card.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.subject_entry = ttk.Entry(identity, style="Field.TEntry")
        self.subject_entry.grid(row=0, column=1, sticky="ew", padx=(10, 24), ipady=3)
        ttk.Label(identity, text="Session ID (optional)", style="Card.TLabel").grid(
            row=0, column=2, sticky="w"
        )
        self.session_entry = ttk.Entry(identity, style="Field.TEntry")
        self.session_entry.grid(row=0, column=3, sticky="ew", padx=(10, 0), ipady=3)
        self.session_entry.insert(0, DEFAULT_SESSION_ID)

        estimate = ttk.LabelFrame(
            main,
            text="Nurse Estimated Pain Score",
            padding=12,
            style="Card.TLabelframe",
        )
        estimate.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        estimate.columnconfigure(0, weight=1)
        estimate.rowconfigure(1, weight=1)

        estimate_summary = ttk.Frame(
            estimate,
            padding=(14, 7),
            style="Score.TFrame",
        )
        estimate_summary.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        estimate_summary.columnconfigure(0, weight=1)
        ttk.Label(
            estimate_summary,
            text="Nurse Estimated Pain (0–10)",
            style="EstimateTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            estimate_summary,
            text="Changing a value does not record it.",
            style="EstimateHint.TLabel",
        ).grid(row=1, column=0, sticky="w")
        ttk.Label(
            estimate_summary,
            textvariable=self.estimated_display_var,
            style="EstimateValue.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(18, 24))

        mode_frame = ttk.Frame(estimate_summary, style="Score.TFrame")
        mode_frame.grid(row=0, column=2, rowspan=2, sticky="e")
        self.mode_buttons = {
            "buttons": ttk.Button(
                mode_frame,
                text="0–10 Buttons",
                command=lambda: self._set_estimated_mode("buttons"),
                style="Mode.TButton",
            ),
            "slider": ttk.Button(
                mode_frame,
                text="Slider",
                command=lambda: self._set_estimated_mode("slider"),
                style="Mode.TButton",
            ),
        }
        self.mode_buttons["buttons"].grid(row=0, column=0, padx=(0, 5))
        self.mode_buttons["slider"].grid(row=0, column=1)

        self.estimate_button_frame = ttk.Frame(estimate, style="Card.TFrame")
        self.estimate_button_frame.grid(row=1, column=0, sticky="ew")
        for score in range(11):
            self.estimate_button_frame.columnconfigure(
                score,
                weight=1,
                uniform="estimate",
            )
            button = ttk.Button(
                self.estimate_button_frame,
                text=str(score),
                width=2,
                command=lambda value=score: self._set_estimated_pain(float(value)),
                style="Estimate.TButton",
            )
            button.grid(
                row=0,
                column=score,
                sticky="ew",
                padx=(0 if score == 0 else 2, 0 if score == 10 else 2),
            )
            self.estimate_buttons[score] = button

        self.estimate_slider_frame = ttk.Frame(estimate, style="Card.TFrame")
        self.estimate_slider_frame.columnconfigure(0, weight=1)
        self.estimated_scale = ttk.Scale(
            self.estimate_slider_frame,
            from_=0.0,
            to=10.0,
            variable=self.estimated_var,
            command=self._on_estimated_slider,
        )
        self.estimated_scale.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8)
        ttk.Label(
            self.estimate_slider_frame,
            text="0",
            style="Card.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=8)
        ttk.Label(
            self.estimate_slider_frame,
            text="5",
            style="Card.TLabel",
        ).grid(row=1, column=1)
        ttk.Label(
            self.estimate_slider_frame,
            text="10",
            style="Card.TLabel",
        ).grid(row=1, column=2, sticky="e", padx=8)

        assessment = ttk.LabelFrame(
            main,
            text="PAINAD Assessment (optional)",
            padding=10,
            style="Card.TLabelframe",
        )
        assessment.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        for column in range(1, 4):
            assessment.columnconfigure(column, weight=1, uniform="painad")

        for row, (item_key, (label, descriptions)) in enumerate(PAINAD_ITEMS.items()):
            ttk.Label(assessment, text=label, style="Card.TLabel").grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 10),
                pady=2,
            )
            variable = tk.IntVar(value=-1)
            self.selection_vars[item_key] = variable
            self.painad_buttons[item_key] = {}
            for score, description in enumerate(descriptions):
                button = ttk.Button(
                    assessment,
                    text=self._painad_button_text(score, description),
                    command=lambda key=item_key, value=score: self._toggle_painad(
                        key,
                        value,
                    ),
                    style="Painad.TButton",
                    takefocus=True,
                )
                button.grid(
                    row=row,
                    column=score + 1,
                    sticky="nsew",
                    padx=(0 if score == 0 else 2, 0 if score == 2 else 2),
                    pady=3,
                )
                self.painad_buttons[item_key][score] = button

        total_row = len(PAINAD_ITEMS)
        ttk.Label(
            assessment,
            text="Current PAINAD Score",
            style="Card.TLabel",
        ).grid(row=total_row, column=0, sticky="w", pady=(5, 0))
        ttk.Label(
            assessment,
            textvariable=self.total_var,
            style="PainadTotal.TLabel",
        ).grid(
            row=total_row,
            column=1,
            columnspan=3,
            sticky="e",
            pady=(5, 0),
        )

        notes = ttk.LabelFrame(
            main,
            text="Notes (optional)",
            padding=8,
            style="Card.TLabelframe",
        )
        notes.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        notes.columnconfigure(0, weight=1)
        self.notes_text = tk.Text(
            notes,
            width=40,
            height=2,
            wrap="word",
            undo=True,
            background="#FBFDFF",
            foreground=TEXT,
            insertbackground=TEXT,
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=PRIMARY,
            padx=9,
            pady=7,
            font="TkTextFont",
        )
        self.notes_text.grid(row=0, column=0, sticky="ew")

        self._set_estimated_mode("buttons")
        self._set_estimated_pain(0.0)

        actions = ttk.Frame(main, style="App.TFrame")
        actions.grid(row=5, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(2, weight=1)

        ttk.Button(
            actions,
            text="Record",
            command=self.record,
            style="Record.TButton",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.undo_button = ttk.Button(
            actions,
            text="Undo Last Record",
            command=self.undo_last,
            style="Secondary.TButton",
        )
        self.undo_button.grid(row=0, column=1, sticky="ew", padx=6)
        self.undo_button.state(["disabled"])
        ttk.Button(
            actions,
            text="End Session",
            command=self.end_session,
            style="End.TButton",
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        ttk.Label(
            actions,
            textvariable=self.status_var,
            style="Status.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(9, 0))
        ttk.Label(
            actions,
            textvariable=self.file_var,
            style="File.TLabel",
        ).grid(
            row=2, column=0, columnspan=3, sticky="e", pady=(3, 0)
        )

        self.subject_entry.focus_set()

    def _bind_shortcuts(self) -> None:
        windowing_system = str(self.root.tk.call("tk", "windowingsystem"))
        if windowing_system == "aqua":
            self.root.bind("<Command-Return>", self._record_shortcut)
            self.root.bind("<Command-KP_Enter>", self._record_shortcut)
            self.root.bind("<Command-Escape>", self._clear_notes_shortcut)
        else:
            self.root.bind("<Alt-Return>", self._record_shortcut)
            self.root.bind("<Alt-KP_Enter>", self._record_shortcut)
            self.root.bind("<Alt-Escape>", self._clear_notes_shortcut)

    def _record_shortcut(self, _event: tk.Event) -> str:
        self.record()
        return "break"

    def _clear_notes_shortcut(self, _event: tk.Event) -> str:
        self.notes_text.delete("1.0", "end")
        return "break"

    def _toggle_painad(self, item_key: str, score: int) -> None:
        """Select one PAINAD option, or deselect it when pressed again."""
        if item_key not in self.selection_vars or score not in (0, 1, 2):
            raise ValueError("Invalid PAINAD selection")
        variable = self.selection_vars[item_key]
        current_score = variable.get()
        next_score = toggled_score(
            current_score if current_score in (0, 1, 2) else None,
            score,
        )
        variable.set(-1 if next_score is None else next_score)
        self._refresh_painad_buttons(item_key)
        self._update_total()

    def _refresh_painad_buttons(self, item_key: str) -> None:
        selected_score = self.selection_vars[item_key].get()
        for score, button in self.painad_buttons[item_key].items():
            button.configure(
                style=(
                    "PainadSelected.TButton"
                    if score == selected_score
                    else "Painad.TButton"
                )
            )

    @staticmethod
    def _painad_button_text(score: int, description: str) -> str:
        wrapped = textwrap.fill(
            description,
            width=36,
            break_long_words=False,
            break_on_hyphens=False,
        )
        return f"{score} — {wrapped}"

    def _update_total(self) -> None:
        scores = [
            variable.get()
            for variable in self.selection_vars.values()
            if variable.get() in (0, 1, 2)
        ]
        if len(scores) == len(self.selection_vars):
            self.total_var.set(str(sum(scores)))
        else:
            self.total_var.set(
                f"— ({len(scores)}/{len(self.selection_vars)} selected)"
            )

    def _set_estimated_mode(self, mode: str) -> None:
        """Switch the nurse-score control without changing its value."""
        if mode not in ("buttons", "slider"):
            raise ValueError(f"Unknown nurse score input mode: {mode}")
        self.estimated_mode_var.set(mode)
        if mode == "buttons":
            self.estimate_slider_frame.grid_remove()
            self.estimate_button_frame.grid(row=1, column=0, sticky="ew")
        else:
            self.estimate_button_frame.grid_remove()
            self.estimate_slider_frame.grid(row=1, column=0, sticky="ew")
        for name, button in self.mode_buttons.items():
            button.configure(
                style="ModeSelected.TButton" if name == mode else "Mode.TButton"
            )

    def _on_estimated_slider(self, value: str) -> None:
        self._set_estimated_pain(float(value))

    def _set_estimated_pain(self, value: float) -> None:
        """Set and display a 0.5-step nurse estimate without recording it."""
        snapped = round(max(0.0, min(10.0, float(value))) * 2) / 2
        self.estimated_var.set(snapped)
        self.estimated_display_var.set(f"{snapped:.1f}")
        for score, button in self.estimate_buttons.items():
            button.configure(
                style=(
                    "EstimateSelected.TButton"
                    if math.isclose(snapped, float(score), abs_tol=1e-9)
                    else "Estimate.TButton"
                )
            )

    def _estimated_pain(self) -> float:
        try:
            value = float(self.estimated_var.get())
        except (ValueError, tk.TclError) as exc:
            raise ValueError("Estimated pain must be a number from 0 to 10.") from exc

        if (
            not math.isfinite(value)
            or not 0 <= value <= 10
            or not math.isclose(value * 2, round(value * 2), abs_tol=1e-9)
        ):
            raise ValueError("Estimated pain must be from 0 to 10 in 0.5 steps.")
        return value

    def record(self) -> None:
        """Validate the form and append one assessment."""
        subject = self.subject_entry.get().strip()
        session = self.session_entry.get().strip() or DEFAULT_SESSION_ID
        if not subject:
            messagebox.showerror(
                APP_TITLE,
                "Subject ID is required before recording.",
                parent=self.root,
            )
            self.subject_entry.focus_set()
            return
        if not self.session_entry.get().strip():
            self.session_entry.delete(0, "end")
            self.session_entry.insert(0, DEFAULT_SESSION_ID)

        try:
            estimated_pain = self._estimated_pain()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self.root)
            (
                self.estimated_scale
                if self.estimated_mode_var.get() == "slider"
                else self.estimate_buttons[0]
            ).focus_set()
            return

        scores = {
            item_key: variable.get() if variable.get() in (0, 1, 2) else None
            for item_key, variable in self.selection_vars.items()
        }
        selected_scores = [score for score in scores.values() if score is not None]
        total = (
            sum(selected_scores)
            if len(selected_scores) == len(self.selection_vars)
            else None
        )
        record = AssessmentRecord(
            subject=subject,
            session=session,
            breathing=scores["breathing"],
            negative_vocalization=scores["negative_vocalization"],
            facial_expression=scores["facial_expression"],
            body_language=scores["body_language"],
            consolability=scores["consolability"],
            painad_total=total,
            estimated_pain=estimated_pain,
            notes=self.notes_text.get("1.0", "end-1c"),
        )

        try:
            path = self.recorder.append(record)
        except (OSError, ValueError, csv.Error) as exc:
            messagebox.showerror(
                APP_TITLE,
                f"Could not save the assessment:\n{exc}",
                parent=self.root,
            )
            return

        self._update_total()
        self.file_var.set(self._display_file(path.name))
        self._set_identity_locked(True)
        self.undo_button.state(["!disabled"])
        self._show_status("Saved.", 1_000)

    def undo_last(self) -> None:
        """Remove the most recent row from the active session CSV."""
        try:
            path = self.recorder.undo_last()
        except (OSError, ValueError, csv.Error) as exc:
            messagebox.showerror(
                APP_TITLE,
                f"Could not undo the last record:\n{exc}",
                parent=self.root,
            )
            return

        if path is None:
            self._show_status("Nothing to undo.", 1_500)
        else:
            self.file_var.set(self._display_file(path.name))
            self._show_status("Last record removed.", 1_500)
        if not self.recorder.can_undo:
            self.undo_button.state(["disabled"])

    def end_session(self) -> None:
        """Confirm the end of a session and reset the full form."""
        path = self.recorder.session_path
        if path is None:
            file_message = "No records have been saved yet."
        else:
            file_message = f"Saved file:\n{path.name}"

        confirmed = messagebox.askyesno(
            "End Session",
            (
                "End the current session?\n\n"
                f"{file_message}\n\n"
                "All input fields will be cleared."
            ),
            parent=self.root,
            icon="question",
        )
        if not confirmed:
            return

        self.recorder.end_session()
        self._reset_form()
        self._show_status("Session ended. Ready for a new session.", 2_000)

    def _set_identity_locked(self, locked: bool) -> None:
        state = ["readonly"] if locked else ["!readonly"]
        self.subject_entry.state(state)
        self.session_entry.state(state)

    def _reset_form(self) -> None:
        self._set_identity_locked(False)
        self.subject_entry.delete(0, "end")
        self.session_entry.delete(0, "end")
        self.session_entry.insert(0, DEFAULT_SESSION_ID)
        for item_key, variable in self.selection_vars.items():
            variable.set(-1)
            self._refresh_painad_buttons(item_key)
        self._update_total()
        self._set_estimated_mode("buttons")
        self._set_estimated_pain(0.0)
        self.notes_text.delete("1.0", "end")
        self.notes_text.edit_reset()
        self.file_var.set("CSV: created with the first record")
        self.undo_button.state(["disabled"])
        self.subject_entry.focus_set()

    @staticmethod
    def _display_file(filename: str) -> str:
        if len(filename) > 84:
            filename = f"{filename[:40]}…{filename[-43:]}"
        return f"CSV: {filename}"

    def _show_status(self, message: str, duration_ms: int) -> None:
        if self._status_timer is not None:
            self.root.after_cancel(self._status_timer)
        self.status_var.set(message)
        self._status_timer = self.root.after(duration_ms, self._clear_status)

    def _clear_status(self) -> None:
        self.status_var.set("")
        self._status_timer = None
