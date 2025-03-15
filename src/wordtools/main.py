from typing import Annotated, Optional

import typer

from wordtools.anagrams import Anagrammer, AnagramOptions
from wordtools.letter_boxed import letter_boxed
from wordtools.words import DEFAULT_WORD_LISTS, DefaultWordList, WordBag

app = typer.Typer()

# TODO: Add word list management.

max_words_option = Annotated[int, typer.Option("--max-words", "-W", min=0)]
min_words_option = Annotated[int, typer.Option("--min-words", "-w", min=0)]
min_word_length_option = Annotated[int, typer.Option("--max-word-length", "-L", min=0)]
max_word_length_option = Annotated[int, typer.Option("--min-word-length", "-l", min=0)]
include_word_option = Annotated[
    Optional[list[str]], typer.Option("--include-word", "-i", show_default=False)
]
exclude_word_option = Annotated[
    Optional[list[str]], typer.Option("--exclude-word", "-x", show_default=False)
]
word_list_option = Annotated[DefaultWordList, typer.Option("--dictionary", "-d")]


@app.command("letter-boxed")
def _letter_boxed(
    sides: Annotated[list[str], typer.Argument()],
    word_list: word_list_option = DefaultWordList.MEDIUM,
    min_word_length: min_word_length_option = 3,
    max_chain: int = 0,
) -> None:
    words = WordBag(includes=DEFAULT_WORD_LISTS[word_list], min_length=min_word_length)

    for solution in letter_boxed(words, *sides, max_len=max_chain):
        print(" ".join(solution))


@app.command()
def anagram(
    phrase: Annotated[str, typer.Argument()],
    word_list: word_list_option = DefaultWordList.MEDIUM,
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
