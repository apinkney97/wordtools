from typing import Annotated, Optional

import typer

from wordtools.anagrams import Anagrammer, AnagramOptions
from wordtools.letter_boxed import letter_boxed
from wordtools.spelling_bee import spelling_bee
from wordtools.wordle import _get_candidates, parse_input, summarise
from wordtools.words import DEFAULT_WORD_LISTS, DefaultWordList, LengthGrouper, WordBag

app = typer.Typer()

# TODO: Add word list management.

max_words_option = Annotated[int, typer.Option("--max-words", "-W", min=0)]
min_words_option = Annotated[int, typer.Option("--min-words", "-w", min=0)]
max_word_length_option = Annotated[int, typer.Option("--max-word-length", "-L", min=0)]
min_word_length_option = Annotated[int, typer.Option("--min-word-length", "-l", min=0)]
include_word_option = Annotated[
    Optional[list[str]], typer.Option("--include-word", "-i", show_default=False)
]
exclude_word_option = Annotated[
    Optional[list[str]], typer.Option("--exclude-word", "-x", show_default=False)
]
word_list_option = Annotated[DefaultWordList, typer.Option("--dictionary", "-d")]


@app.command()
def anagram(
    phrase: Annotated[str, typer.Argument()],
    word_list: word_list_option = DefaultWordList.LARGE,
    max_words: max_words_option = 0,
    min_words: min_words_option = 0,
    max_word_length: max_word_length_option = 0,
    min_word_length: min_word_length_option = 0,
    include_word: include_word_option = None,
    exclude_word: exclude_word_option = None,
) -> None:
    words = WordBag(includes=DEFAULT_WORD_LISTS[word_list])
    anagrammer = Anagrammer(words)

    options = AnagramOptions(
        max_words=max_words,
        min_words=min_words,
        max_word_length=max_word_length,
        min_word_length=min_word_length,
        include_words=set(include_word or []),
        exclude_words=set(exclude_word or []),
    )

    for anag in anagrammer.anagram_phrase(phrase, options=options):
        print(anag)


@app.command("letter-boxed")
def _letter_boxed(
    sides: Annotated[list[str], typer.Argument()],
    word_list: word_list_option = DefaultWordList.LARGE,
    min_word_length: min_word_length_option = 3,
    max_chain: int = 0,
) -> None:
    words = WordBag(includes=DEFAULT_WORD_LISTS[word_list], min_length=min_word_length)

    for solution in sorted(
        (" ".join(sol) for sol in letter_boxed(words, *sides, max_len=max_chain)),
        key=len,
    ):
        print(solution)


@app.command(
    help=(
        "Guesses are entered as follows: "
        "Grey (no match): lower case letters. "
        "Yellow (right letter, wrong place): upper case letters. "
        "Green (correct place): letters prefixed with a dot. "
        "Example: 'gUe.ss' matches 'blush' and 'crust'"
    )
)
def wordle(
    guess: Annotated[
        list[str],
        typer.Argument(),
    ],
    word_list: word_list_option = DefaultWordList.MEDIUM,
) -> None:
    words = WordBag(includes=DEFAULT_WORD_LISTS[word_list])
    by_length = LengthGrouper(words)

    parsed_input = [parse_input(g) for g in guess]
    input_len = len(parsed_input[0])

    candidates = by_length.get_group("a" * input_len)
    for guess_ in parsed_input:
        candidates = _get_candidates(guess_, candidates)
    for candidate in candidates:
        print(candidate)

    print()
    print(summarise(candidates))


@app.command("spelling-bee")
def _spelling_bee(
    letters: Annotated[str, typer.Argument()],
    required_letter: Annotated[str, typer.Argument()],
    word_list: word_list_option = DefaultWordList.LARGE,
) -> None:
    words = WordBag(includes=DEFAULT_WORD_LISTS[word_list])
    solutions = spelling_bee(
        words=words, letters=letters, required_letter=required_letter
    )
    for score in sorted(solutions, reverse=True):
        print(f"===== {score} =====")
        for word in sorted(solutions[score]):
            print(word)
        print()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
