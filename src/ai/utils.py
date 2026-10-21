import re


def split_sentences(text: str) -> list[str]:
    """Splits German text on sentence boundaries (. ! ?), ignoring inline ?...? hypothesis markers."""
    masked = re.sub(r"(?<!\S)\?([^.!?\n]+?)\?", lambda m: "_" * len(m.group(0)), text)
    spans = [m.end() for m in re.finditer(r"(?<=[.!?])\s+", masked)]
    bounds = [0, *spans, len(text)]
    return [
        text[bounds[i] : bounds[i + 1]].strip()
        for i in range(len(bounds) - 1)
        if text[bounds[i] : bounds[i + 1]].strip()
    ]


def locate_sentence(text: str, quote: str) -> int:
    """Find the 0 indexed sentences containing the quotes errors."""
    sentences = split_sentences(text=text)
    for idx, sentence in enumerate(sentences):
        if quote in sentence:
            return idx
    return 0
