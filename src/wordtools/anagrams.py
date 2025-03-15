import dataclasses
import itertools
import string
from collections import Counter
from typing import Iterable

import unidecode

from wordtools.words import WordGrouper

KeyType = tuple[str, ...]


@dataclasses.dataclass
class AnagramOptions:
    max_words: int = 0
    min_words: int = 0
    min_word_length: int = 0
    max_word_length: int = 0
    include_words: set[str] = dataclasses.field(default_factory=set)
    exclude_words: set[str] = dataclasses.field(default_factory=set)


class Anagrammer(WordGrouper[KeyType]):
    """
    Pre-computes and groups anagrams of single words.
    """

    def group_key(self, word: str) -> KeyType:
        normalised = unidecode.unidecode(word).lower()
        return tuple(sorted(c for c in normalised if c in string.ascii_lowercase))

    def anagram_phrase(self, phrase: str, options: AnagramOptions) -> Iterable[str]:
        # TODO: Support include/exclude words

        phrase_key = self.group_key(phrase)

        for ngram_group in self._get_ngram_groups(
            phrase_key=phrase_key, ancestors=(), options=options
        ):
            for words in itertools.product(*(self._groups[key] for key in ngram_group)):
                yield " ".join(words)

    def _get_ngram_groups(
        self,
        *,
        phrase_key: KeyType,
        ancestors: tuple[KeyType, ...],
        options: AnagramOptions,
    ) -> Iterable[tuple[KeyType, ...]]:
        """
        Yields all unique groups of ngrams that sum to the original phrase_key, and exist as anagram keys.

        This is done by constructing a trie.

        - We only care about one group at a time, so DFS is appropriate here.
        - Order of ngrams within a group is not meaningful, so to remove dupes, enforce ordering:
            - Put longest ngrams first because they're more interesting.
            - Child ngrams must be same length or shorter than their parent
            - If child ngrams are the same length, order them to avoid duplicates
        """

        parent = ancestors[-1] if ancestors else ()

        if phrase_key == ():
            if len(ancestors) >= options.min_words:
                yield ancestors
            return

        if options.max_words and len(ancestors) >= options.max_words:
            return

        for ngram, complement in self._get_ngrams(
            phrase_key=phrase_key,
            min_len=options.min_word_length,
            max_len=options.max_word_length,
        ):
            if (
                parent == ()
                or len(ngram) < len(parent)
                or (len(ngram) == len(parent) and ngram >= parent)
            ):
                yield from self._get_ngram_groups(
                    phrase_key=complement,
                    ancestors=ancestors + (ngram,),
                    options=options,
                )

    def _get_ngrams(
        self, phrase_key: KeyType, min_len: int, max_len: int
    ) -> Iterable[tuple[KeyType, KeyType]]:
        """
        Generator that yields one tuple of (ngram, remainder) for each unique
        ngram in the input phrase_key that is also a known anagram key, in
        descending order of ngram size.
        """
        if max_len == 0:
            max_len = len(phrase_key)
        else:
            max_len = min(max_len, len(phrase_key))

        if min_len == 0:
            min_len = 1

        for i in range(max_len, min_len - 1, -1):
            seen = set()
            for ngram in itertools.combinations(phrase_key, i):
                if ngram in seen or ngram not in self._groups:
                    continue

                seen.add(ngram)

                complement_counter = Counter(phrase_key) - Counter(ngram)
                complement: list[str] = []
                for letter, count in complement_counter.items():
                    complement.extend((letter,) * count)

                yield ngram, tuple(sorted(complement))
