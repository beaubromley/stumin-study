"""Generate the static site from data/*.json into the repo root.

Run: python scripts/build.py
Outputs index.html and lessons/<slug>.html. No network needed — all data is committed.
"""
import html
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
LESSON_DIR = os.path.join(ROOT, "lessons")

CURRENT_YEAR = "2026-2027"


def load(name):
    with open(os.path.join(DATA, name), encoding="utf8") as f:
        return json.load(f)


def esc(s):
    return html.escape(s or "", quote=False)


def slug_for(session, order):
    """Map a curriculum session onto a lesson slug by its Drive id."""
    return order.get(session.get("drive_id"))


def bg_url(ref):
    """BibleGateway link for a reference, ESV by default."""
    q = re.sub(r"\s+", "+", ref.strip())
    return f"https://www.biblegateway.com/passage/?search={q}&version=ESV"


CSS = """
:root{
  --bg:#fbfaf7; --panel:#ffffff; --ink:#1c1b19; --muted:#5d5a54; --faint:#8a857c;
  --line:#e4e0d8; --accent:#b4472f; --accent-soft:#f6e9e4; --accent-2:#3c6e63;
  --shadow:0 1px 2px rgba(28,27,25,.05), 0 8px 24px rgba(28,27,25,.05);
  --radius:12px;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#14140f; --panel:#1c1c18; --ink:#eceae4; --muted:#a8a49b; --faint:#807b72;
    --line:#2e2e28; --accent:#e08e6f; --accent-soft:#2b201c; --accent-2:#7fb5a6;
    --shadow:0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.3);
  }
}
:root[data-theme="dark"]{
  --bg:#14140f; --panel:#1c1c18; --ink:#eceae4; --muted:#a8a49b; --faint:#807b72;
  --line:#2e2e28; --accent:#e08e6f; --accent-soft:#2b201c; --accent-2:#7fb5a6;
  --shadow:0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.3);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:15.5px/1.68 "Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  letter-spacing:-.003em;
}
.wrap{max-width:44rem;margin:0 auto;padding:0 1.25rem}
a{color:var(--accent);text-underline-offset:2px}
h1,h2,h3,.ui{font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
h1{font-size:1.85rem;line-height:1.2;letter-spacing:-.02em;margin:0 0 .4rem}
h2{font-size:1.15rem;letter-spacing:-.01em;margin:0}
h3{font-size:1rem;margin:0 0 .35rem}

header.site{border-bottom:1px solid var(--line);background:var(--panel)}
header.site .wrap{padding-top:1.5rem;padding-bottom:1.5rem}
.kicker{font:600 .7rem/1 "Inter",sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 .6rem}
.sub{color:var(--muted);margin:.35rem 0 0;font-size:.95rem}
.backlink{display:inline-block;font:500 .82rem/1 "Inter",sans-serif;color:var(--muted);text-decoration:none;margin-bottom:1rem}
.backlink:hover{color:var(--accent)}

/* ---- index ---- */
.yearnav{display:flex;flex-wrap:wrap;gap:.4rem;margin:1.25rem 0 0}
.yearnav a{
  font:500 .8rem/1 "Inter",sans-serif;text-decoration:none;color:var(--muted);
  border:1px solid var(--line);border-radius:99px;padding:.42rem .8rem;background:var(--panel);
}
.yearnav a.on{background:var(--accent);border-color:var(--accent);color:#fff}
.volume{margin:2.5rem 0 0}
.volume h2{font-size:1.3rem;letter-spacing:-.015em}
.keyverse{
  border-left:3px solid var(--accent);background:var(--accent-soft);
  padding:.7rem .9rem;margin:.75rem 0 0;border-radius:0 8px 8px 0;
  font-size:.92rem;color:var(--ink);
}
.unit{
  font:600 .72rem/1 "Inter",sans-serif;letter-spacing:.1em;text-transform:uppercase;
  color:var(--faint);margin:1.75rem 0 .6rem;padding-bottom:.4rem;border-bottom:1px solid var(--line);
}
ol.sessions{list-style:none;margin:0;padding:0}
li.session{
  display:grid;grid-template-columns:5.5rem 1fr;gap:.9rem;align-items:start;
  padding:.8rem 0;border-bottom:1px solid var(--line);
}
li.session:last-child{border-bottom:0}
.when{font:500 .78rem/1.4 "Inter",sans-serif;color:var(--faint);padding-top:.15rem}
.when .no{color:var(--accent);font-weight:600}
.stitle{font-family:"Inter",sans-serif;font-weight:600;font-size:1rem;letter-spacing:-.01em}
.stitle a{text-decoration:none}
.stitle a:hover{text-decoration:underline}
.point{color:var(--muted);font-size:.92rem;margin:.15rem 0 0}
.passage{font:500 .78rem/1.4 "Inter",sans-serif;color:var(--accent-2);margin:.3rem 0 0}
.tag{
  display:inline-block;font:600 .62rem/1 "Inter",sans-serif;letter-spacing:.07em;text-transform:uppercase;
  border:1px solid var(--line);border-radius:99px;padding:.28rem .5rem;color:var(--faint);margin-left:.4rem;vertical-align:2px;
}
.tag.study{border-color:var(--accent);color:var(--accent)}
li.brk{padding:.55rem 0;border-bottom:1px solid var(--line);color:var(--faint);font:500 .82rem/1.4 "Inter",sans-serif}
.note{
  background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:.9rem 1rem;margin:1.25rem 0 0;font-size:.9rem;color:var(--muted);box-shadow:var(--shadow);
}

/* ---- lesson ---- */
.lessonhead{background:var(--panel);border-bottom:1px solid var(--line)}
.lessonhead .wrap{padding-top:1.25rem;padding-bottom:1.5rem}
.mainpoint{
  border-left:3px solid var(--accent);background:var(--accent-soft);
  padding:.75rem .95rem;border-radius:0 8px 8px 0;margin:1rem 0 0;
  font-size:1.02rem;
}
.meta{font:500 .8rem/1.5 "Inter",sans-serif;color:var(--faint);margin:.6rem 0 0}
.meta a{color:var(--accent-2)}
nav.sections{
  position:sticky;top:0;z-index:5;background:var(--bg);
  border-bottom:1px solid var(--line);
}
nav.sections .wrap{display:flex;gap:.3rem;overflow-x:auto;padding-top:.55rem;padding-bottom:.55rem}
nav.sections a{
  white-space:nowrap;font:600 .75rem/1 "Inter",sans-serif;text-decoration:none;color:var(--muted);
  padding:.45rem .7rem;border-radius:99px;
}
nav.sections a:hover{background:var(--accent-soft);color:var(--accent)}
section{padding:2.25rem 0 0}
.shead{
  font:700 .72rem/1 "Inter",sans-serif;letter-spacing:.13em;text-transform:uppercase;
  color:var(--accent);margin:0 0 1rem;
}
.block{margin:0 0 1.75rem}
.blocktitle{
  font:600 .95rem/1.3 "Inter",sans-serif;letter-spacing:-.01em;margin:0 0 .5rem;
}
.ref{
  font:600 .78rem/1 "Inter",sans-serif;letter-spacing:.04em;color:var(--faint);
  margin:0 0 .5rem;display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;
}
.ref a{font-weight:500;text-decoration:none;border-bottom:1px solid var(--line)}
.scripture{
  background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:1rem 1.15rem;box-shadow:var(--shadow);
  font:1.02rem/1.8 "Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  letter-spacing:-.003em;
}
.scripture p{margin:0}
.scripture .v{
  font:600 .62rem/1 "Inter",sans-serif;color:var(--accent);
  vertical-align:.35em;margin-right:.15rem;
}
.attrib{font:400 .74rem/1.5 "Inter",sans-serif;color:var(--faint);margin:.6rem 0 0}
.cmt{margin:0 0 1.15rem}
.cmt .ref{margin-bottom:.2rem}
.cmt p{margin:0;color:var(--ink)}
details.q{
  border:1px solid var(--line);border-radius:var(--radius);background:var(--panel);
  margin:0 0 .6rem;box-shadow:var(--shadow);overflow:hidden;
}
details.q>summary{
  cursor:pointer;list-style:none;padding:.85rem 1rem;
  font:600 .95rem/1.45 "Inter",sans-serif;letter-spacing:-.005em;
  display:flex;gap:.6rem;align-items:flex-start;
}
details.q>summary::-webkit-details-marker{display:none}
details.q>summary::before{
  content:"+";color:var(--accent);font-weight:700;line-height:1.45;flex:none;
}
details.q[open]>summary::before{content:"\\2212"}
details.q>summary:hover{background:var(--accent-soft)}
details.q .ans{padding:0 1rem 1rem 2.1rem;color:var(--muted);font-size:.96rem}
details.deep{
  border:1px solid var(--line);border-radius:var(--radius);background:var(--panel);
  box-shadow:var(--shadow);overflow:hidden;
}
details.deep>summary{
  cursor:pointer;list-style:none;padding:1rem 1.15rem;
  font:600 1rem/1.3 "Inter",sans-serif;display:flex;justify-content:space-between;align-items:center;gap:1rem;
}
details.deep>summary::-webkit-details-marker{display:none}
details.deep>summary .hint{font:500 .75rem/1 "Inter",sans-serif;color:var(--faint);flex:none}
details.deep>summary .hint::after{content:"open"}
details.deep[open]>summary .hint::after{content:"close"}
details.deep[open]>summary{border-bottom:1px solid var(--line)}
.deepbody{padding:1.15rem}
.deepbody h3{
  font:700 .7rem/1 "Inter",sans-serif;letter-spacing:.12em;text-transform:uppercase;
  color:var(--faint);margin:1.6rem 0 .6rem;
}
.deepbody h3:first-child{margin-top:0}
.deepbody ul{margin:0;padding-left:1.1rem}
.deepbody li{margin:0 0 .45rem;font-size:.96rem}
.word{border-left:2px solid var(--line);padding-left:.85rem;margin:0 0 .8rem}
.word .term{font-size:1.1rem;font-weight:600}
.word .translit{font:600 .8rem/1 "Inter",sans-serif;color:var(--accent);margin-left:.4rem}
.word .lang{font:500 .68rem/1 "Inter",sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);margin-left:.4rem}
.word p{margin:.3rem 0 0;font-size:.94rem;color:var(--muted)}
.hardq{margin:0 0 .9rem}
.hardq .t{font:600 .93rem/1.4 "Inter",sans-serif;margin:0 0 .2rem}
.hardq p{margin:0;font-size:.94rem;color:var(--muted)}
.xref{display:grid;grid-template-columns:minmax(8rem,auto) 1fr;gap:.3rem .9rem;font-size:.93rem}
.xref .r{font:600 .82rem/1.6 "Inter",sans-serif}
.xref .n{color:var(--muted)}
.pager{
  display:flex;justify-content:space-between;gap:1rem;margin:3rem 0 0;
  padding-top:1.25rem;border-top:1px solid var(--line);
  font:500 .85rem/1.4 "Inter",sans-serif;
}
.pager a{text-decoration:none;max-width:45%}
.pager .dir{display:block;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.pager .nx{text-align:right}
footer.site{
  margin-top:3.5rem;border-top:1px solid var(--line);background:var(--panel);
}
footer.site .wrap{padding:1.5rem 1.25rem;font:400 .8rem/1.6 "Inter",sans-serif;color:var(--faint)}
@media (max-width:34rem){
  li.session{grid-template-columns:1fr;gap:.15rem}
  .when{padding-top:0}
  .xref{grid-template-columns:1fr;gap:.1rem}
  .xref .n{margin-bottom:.5rem}
}
@media print{
  nav.sections,.pager,.backlink{display:none}
  details.q,details.deep{border:0;box-shadow:none}
  details.q .ans{display:block}
}
"""

PAGE = """<!doctype html>
<html lang="en"{theme}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='13' font-size='13'>📖</text></svg>">
<style>{css}</style>
</head>
<body>
{body}
<footer class="site"><div class="wrap">
Scripture quotations are from the <strong>World English Bible</strong> (public domain).
Session titles, main points, and the schedule come from the StuMin Scope &amp; Sequence
(Lifeway curriculum); the context, commentary, questions, and deeper-study notes on this
site are original summaries written for group prep, not reproductions of the lesson guides.
</div></footer>
</body>
</html>
"""


def render_scripture(sections):
    out = []
    for sec in sections:
        out.append('<div class="block">')
        out.append(f'<div class="blocktitle">{esc(sec["title"])}</div>')
        for p in sec["passages"]:
            ref = p["reference"]
            out.append(
                f'<div class="ref">{esc(ref)}'
                f'<a href="{bg_url(ref)}" target="_blank" rel="noopener">read in ESV &rarr;</a></div>'
            )
            verses = "".join(
                f'<span class="v">{v["verse"]}</span>{esc(v["text"])} ' for v in p["verses"]
            )
            out.append(f'<div class="scripture"><p>{verses}</p></div>')
        out.append("</div>")
    out.append('<p class="attrib">World English Bible &mdash; public domain.</p>')
    return "\n".join(out)


def render_lesson(slug, lesson, scripture, session, prev_link, next_link):
    title = session["title"]
    passage = session.get("passage") or ""
    date = session.get("date") or ""

    body = [
        '<header class="lessonhead"><div class="wrap">',
        '<a class="backlink" href="../index.html">&larr; All sessions</a>',
        f'<p class="kicker">Unit {esc(session.get("unit") or "")} &middot; Session {esc(session.get("session") or "")}</p>',
        f"<h1>{esc(title)}</h1>",
        f'<div class="mainpoint">{esc(session.get("main_point") or "")}</div>',
        f'<p class="meta">{esc(date)} &middot; {esc(passage)}'
        + (
            f' &middot; <a href="{session["pdf_url"]}" target="_blank" rel="noopener">Lesson PDF</a>'
            if session.get("pdf_url")
            else ""
        )
        + "</p>",
        "</div></header>",
        '<nav class="sections"><div class="wrap">',
        '<a href="#scripture">Scripture</a><a href="#context">Context</a>',
        '<a href="#commentary">Commentary</a><a href="#questions">Questions</a>',
        '<a href="#deeper">Deeper study</a>',
        "</div></nav>",
        '<main class="wrap">',
        '<section id="scripture"><p class="shead">Scripture</p>',
        render_scripture(scripture),
        "</section>",
        '<section id="context"><p class="shead">Context</p>',
    ]
    for para in lesson["context"]:
        body.append(f"<p>{esc(para)}</p>")
    body.append("</section>")

    body.append('<section id="commentary"><p class="shead">Commentary</p>')
    for c in lesson["commentary"]:
        body.append(
            f'<div class="cmt"><div class="ref">{esc(c["ref"])}</div><p>{esc(c["body"])}</p></div>'
        )
    body.append("</section>")

    body.append('<section id="questions"><p class="shead">Questions</p>')
    for q in lesson["questions"]:
        body.append(
            f'<details class="q"><summary>{esc(q["q"])}</summary>'
            f'<div class="ans">{esc(q["a"])}</div></details>'
        )
    body.append("</section>")

    d = lesson["deeper"]
    body.append('<section id="deeper"><p class="shead">Deeper study</p>')
    body.append(
        '<details class="deep"><summary>Themes, hard questions, word studies, cross-references'
        '<span class="hint"></span></summary><div class="deepbody">'
    )
    body.append(f"<h3>Summary</h3><p>{esc(d['summary'])}</p>")
    body.append("<h3>Themes in the bigger story</h3><ul>")
    for t in d["themes"]:
        body.append(f"<li>{esc(t)}</li>")
    body.append("</ul>")
    body.append("<h3>Hard or debated</h3>")
    for h in d["hard"]:
        body.append(
            f'<div class="hardq"><p class="t">{esc(h["topic"])}</p><p>{esc(h["body"])}</p></div>'
        )
    body.append("<h3>Key words</h3>")
    for w in d["words"]:
        body.append(
            f'<div class="word"><span class="term">{esc(w["term"])}</span>'
            f'<span class="translit">{esc(w["translit"])}</span>'
            f'<span class="lang">{esc(w["lang"])}</span>'
            f'<p>{esc(w["body"])}</p></div>'
        )
    body.append("<h3>Elsewhere in Scripture</h3><div class=\"xref\">")
    for x in d["crossrefs"]:
        body.append(
            f'<div class="r"><a href="{bg_url(x["ref"].split(";")[0])}" target="_blank" rel="noopener">{esc(x["ref"])}</a></div>'
            f'<div class="n">{esc(x["note"])}</div>'
        )
    body.append("</div></div></details></section>")

    body.append('<div class="pager">')
    if prev_link:
        body.append(
            f'<a href="{prev_link[0]}"><span class="dir">Previous</span>{esc(prev_link[1])}</a>'
        )
    else:
        body.append("<span></span>")
    if next_link:
        body.append(
            f'<a class="nx" href="{next_link[0]}"><span class="dir">Next</span>{esc(next_link[1])}</a>'
        )
    else:
        body.append("<span></span>")
    body.append("</div></main>")

    return PAGE.format(
        theme="",
        title=f"{title} &middot; StuMin Study",
        desc=esc(session.get("main_point") or title),
        css=CSS,
        body="\n".join(body),
    )


def render_year_blocks(year, studied):
    """Render one worksheet's volumes, units, and sessions as list markup."""
    body = []
    open_list = False
    for b in year["blocks"]:
        if b["kind"] == "volume":
            if open_list:
                body.append("</ol>")
                open_list = False
            body.append(f'<div class="volume"><h2>{esc(b["title"])}</h2></div>')
        elif b["kind"] == "key_passage":
            body.append(f'<div class="keyverse">{esc(b["text"])}</div>')
        elif b["kind"] == "unit":
            if open_list:
                body.append("</ol>")
            body.append(
                f'<p class="unit">Unit {esc(b.get("number") or "")} &mdash; {esc(b.get("title") or "")}</p>'
            )
            body.append('<ol class="sessions">')
            open_list = True
        elif b["kind"] == "break":
            if not open_list:
                body.append('<ol class="sessions">')
                open_list = True
            body.append(
                f'<li class="brk">{esc(b.get("date") or "")} &mdash; {esc(b.get("label") or "")}</li>'
            )
        elif b["kind"] == "session":
            if not open_list:
                body.append('<ol class="sessions">')
                open_list = True
            slug = studied.get(b.get("drive_id"))
            when = b.get("date") or ""
            when_html = (
                f'<span class="no">{esc(when)}</span>'
                if when and not re.match(r"^\d{4}-", when)
                else esc(when) or "&mdash;"
            )
            if slug:
                t = f'<a href="lessons/{slug}.html">{esc(b["title"])}</a><span class="tag study">Study</span>'
            elif b.get("pdf_url"):
                t = f'<a href="{b["pdf_url"]}" target="_blank" rel="noopener">{esc(b["title"])}</a><span class="tag">PDF</span>'
            else:
                t = esc(b["title"])
            body.append(
                f'<li class="session"><div class="when">{when_html}</div><div>'
                f'<div class="stitle">{t}</div>'
                + (f'<p class="point">{esc(b["main_point"])}</p>' if b.get("main_point") else "")
                + (f'<p class="passage">{esc(b["passage"])}</p>' if b.get("passage") else "")
                + "</div></li>"
            )
    if open_list:
        body.append("</ol>")
    return body


def render_index(curriculum, studied):
    """The current year only. Earlier years live on archive.html."""
    year = next(y for y in curriculum["years"] if y["year"] == CURRENT_YEAR)
    older = [y for y in curriculum["years"] if y["year"] != CURRENT_YEAR]

    body = [
        '<header class="site"><div class="wrap">',
        '<p class="kicker">Student Ministry</p>',
        "<h1>Scope &amp; Sequence</h1>",
        f'<p class="sub">{esc(CURRENT_YEAR)} &mdash; every session from Fall 2026 on, with full '
        "study notes for the weeks we have lesson guides for.</p>",
        '<div class="yearnav">',
        f'<a class="on" href="index.html">{esc(CURRENT_YEAR)}</a>',
        '<a href="archive.html">Past years &rarr;</a>',
        "</div></div></header>",
        '<main class="wrap">',
        f'<div class="note"><strong>{len(studied)} sessions</strong> have the full four-section '
        "study (scripture, context, commentary, questions) plus a deeper-study block. Those are "
        "the weeks with linked lesson guides &mdash; Aug 16 through Nov 1, 2026. Everything after "
        "that is listed here with its passage and main point, ready to fill in when the guides "
        f"land. Earlier years ({esc(older[-1]['year'])} through {esc(older[0]['year'])}) are in "
        'the <a href="archive.html">archive</a>.</div>',
    ]
    body += render_year_blocks(year, studied)
    body.append("</main>")
    return PAGE.format(
        theme="",
        title="StuMin Scope &amp; Sequence",
        desc=f"Student ministry scope and sequence for {CURRENT_YEAR}, with Bible study notes for each session.",
        css=CSS,
        body="\n".join(body),
    )


def render_archive(curriculum, studied):
    """Prior years, kept for reference. Most sessions still link to their lesson PDF."""
    older = [y for y in curriculum["years"] if y["year"] != CURRENT_YEAR]
    linked = sum(y["linked_count"] for y in older)

    body = [
        '<header class="site"><div class="wrap">',
        '<a class="backlink" href="index.html">&larr; Current year</a>',
        '<p class="kicker">Student Ministry</p>',
        "<h1>Archive</h1>",
        f'<p class="sub">Previous rotations, {esc(older[-1]["year"])} through '
        f'{esc(older[0]["year"])}. {linked} of these sessions still have their lesson guide '
        "linked.</p>",
        '<div class="yearnav">',
    ]
    for y in older:
        body.append(f'<a href="#y{y["year"]}">{y["year"]}</a>')
    body.append("</div></div></header>")
    body.append('<main class="wrap">')
    body.append(
        '<div class="note">These years are here for reference &mdash; passages, main points, and '
        "the original lesson PDFs. The four-section study notes are only written for the current "
        f'year. <a href="index.html">Back to {esc(CURRENT_YEAR)}</a>.</div>'
    )
    for y in older:
        body.append(
            f'<h2 id="y{y["year"]}" class="unit" style="margin-top:3rem">{y["year"]} '
            f'&middot; {y["session_count"]} sessions</h2>'
        )
        body += render_year_blocks(y, studied)
    body.append("</main>")
    return PAGE.format(
        theme="",
        title="Archive &middot; StuMin Scope &amp; Sequence",
        desc="Previous years of the student ministry scope and sequence, with links to each lesson guide.",
        css=CSS,
        body="\n".join(body),
    )


def main():
    curriculum = load("curriculum.json")
    lessons = load("lessons.json")
    scripture = load("scripture.json")

    # Order lesson slugs by their numeric prefix, and map Drive ids -> slug
    slugs = sorted(lessons)
    current = next(y for y in curriculum["years"] if y["year"] == CURRENT_YEAR)
    linked = [b for b in current["blocks"] if b["kind"] == "session" and b.get("drive_id")]
    if len(linked) != len(slugs):
        raise SystemExit(f"expected {len(slugs)} linked sessions, found {len(linked)}")
    by_drive = {s["drive_id"]: slug for s, slug in zip(linked, slugs)}
    session_by_slug = {slug: s for s, slug in zip(linked, slugs)}

    os.makedirs(LESSON_DIR, exist_ok=True)
    for i, slug in enumerate(slugs):
        prev_link = (
            (f"{slugs[i-1]}.html", session_by_slug[slugs[i - 1]]["title"]) if i else None
        )
        next_link = (
            (f"{slugs[i+1]}.html", session_by_slug[slugs[i + 1]]["title"])
            if i + 1 < len(slugs)
            else None
        )
        page = render_lesson(
            slug, lessons[slug], scripture[slug], session_by_slug[slug], prev_link, next_link
        )
        with open(os.path.join(LESSON_DIR, f"{slug}.html"), "w", encoding="utf8") as f:
            f.write(page)

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf8") as f:
        f.write(render_index(curriculum, by_drive))

    with open(os.path.join(ROOT, "archive.html"), "w", encoding="utf8") as f:
        f.write(render_archive(curriculum, by_drive))

    print(f"built index.html + archive.html + {len(slugs)} lesson pages")


if __name__ == "__main__":
    main()
