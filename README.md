# StuMin Study

A browsable viewer for the student ministry Scope & Sequence, with Bible study notes for
each session that has a lesson guide.

**Live site:** <https://beaubromley.github.io/stumin-study/>

## What's here

- **`index.html`** — the current year (2026-27), starting Fall 2026. Every session grouped
  by volume and unit, with date, main point, and passage. The 13 with full study notes link
  to their own page.
- **`archive.html`** — the five previous rotations (2021-22 through 2025-26), 267 sessions,
  264 of which still link to their original Google Drive lesson guide. Reference only; no
  study notes are written for these.
- **`lessons/*.html`** — one page per studied session, with five sections:
  1. **Scripture** — the session's focal passages in full (World English Bible, public
     domain), plus one-click links to read the same passage in ESV on BibleGateway.
  2. **Context** — historical and literary background, condensed.
  3. **Commentary** — verse-anchored notes on what's actually happening in the text.
  4. **Questions** — discussion questions with answers, collapsed by default so you can
     think before you peek.
  5. **Deeper study** — a collapsible block with a summary, themes in the wider biblical
     story, hard or debated points, Hebrew/Greek/Aramaic word studies, and cross-references.

  On screens wider than 72rem the scripture sits in its own sticky column so it stays in
  view while the commentary and questions scroll beside it. Below that it collapses to a
  single column in reading order. Prev/next buttons appear above and below each lesson.

Currently 13 sessions have full notes: **Aug 16 – Nov 1, 2026**. Those are the weeks the
spreadsheet has Drive links for. Later sessions are listed on the index with their passage
and main point, ready to fill in when the guides are published.

`CURRENT_YEAR` at the top of `scripts/build.py` decides which worksheet is the index and
which fall through to the archive. Bump it when the rotation rolls over.

## Regenerating the site

```bash
python scripts/build.py
```

Everything the build needs is committed in `data/`, so no network access is required.

`SOURCE_SHEET_URL` in `scripts/build.py` points at the Google Sheets original; it is linked
from the index header and every page footer.

### Data pipeline

| Script | Purpose | When to run |
| --- | --- | --- |
| `scripts/parse_xlsx.py` | Reads the master `.xlsx` and writes `data/curriculum.json` (schedule + Drive links) | When the spreadsheet changes |
| `scripts/fetch_scripture.py` | Fetches WEB text from bible-api.com into `data/scripture.json` | When a lesson's passages change |
| `scripts/build.py` | Renders `index.html`, `archive.html`, and `lessons/*.html` | After any data change |

`scripts/parse_xlsx.py` takes the workbook path as its first argument and defaults to
`~/Downloads/StuMin MASTER Scope and Sequence.xlsx`.

## Adding notes for a new session

1. Re-run `parse_xlsx.py` so the new Drive links land in `data/curriculum.json`.
2. Add the session's focal passages to `PASSAGES` in `scripts/fetch_scripture.py`, keyed by
   a new slug, then run it.
3. Add an entry with the same slug to `data/lessons.json` following the existing shape
   (`context`, `commentary`, `questions`, `deeper`).
4. Run `scripts/build.py`.

The build maps sessions to lesson pages by Google Drive file id and will fail loudly if the
number of linked sessions and the number of lesson entries disagree.

## Deploying to GitHub Pages

The site is plain static files at the repo root, so Pages serves it directly:

1. Push this repo to GitHub.
2. **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch
   `main`, folder `/ (root)`.
3. First build takes a minute or two.

## Sources and attribution

Scripture text is the **World English Bible**, which is public domain.

Session titles, main points, unit structure, and the schedule come from the StuMin Scope &
Sequence workbook (Lifeway curriculum, © Lifeway Christian Resources). The context,
commentary, questions, and deeper-study notes on this site are **original summaries written
for group prep** — informed by the lesson guides, not reproductions of them. The linked PDFs
remain the source of record; this site is a study companion, not a replacement.
