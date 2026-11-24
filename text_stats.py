"""Compute simple statistics about a piece of text."""

import argparse
import json
import math
import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")
SENTENCE_END_RE = re.compile(r"[.!?]+(?=\s|$)")
DEFAULT_WPM = 200

STOPWORDS = frozenset("""
a about above after again against all am an and any are as at be because been before
being below between both but by can could did do does doing down during each few for
from further had has have having he her here hers herself him himself his how i if in
into is it its itself just me more most my myself no nor not now of off on once only or
other our ours ourselves out over own same she should so some such than that the their
theirs them themselves then there these they this those through to too under until up
very was we were what when where which while who whom why will with would you your
yours yourself yourselves
""".split())


def words(text):
    return WORD_RE.findall(text)


def count_sentences(text):
    if not text.strip():
        return 0
    found = len(SENTENCE_END_RE.findall(text))
    # Trailing text without final punctuation still counts as a sentence.
    if not re.search(r"[.!?]\s*$", text.strip()):
        found += 1
    return found


def top_words(text, n=10, skip_stopwords=False):
    counts = Counter(word.lower() for word in words(text))
    if skip_stopwords:
        for stopword in STOPWORDS:
            counts.pop(stopword, None)
    return counts.most_common(n)


def analyze(text, top=10, skip_stopwords=False, wpm=DEFAULT_WPM):
    """Return a dict of statistics for `text`."""
    word_list = words(text)
    word_count = len(word_list)
    sentences = count_sentences(text)
    return {
        "words": word_count,
        "lines": len(text.splitlines()),
        "characters": len(text),
        "characters_no_spaces": len(re.sub(r"\s", "", text)),
        "sentences": sentences,
        "avg_word_length": round(sum(map(len, word_list)) / word_count, 2) if word_count else 0,
        "avg_sentence_length": round(word_count / sentences, 2) if sentences else 0,
        "reading_time_minutes": math.ceil(word_count / wpm) if word_count else 0,
        "top_words": top_words(text, top, skip_stopwords),
    }


def format_report(stats):
    lines = [
        f"Words:                {stats['words']}",
        f"Lines:                {stats['lines']}",
        f"Characters:           {stats['characters']}",
        f"Characters (no ws):   {stats['characters_no_spaces']}",
        f"Sentences:            {stats['sentences']}",
        f"Avg word length:      {stats['avg_word_length']}",
        f"Avg sentence length:  {stats['avg_sentence_length']} words",
        f"Reading time:         ~{stats['reading_time_minutes']} min",
    ]
    if stats["top_words"]:
        lines.append("\nTop words:")
        width = max(len(word) for word, _ in stats["top_words"])
        lines += [f"  {word:<{width}}  {count}" for word, count in stats["top_words"]]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Show statistics about a text file.")
    parser.add_argument("file", nargs="?", help="text file to analyze (default: stdin)")
    parser.add_argument("-n", "--top", type=int, default=10, help="number of top words to show")
    parser.add_argument("--no-stopwords", action="store_true",
                        help="ignore common words like 'the' and 'and' in the top list")
    parser.add_argument("--wpm", type=int, default=DEFAULT_WPM, help="reading speed in words/minute")
    parser.add_argument("--json", action="store_true", help="print the results as JSON")
    args = parser.parse_args(argv)

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    stats = analyze(text, args.top, args.no_stopwords, args.wpm)
    print(json.dumps(stats, indent=2) if args.json else format_report(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
