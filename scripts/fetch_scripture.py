"""Fetch public-domain World English Bible text for each lesson's focal passages.

The references mirror the two teaching blocks in each Lifeway session guide.
Writes data/scripture.json, which is committed so the site build needs no network.
"""
import json
import os
import time
import urllib.parse
import urllib.request

# slug -> list of (section title, [references]) matching the session's two blocks
PASSAGES = {
    "01-secrets-of-the-kingdom": [
        ("God's Word Is a Seed", ["Luke 8:4-10"]),
        ("God's Word Grows in Good Soil", ["Luke 8:11-15"]),
    ],
    "02-kingdom-of-heaven": [
        ("The Kingdom Is Growing", ["Matthew 13:31-33"]),
        ("The Kingdom Is Priceless", ["Matthew 13:44-46"]),
    ],
    "03-wind-and-sea-obey": [
        ("Storms Are Not God's Absence", ["Mark 4:35-38"]),
        ("Storms Reveal God's Authority", ["Mark 4:39-41"]),
    ],
    "04-your-faith-has-saved-you": [
        ("We Can Take Our Desperation to Jesus", ["Luke 8:40-45"]),
        ("Our Faith Saves Us", ["Luke 8:46-56"]),
    ],
    "05-five-loaves-two-fish": [
        ("Jesus Cares About Our Needs", ["Matthew 14:13-16"]),
        ("Jesus Has the Power to Meet Our Needs", ["Matthew 14:17-21"]),
    ],
    "06-walking-on-the-sea": [
        ("Jesus Moves First", ["Matthew 14:22-26"]),
        ("Jesus Calls Us to Walk Boldly", ["Matthew 14:27-33"]),
    ],
    "07-childrens-crumbs": [
        ("Jesus Brings Us Out of Darkness", ["Mark 7:24-30"]),
        ("Jesus Heals Us", ["Mark 7:31-37"]),
    ],
    "08-resurrection-and-life": [
        ("Death Stings Now", ["John 11:17-37"]),
        ("Death Has Lost", ["John 11:38-44"]),
    ],
    "09-now-i-can-see": [
        ("We Are Spiritually Blind", ["John 9:1-7", "John 9:13-16", "John 9:24-34"]),
        ("Jesus Gives Us Sight", ["John 9:35-41"]),
    ],
    "10-seek-and-save-the-lost": [
        ("Jesus Meets Us Where We Are", ["Luke 19:1-5"]),
        ("Meeting Jesus Transforms Us", ["Luke 19:6-10"]),
    ],
    "11-stones-would-cry-out": [
        ("Jesus Is Worthy of Worship", ["Luke 19:28-40"]),
        ("Jesus Longs for Us to Know Him", ["Luke 19:41-44"]),
    ],
    "12-the-time-is-coming": [
        ("We Can Expect Persecution", ["Mark 13:5-13"]),
        ("We Can Expect Jesus's Return", ["Mark 13:21-27", "Mark 13:32-33"]),
    ],
    "13-surely-not-i": [
        ("Jesus Endured Betrayal", ["Mark 14:17-21"]),
        ("Jesus Knew the Cost", ["Mark 14:22-31"]),
    ],
}

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "scripture.json")


def fetch(ref):
    url = "https://bible-api.com/" + urllib.parse.quote(ref) + "?translation=web"
    with urllib.request.urlopen(url, timeout=120) as r:
        d = json.loads(r.read().decode("utf8"))
    return {
        "reference": d["reference"],
        "verses": [
            {"chapter": v["chapter"], "verse": v["verse"], "text": v["text"].strip()}
            for v in d["verses"]
        ],
    }


def main():
    out = {}
    for slug, sections in PASSAGES.items():
        out[slug] = []
        for title, refs in sections:
            passages = []
            for ref in refs:
                print(slug, ref, flush=True)
                passages.append(fetch(ref))
                time.sleep(2)
            out[slug].append({"title": title, "passages": passages})
    with open(OUT, "w", encoding="utf8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
