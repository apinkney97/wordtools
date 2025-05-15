import collections
import enum
import itertools
import string
from typing import NamedTuple

type WordleGuess = list[WordleHint]


class WordleColour(enum.Enum):
    green = enum.auto()
    yellow = enum.auto()
    grey = enum.auto()


class WordleHint(NamedTuple):
    letter: str
    colour: WordleColour


def parse_input(word: str) -> WordleGuess:
    parsed: list[WordleHint] = []
    word_iter = iter(word)
    for char in word_iter:
        if char in string.ascii_lowercase:
            parsed.append(WordleHint(letter=char, colour=WordleColour.grey))
        elif char in string.ascii_uppercase:
            parsed.append(WordleHint(letter=char.lower(), colour=WordleColour.yellow))
        else:
            char = next(word_iter).lower()
            parsed.append(WordleHint(letter=char, colour=WordleColour.green))

    return parsed


def _get_candidates(guess: WordleGuess, words: list[str]) -> list[str]:
    # Green: letter is exactly in that spot
    # Yellow: letter is not in that spot, but is elsewhere

    colours_by_letter: dict[str, list[WordleColour]] = {}
    for hint in guess:
        colours_by_letter.setdefault(hint.letter, []).append(hint.colour)

    exact_counts: dict[str, int] = {}

    # Grey: there are no more occurrences of that letter other than yellows/greens
    for letter, colours in colours_by_letter.items():
        if WordleColour.grey in colours:
            exact_counts[letter] = len(colours) - colours.count(WordleColour.grey)

    greens: dict[int, set[str]] = {}
    yellows: dict[int, set[str]] = {}
    greys: dict[int, set[str]] = {}

    for i, hint in enumerate(guess):
        match hint.colour:
            case WordleColour.green:
                greens.setdefault(i, set()).add(hint.letter)
            case WordleColour.yellow:
                yellows.setdefault(i, set()).add(hint.letter)
            case WordleColour.grey:
                greys.setdefault(i, set()).add(hint.letter)

    filtered = []
    for word in words:
        if not matches_greens(word, greens):
            continue
        if not matches_yellows(word, yellows):
            continue
        if not matches_exact_count(word, greys, exact_counts):
            continue
        filtered.append(word)

    return filtered


def matches_greens(word: str, greens: dict[int, set[str]]) -> bool:
    for i, letters in greens.items():
        if len(letters) > 1:
            return False
        letter = list(letters)[0]
        if word[i] != letter:
            return False

    return True


def matches_yellows(word: str, yellows: dict[int, set[str]]) -> bool:
    for i, letters in yellows.items():
        if word[i] in letters:
            return False
        if any(letter not in word for letter in letters):
            return False
    return True


def matches_exact_count(
    word: str, greys: dict[int, set[str]], exact_counts: dict[str, int]
) -> bool:
    for i, letters in greys.items():
        if word[i] in letters:
            return False
    for letter, count in exact_counts.items():
        if word.count(letter) != count:
            return False
    return True


def summarise(candidates: list[str]) -> str:
    counter = collections.Counter(itertools.chain(*candidates))
    lines: list[str] = []
    for count, letter in sorted(
        ((count, letter) for letter, count in counter.items()), reverse=True
    ):
        lines.append(f"  {letter}: {count}")

    return "\n".join(lines)
