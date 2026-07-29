"""PAINAD categories and scoring helpers."""

from collections.abc import Iterable

PAINAD_ITEMS: dict[str, tuple[str, tuple[str, str, str]]] = {
    "breathing": (
        "Breathing",
        (
            "Normal",
            "Occasional labored breathing / short hyperventilation",
            "Noisy labored breathing / long hyperventilation / Cheyne-Stokes",
        ),
    ),
    "negative_vocalization": (
        "Negative Vocalization",
        (
            "None",
            "Occasional moan or groan",
            "Repeated calling out / loud moaning / crying",
        ),
    ),
    "facial_expression": (
        "Facial Expression",
        (
            "Smiling / Inexpressive",
            "Sad / Frightened / Frown",
            "Grimacing",
        ),
    ),
    "body_language": (
        "Body Language",
        (
            "Relaxed",
            "Tense / Fidgeting",
            "Rigid / Pulling away / Striking",
        ),
    ),
    "consolability": (
        "Consolability",
        (
            "No need to console",
            "Distracted or reassured by voice/touch",
            "Unable to console",
        ),
    ),
}


def choices_for(item_key: str) -> tuple[str, str, str]:
    """Return display choices with their numeric scores."""
    descriptions = PAINAD_ITEMS[item_key][1]
    return (
        f"0 — {descriptions[0]}",
        f"1 — {descriptions[1]}",
        f"2 — {descriptions[2]}",
    )


def score_for(choice: str) -> int:
    """Extract and validate the score at the start of a displayed choice."""
    try:
        score = int(choice.split(maxsplit=1)[0])
    except (ValueError, IndexError) as exc:
        raise ValueError(f"Invalid PAINAD choice: {choice!r}") from exc

    if score not in (0, 1, 2):
        raise ValueError(f"PAINAD item score must be 0, 1, or 2: {score}")
    return score


def total_score(choices: Iterable[str]) -> int:
    """Calculate the total PAINAD score for a set of item choices."""
    return sum(score_for(choice) for choice in choices)


def toggled_score(current_score: int | None, pressed_score: int) -> int | None:
    """Toggle one 0/1/2 option while keeping each PAINAD row single-select."""
    if pressed_score not in (0, 1, 2):
        raise ValueError(f"PAINAD item score must be 0, 1, or 2: {pressed_score}")
    return None if current_score == pressed_score else pressed_score
