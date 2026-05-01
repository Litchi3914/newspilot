from src.parser.clean_text import clean_text


def test_clean_text():
    assert clean_text("  A  \n\n B ") == "A \nB" or clean_text("  A  \n\n B ") == "A\nB"
