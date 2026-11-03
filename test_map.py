import unittest
from bilingual_map import parse_markdown, compare


class MapTests(unittest.TestCase):
    def test_translated_titles_are_not_differences(self):
        result = compare(parse_markdown("# Methods\nText"), parse_markdown("# 方法\n內容"))
        self.assertEqual(result["pairs"][0]["review_items"], [])

    def test_code_and_math_ignore_fake_headings(self):
        result = parse_markdown("# One\n```python\n# Fake\n```\n$$\n# Not a heading\n$$\n")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["code_languages"], ["python"])
        self.assertEqual(result[0]["math_blocks"], 1)

    def test_missing_section_and_image(self):
        result = compare(parse_markdown("# Methods\n![plot](plot.png)\n# Results"), parse_markdown("# 方法"))
        self.assertEqual(result["source_unpaired"][0]["title"], "Results")
        self.assertEqual(result["pairs"][0]["review_items"][0]["field"], "images")

    def test_explicit_reordered_mapping(self):
        result = compare(parse_markdown("# A\n# B"), parse_markdown("# 乙\n# 甲"), [[1, 2], [2, 1]])
        self.assertEqual(result["pairs"][0]["target"]["title"], "甲")
        self.assertEqual(result["source_unpaired"], [])

    def test_duplicate_and_empty_headings_have_stable_indices(self):
        result = parse_markdown("#\n# Same\n# Same\n")
        self.assertEqual([s["index"] for s in result], [1, 2, 3])
        self.assertEqual(result[0]["title"], "")
        with self.assertRaises(ValueError):
            compare(result, result, [[2, 2], [2, 3]])

    def test_blank_docs_and_leading_blank_lines(self):
        self.assertEqual(parse_markdown("\n\n"), [])
        self.assertEqual([s["index"] for s in parse_markdown("\n\n# Hi")], [1])

    def test_preamble_independent_of_heading_pairing(self):
        result = compare(parse_markdown("Intro\n# A"), parse_markdown("# 甲"))
        self.assertEqual(result["pairs"][0]["source"]["index"], 1)
        self.assertEqual(result["source_unpaired"][0]["index"], 0)

    def test_target_multiplicity_and_inline_code(self):
        left = parse_markdown("# A\n`[not](ignored)` [a](x) [b](x)")
        right = parse_markdown("# A\n[a](x)")
        self.assertEqual(left[0]["links"], ["x", "x"])
        self.assertEqual(compare(left, right)["pairs"][0]["review_items"][0]["field"], "links")


if __name__ == "__main__":
    unittest.main()
