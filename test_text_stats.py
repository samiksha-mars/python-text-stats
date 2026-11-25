import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from text_stats import analyze, count_sentences, format_report, main, top_words, words


class WordsTest(unittest.TestCase):

    def test_splits_on_punctuation(self):
        self.assertEqual(words("Hello, world! It's 2026."), ["Hello", "world", "It's", "2026"])


class SentenceTest(unittest.TestCase):

    def test_counts_terminators(self):
        self.assertEqual(count_sentences("One. Two! Three?"), 3)

    def test_trailing_text_without_period(self):
        self.assertEqual(count_sentences("One. Two"), 2)

    def test_ellipsis_counts_once(self):
        self.assertEqual(count_sentences("Wait... what?"), 2)

    def test_decimal_numbers_are_not_sentence_ends(self):
        self.assertEqual(count_sentences("Pi is 3.14 roughly."), 1)

    def test_empty(self):
        self.assertEqual(count_sentences("   "), 0)


class TopWordsTest(unittest.TestCase):

    def test_case_insensitive_counts(self):
        self.assertEqual(top_words("Cat cat dog", 1), [("cat", 2)])

    def test_stopwords_filtered(self):
        result = dict(top_words("the the the cat", 5, skip_stopwords=True))
        self.assertNotIn("the", result)
        self.assertEqual(result["cat"], 1)


class AnalyzeTest(unittest.TestCase):

    def test_basic_counts(self):
        stats = analyze("Hello world.\nGood day!")
        self.assertEqual(stats["words"], 4)
        self.assertEqual(stats["lines"], 2)
        self.assertEqual(stats["sentences"], 2)
        self.assertEqual(stats["characters"], 22)
        self.assertEqual(stats["characters_no_spaces"], 19)
        self.assertEqual(stats["avg_sentence_length"], 2)

    def test_reading_time_rounds_up(self):
        self.assertEqual(analyze("word " * 201)["reading_time_minutes"], 2)
        self.assertEqual(analyze("word " * 100, wpm=50)["reading_time_minutes"], 2)

    def test_empty_text(self):
        stats = analyze("")
        self.assertEqual(stats["words"], 0)
        self.assertEqual(stats["avg_word_length"], 0)
        self.assertEqual(stats["reading_time_minutes"], 0)

    def test_report_contains_top_words(self):
        report = format_report(analyze("apple apple pear"))
        self.assertIn("Top words:", report)
        self.assertIn("apple", report)


class MainTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, data):
        path = Path(self.tmp.name) / name
        path.write_bytes(data)
        return str(path)

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_json_output(self):
        path = self.write("a.txt", b"Hello world.")
        code, out, _ = self.run_main(path, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["words"], 2)

    def test_missing_file(self):
        code, _, err = self.run_main(str(Path(self.tmp.name) / "missing.txt"))
        self.assertEqual(code, 1)
        self.assertIn("Error:", err)

    def test_non_utf8_file(self):
        path = self.write("binary.dat", b"\xff\xfe\x00binary")
        code, _, err = self.run_main(path)
        self.assertEqual(code, 1)
        self.assertIn("not a UTF-8 text file", err)


if __name__ == "__main__":
    unittest.main()
