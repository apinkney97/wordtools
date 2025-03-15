import collections
import itertools
from collections.abc import Collection
from typing import Iterator

from wordtools.anagrams import Anagrammer


def letter_boxed(
    words: Collection[str], *sides: str, max_len: int = 0
) -> Iterator[list[str]]:
    anagrammer = Anagrammer(words)

    letters = set()
    side_letters = []

    for side in sides:
        side_set = set(side)
        side_letters.append(side_set)
        letters.update(side_set)

    # Find candidate words.
    candidates = []
    for anagram_key in anagrammer.get_group_keys():
        anag_letters = set(anagram_key)
        if anag_letters.issubset(letters):
            candidates.extend(anagrammer.get_group("".join(anagram_key)))

    # Filter out words with adjacent letters on the same side.
    # nb. if there are duplicate letters on multiple sides this
    # will filter out too many words.
    filtered_words = []
    for word in candidates:
        for a, b in zip(word, word[1:]):
            if any(a in side and b in side for side in side_letters):
                break
        else:
            filtered_words.append(word)

    filtered_words.sort()

    words_by_start: dict[str, list[str]] = {}
    for word in filtered_words:
        words_by_start.setdefault(word[0], []).append(word)

    # Now find chains of words sharing start/end
    queue = collections.deque([word] for word in filtered_words)

    while queue:
        current = queue.popleft()
        if max_len > 0 and len(current) >= max_len:
            break
        curr_letters = set(itertools.chain(*current))
        for word in words_by_start[current[-1][-1]]:
            chain = current + [word]
            if curr_letters.union(set(word)) == letters:
                if max_len == 0:
                    max_len = len(chain)
                yield chain
            else:
                queue.append(chain)
