# Bilingual Markdown Map

[繁體中文](README.zh-Hant.md) · [Website](https://markdown.vesperai.space/en/)

Compare two local Markdown documents by chapter order or an explicit one-to-one index map. Inspect structural omissions without translating or scoring meaning.

## Run

Requires Python 3.10+. Clone this repository, then work from its root:

```sh
git clone https://github.com/Vesper2026/bilingual-markdown-map.git
cd bilingual-markdown-map
# No runtime dependencies; Python 3.10+ is sufficient.
python bilingual_map.py examples/source.md examples/zh-Hant.md --output examples/output
```

Optional project installation: create a local venv and install `.` there to expose the console entry point. Direct script execution needs no installation.

## Input and actual example output

```text
source.md: # Methods + image / # Results
zh-Hant.md: # 方法 (image and Results intentionally omitted)
```

The bundled fixture, not just the abbreviated illustration above, produces:

```text
1 section pairs; 1 source / 0 target unpaired. No semantic scoring.
```

Outputs `comparison.json` and `comparison.md`. The example pairs Methods ↔ 方法, flags `images`, and leaves Results unpaired. To choose pairs, add `--map examples/mapping.json`; the file contains `[[1,1]]`. Reordered chapters can use `[[1,2],[2,1]]`. Every recognized ATX heading gets a 1-based encounter-order index, including empty and duplicate headings. Preamble content is index 0; blank documents have no sections. Default mode pairs preambles only with preambles, then heading positions. Explicit mode matches only listed pairs; repeated or unknown indices are errors. Each heading starts a separate section; subheading objects are not counted again in a parent.

## Tests

```sh
python -m unittest discover -p "test_*.py"
```

Eight tests cover translated titles, fences/math, omissions, explicit reordering, empty/duplicate headings, blank files, preambles and target multiplicity.

## Limits and privacy

This is not a full CommonMark parser or a single-document linter. Supports ATX headings (up to 3 leading spaces), backtick/tilde fences, standalone $$ blocks, and simple direct inline link/image destinations. Compares heading level, code-language multiset, equation-block count and link/image-target multisets. Excludes Setext headings, reference links, raw HTML, nested-parenthesis URLs, tables and inline math. Inline-code handling is limited. Unterminated fences are not linted. The fixture's image target is a symbolic reference. Order mode can misalign after missing middle chapters: review titles or supply a mapping. Equal structure does not imply correct translation.

## Build this repository's independent bilingual site

```sh
python site/build.py
python -m http.server 8090 --directory docs
```

Open http://localhost:8090/en/ or /zh-Hant/. The source lives in `site/`, output in `docs/`, and examples are copied to `docs/downloads/`. The site has two original articles per language, its own hostname/canonical/sitemap/robots/CNAME, and no analytics or upload form. Pages publishing uses main:/docs. GitHub hosts static resources; external links still contact their respective services.

## Related product and maintenance

[KolmoPDF](https://www.kolmopdf.com/pdf-to-markdown) is the related product, not a dependency. KolmoPDF's cloud service uploads documents; these open-source local CLIs do not replace its proprietary parser.

Maintained by Vesper2026 as part of the same maintenance team as the related Eqvero, KolmoPDF and KomoPDF ecosystem. This is not an independent third-party endorsement or the private implementation of those products.

## License

MIT for this code, authored fixtures, documentation and static-site sources; see LICENSE. Third-party dependencies keep their own licenses.
