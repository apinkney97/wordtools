from wordtools.words import WordBag


def test_contains():
    words = WordBag()
    assert "hello" not in words
    words.add_word("hello")
    assert "hello" in words


def test_ignore_removes_word():
    words = WordBag(includes=["word", "sword"])

    assert sorted(words) == ["sword", "word"]

    words.exclude_word("sword")

    assert list(words) == ["word"]

    words.exclude_word("word")
    assert list(words) == []


def test_duplicates():
    words = WordBag(includes=["words", "sword"], excludes=["words"])
    words.exclude_word("words")
    words.add_word("words")
    words.add_word("sword")

    assert list(words) == ["sword"]


def test_len():
    words = WordBag()
    assert len(words) == 0

    words.add_word("word")
    assert len(words) == 1

    # check re-adding is a noop
    words.add_word("word")
    assert len(words) == 1
