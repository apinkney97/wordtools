# wordtools
A variety of tools for solving word puzzles


## anagram

Generates anagram phrases.

Example:
```
$ uv run wordtools anagram "give me some anagrams please" --dictionary small --min-word-length 5 | head
passenger gamma lease movie
singapore gamma leave seems
responses gamma leave image
managers please image moves
managers please sagem movie
managers please games movie
managers leaves image poems
managers images leave poems
managers impose leave sagem
managers impose leave games
```

See `uv run wordtools anagram --help` for further filtering options, eg max/min word length, max/min word count.

## letter-boxed

Generates solutions for the New York Times [Letter Boxed](https://www.nytimes.com/puzzles/letter-boxed) puzzles.

Example:
```
$ uv run wordtools letter-boxed zls pri cky ate | head
keys spectral liz
yrs skeptical liz
ars skeptical lazy
crs skeptical lazy
ers skeptical lazy
kits spectral lazy
lakes septic crazy
lazy yrs skeptical
likes septic crazy
ras skeptical lazy
```

## wordle

Shows possible words for Wordle based on your guesses.

Guesses are entered as follows:

- Grey letters: lowercase; example: `a`
- Yellow letters: uppercase; example: `A`
- Green letters: preceded by a dot; example: `.a`

Enter multiple guesses as separate arguments.

Example:
```
$ uv run wordtools wordle gUe.ss
blush
brush
crush
crust
flush
plush
trust
```