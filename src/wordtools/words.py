import abc
import enum
import json
from collections.abc import Collection, Hashable, Iterator

import platformdirs
import requests

DATA_PATH = platformdirs.user_data_path("wordtools")

WORD_LISTS_PATH = DATA_PATH / "words-lists"
WORD_LISTS_PATH.mkdir(parents=True, exist_ok=True)


class FileFormat(enum.StrEnum):
    PLAIN = enum.auto()
    JSON = enum.auto()


class RawWordList(Collection[str]):
    """
    Corresponds to a physical file on disk (optionally fetched from a remote URL).

    Default format is plain text, with one word per line. A single JSON list is also supported.
    """

    def __init__(
        self, name: str = "", url: str = "", file_format: FileFormat = FileFormat.PLAIN
    ):
        if not name and not url:
            raise ValueError("At least one of name and url must be supplied")

        if not name:
            name = url.rsplit("/", maxsplit=1)[-1]

        self._name = name
        self._url = url
        self._file_format = file_format

        self._path = WORD_LISTS_PATH / self._name

        self._loaded = False
        self._words: list[str] = []

    def _load(self, force: bool = False) -> None:
        if not force and self._loaded:
            return

        if self._url and not self._path.exists():
            with open(self._path, "w") as f:
                response = requests.get(self._url)
                f.write(response.text)

        with open(self._path, "r") as f:
            match self._file_format:
                case FileFormat.PLAIN:
                    self._words = []
                    for line in f:
                        line = line.strip()
                        if line:
                            self._words.append(line)
                case FileFormat.JSON:
                    # Supports a JSON list of strings. Using any other JSON type will have unpredictable effects.
                    self._words = json.load(f)

        self._loaded = True

    def __iter__(self) -> Iterator[str]:
        self._load()
        yield from self._words

    def __len__(self) -> int:
        self._load()
        return len(self._words)

    def __contains__(self, item: object) -> bool:
        self._load()
        return item in self._words


class DefaultWordList(enum.StrEnum):
    SMALL = enum.auto()
    MEDIUM = enum.auto()
    LARGE = enum.auto()


DEFAULT_WORD_LISTS = {
    DefaultWordList.SMALL: RawWordList(
        url="https://raw.githubusercontent.com/first20hours/google-10000-english/refs/heads/master/google-10000-english.txt"
    ),
    DefaultWordList.MEDIUM: RawWordList(
        url="https://raw.githubusercontent.com/first20hours/google-10000-english/refs/heads/master/20k.txt"
    ),
    DefaultWordList.LARGE: RawWordList(
        url="https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words_alpha.txt"
    ),
}


class WordBag(Collection[str]):
    """
    A bag of unique words.

    Words can be added or permanently ignored.
    """

    def __init__(
        self,
        includes: Collection[str] | None = None,
        excludes: Collection[str] | None = None,
        min_length: int = 1,
    ) -> None:
        self._words: set[str] = set()
        self._excluded: set[str] = set()

        self._min_length = min_length

        for word in excludes or []:
            self.exclude_word(word)

        for word in includes or []:
            self.add_word(word)

    def add_word(self, word: str) -> None:
        if word in self._excluded:
            return

        if len(word) < self._min_length:
            return

        self._words.add(word)

    def exclude_word(self, word: str) -> None:
        if word in self._excluded:
            return

        if len(word) < self._min_length:
            return

        self._excluded.add(word)

        if word not in self._words:
            return

        self._words.remove(word)

    def __iter__(self) -> Iterator[str]:
        return iter(self._words)

    def __contains__(self, word: object) -> bool:
        return word in self._words

    def __len__(self) -> int:
        return len(self._words)


class WordGrouper[T: Hashable](abc.ABC):
    """
    Groups words based on some common property.

    Each word is a member of exactly one group.
    """

    def __init__(self, words: Collection[str]) -> None:
        self._groups: dict[T, set[str]] = {}

        for word in words:
            self.add_word(word)

    @abc.abstractmethod
    def group_key(self, word: str) -> T:
        pass

    def get_group_keys(self) -> Iterator[T]:
        yield from self._groups.keys()

    def contains_key(self, key: T) -> bool:
        return key in self._groups

    def get_group(self, word: str) -> list[str]:
        return sorted(self._groups.get(self.group_key(word), []))

    def __getitem__(self, word: str) -> list[str]:
        return self.get_group(word)

    def __contains__(self, word: str) -> bool:
        key = self.group_key(word)
        return word in self._groups.get(key, [])

    def add_word(self, word: str) -> None:
        self._groups.setdefault(self.group_key(word), set()).add(word)

    def remove_word(self, word: str) -> None:
        key = self.group_key(word)
        anagrams = self._groups[key]
        anagrams.remove(word)
        if len(anagrams) == 0:
            self._groups.pop(key)


class LengthGrouper(WordGrouper[int]):
    """
    Groups words by length.
    """

    def group_key(self, word: str) -> int:
        return len(word)
