from collections.abc import Collection


def spelling_bee(
    *, words: Collection[str], letters: str, required_letter: str
) -> dict[int, list[str]]:
    # Must contain required letter, and any number of other letters

    all_letters = set(letters + required_letter)

    by_score: dict[int, list[str]] = {}

    for word in words:
        score = get_score(
            word, all_letters=all_letters, required_letter=required_letter
        )
        if score:
            by_score.setdefault(score, []).append(word)

    return by_score


def get_score(word: str, *, all_letters: set[str], required_letter: str) -> int:
    if len(word) < 4:
        return 0

    word_set = set(word)
    if required_letter not in word_set:
        return 0

    if not word_set.issubset(all_letters):
        return 0

    if len(word) == 4:
        return 1

    if all_letters == word_set:
        return len(word) + 7

    return len(word)
