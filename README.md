# Python Text Stats

A command-line tool that analyzes a text file (or piped text) and reports word,
line, character and sentence counts, average word length, estimated reading time
and the most frequent words. Uses only the Python standard library.

## Features

- Counts words, lines, characters (with and without spaces) and sentences
- Average word length and average sentence length
- Estimated reading time (at 200 words per minute, configurable)
- Top-N most frequent words, with optional stopword filtering
- JSON output with `--json`

## Usage

```bash
python3 text_stats.py sample.txt --no-stopwords -n 5
```

```
Words:                54
Lines:                4
Characters:           329
Characters (no ws):   275
Sentences:            5
Avg word length:      4.96
Avg sentence length:  10.8 words
Reading time:         ~1 min

Top words:
  python       3
  many         2
  programming  1
  language     1
  lets         1
```

More examples:

```bash
# Read from stdin
cat essay.txt | python3 text_stats.py

# Machine-readable output
python3 text_stats.py sample.txt --json

# Slower reader (150 words per minute)
python3 text_stats.py sample.txt --wpm 150
```

## Tests

```bash
python3 -m unittest test_text_stats.py
```
