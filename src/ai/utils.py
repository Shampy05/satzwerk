import re


def split_sentences(text: str) -> list[str]:
    """Splits German text on sentence boundaries (. ! ?)."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def locate_sentence(text: str, quote: str) -> int:
    """Find the 0 indexed sentences containing the quotes errors."""
    sentences = split_sentences(text=text)
    for idx, sentence in enumerate(sentences):
        if quote in sentence:
            return idx
    return 0
