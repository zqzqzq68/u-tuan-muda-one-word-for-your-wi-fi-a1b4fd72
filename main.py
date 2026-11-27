#!/usr/bin/env python3
"""One Word for Your Wi-Fi -- make.fun bounty entry.

The brief: send a single word that describes your Wi-Fi, aiming to be
both the funniest and the most accurate. A judge model compares the words
two at a time, weighing, most important first:

1. the word describes Wi-Fi as the entrant lives it;
2. it is funny at once, a real laugh rather than a pun that needs
   explaining;
3. it feels true to how home Wi-Fi actually behaves;
4. it avoids the words everyone reaches for and finds a surprising angle;
5. it works as a single word with no context needed, spelled so a reader
   gets it instantly.

This program scores a shortlist of candidate words against those five
axes, picks the highest-scoring one, and writes it -- exactly one word,
no trailing newline -- to ``entry.txt`` in the output directory
(``MAKEFUN_OUTPUT_DIR``, default ``/output``), which is the artifact the
gate and the judge read. The gate requires 1 to 20 UTF-8 characters, not
only white space; the writer validates the word against that before it
touches the file, so a bad pick can never produce an invalid entry.

The pick is fully deterministic: fixed candidates, fixed scores, and a
first-in-list tie-break, so two runs write byte-identical output.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

OUTPUT_ENV = "MAKEFUN_OUTPUT_DIR"
DEFAULT_OUTPUT_DIR = "/output"
ENTRY_FILENAME = "entry.txt"

MAX_ENTRY_CHARS = 20

# Weights follow the judge's own order: on-subject first, then funny,
# then true, then fresh, then instantly readable.
WEIGHTS = (5, 4, 3, 2, 1)


@dataclass(frozen=True)
class Candidate:
    """One candidate word with its score on each of the judge's axes."""

    word: str
    on_subject: int  # describes Wi-Fi as lived, 0-5
    funny: int  # funny at once, 0-5
    true: int  # true to how home Wi-Fi behaves, 0-5
    fresh: int  # surprising angle, not the obvious word, 0-5
    readable: int  # single word, got instantly, 0-5
    why: str

    def score(self) -> int:
        axes = (
            self.on_subject,
            self.funny,
            self.true,
            self.fresh,
            self.readable,
        )
        return sum(weight * axis for weight, axis in zip(WEIGHTS, axes))


CANDIDATES = (
    Candidate(
        "Diva", 5, 5, 4, 4, 5,
        "Wi-Fi is a diva: it only performs when the conditions are "
        "perfect -- right room, right distance, freshly rebooted -- and "
        "storms off mid-performance the moment anything displeases it.",
    ),
    Candidate(
        "Goldilocks", 4, 4, 5, 5, 4,
        "Wi-Fi only works when everything is just right: not too far, "
        "not too many walls, not too many devices.",
    ),
    Candidate(
        "Stagefright", 4, 4, 5, 4, 4,
        "Wi-Fi dies the moment you actually need it -- the important "
        "call, the presentation, the show-and-tell.",
    ),
    Candidate(
        "Frenemy", 4, 4, 4, 3, 5,
        "Wi-Fi is your friend right up until it betrays you at the "
        "worst possible moment.",
    ),
    Candidate(
        "CommitmentIssues", 4, 4, 4, 4, 3,
        "Wi-Fi will not stay connected to anything, or anyone, for long.",
    ),
    Candidate(
        "Mirage", 3, 3, 5, 4, 4,
        "Full bars, no internet: the signal was never really there.",
    ),
    Candidate(
        "HideAndSeek", 4, 3, 4, 3, 4,
        "The network appears, disappears, and reappears exactly when "
        "you stop looking for it.",
    ),
    Candidate(
        "Fairweather", 3, 3, 4, 4, 3,
        "A fair-weather friend: fine on a good day, gone at the first "
        "sign of trouble.",
    ),
    Candidate(
        "Tease", 3, 3, 4, 3, 5,
        "Full bars, one bar, full bars -- it teases you with a "
        "connection it never delivers.",
    ),
    Candidate(
        "Moody", 4, 2, 4, 2, 5,
        "Wi-Fi has moods: wonderful in the morning, unbearable by night, "
        "for no reason anyone can name.",
    ),
)


def pick_best(candidates: tuple[Candidate, ...]) -> Candidate:
    """Return the highest-scoring candidate; ties go to the earliest."""
    best: Candidate | None = None
    for candidate in candidates:
        if best is None or candidate.score() > best.score():
            best = candidate
    if best is None:
        raise ValueError("no candidates to pick from")
    return best


def validate_word(word: str) -> str:
    """Check a word against the gate; return it unchanged if it passes."""
    if not word:
        raise ValueError("entry word is empty")
    if len(word) > MAX_ENTRY_CHARS:
        raise ValueError(
            f"entry word {word!r} is {len(word)} characters, "
            f"over the {MAX_ENTRY_CHARS} limit"
        )
    if word.strip() != word or any(ch.isspace() for ch in word):
        raise ValueError(f"entry word {word!r} is not a single word")
    if not word.isalpha() or not word.isascii():
        raise ValueError(f"entry word {word!r} is not plain ASCII letters")
    return word


def output_dir() -> str:
    """The directory the artifact goes in (kit convention, grader default)."""
    return os.environ.get(OUTPUT_ENV, DEFAULT_OUTPUT_DIR)


def verify_written(word: str, path: str) -> None:
    """Read entry.txt back and confirm it holds exactly the chosen word.

    Catches a partial write or an encoding surprise before the program
    exits successfully: the gate reads this file, so what is on disk --
    not what was handed to write() -- is what counts.
    """
    with open(path, "r", encoding="utf-8", newline="") as handle:
        on_disk = handle.read()
    if on_disk != word:
        raise ValueError(
            f"read-back mismatch: {path} holds {on_disk!r}, "
            f"expected {word!r}"
        )
    if not on_disk or len(on_disk) > MAX_ENTRY_CHARS:
        raise ValueError(f"read-back failed the gate: {on_disk!r}")


def write_entry(word: str, directory: str) -> str:
    """Write exactly the word (no trailing newline) to entry.txt."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, ENTRY_FILENAME)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(word)
    verify_written(word, path)
    return path


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"usage: {argv[0]} (takes no arguments)", file=sys.stderr)
        return 2
    word = validate_word(pick_best(CANDIDATES).word)
    path = write_entry(word, output_dir())
    print(f"{word} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
