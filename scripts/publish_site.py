#!/usr/bin/env python3
"""Add a rendered brief to the Netlify dashboard archive under site/.

Usage:
    python3 scripts/publish_site.py brief.json PDB_YYYY-MM-DD.pdf \
        --summary "One or two sentences on the day's top-line judgments." \
        [--sample]

What it does (all paths relative to the repo root, wherever you run it from):
  * copies the PDF to            site/briefs/PDB_<date>.pdf
  * writes the brief JSON to     site/briefs/PDB_<date>.json
  * updates the archive index    site/briefs/index.json
  * points /latest.pdf and /latest.json (site/_redirects) at the newest edition

The <date> comes from the brief JSON's "date" field. Re-publishing the same
date replaces that day's entry. Entries flagged "sample" are dropped as soon
as a real edition is published.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BRIEFS = SITE / "briefs"
INDEX = BRIEFS / "index.json"
REDIRECTS = SITE / "_redirects"

TAG_RE = re.compile(r"<[^>]+>")


def plain(text):
    """Strip the renderer's mini-HTML so the index carries clean text."""
    return TAG_RE.sub("", text or "").replace("&amp;", "&").replace("&lt;", "<").strip()


def load_index():
    if INDEX.exists():
        with INDEX.open() as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("editions"), list):
            return data
    return {"editions": []}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brief_json", help="the brief JSON that was rendered")
    ap.add_argument("pdf", help="the rendered PDF (PDB_YYYY-MM-DD.pdf)")
    ap.add_argument("--summary", default="", help="one or two sentences on the day's top-line judgments")
    ap.add_argument("--sample", action="store_true", help="flag this edition as a sample (removed on first real publish)")
    args = ap.parse_args()

    brief_path = pathlib.Path(args.brief_json)
    pdf_path = pathlib.Path(args.pdf)
    if not brief_path.exists():
        sys.exit(f"brief JSON not found: {brief_path}")
    if not pdf_path.exists():
        sys.exit(f"PDF not found: {pdf_path}")

    with brief_path.open() as fh:
        brief = json.load(fh)
    date = brief.get("date")
    try:
        dt.date.fromisoformat(date)
    except (TypeError, ValueError):
        sys.exit(f'brief JSON "date" must be YYYY-MM-DD, got {date!r}')

    BRIEFS.mkdir(parents=True, exist_ok=True)
    pdf_name = f"PDB_{date}.pdf"
    json_name = f"PDB_{date}.json"
    shutil.copyfile(pdf_path, BRIEFS / pdf_name)
    with (BRIEFS / json_name).open("w") as fh:
        json.dump(brief, fh, ensure_ascii=False, indent=1)

    headlines = [plain(a.get("headline", "")) for a in brief.get("articles", []) if a.get("headline")]
    entry = {
        "date": date,
        "pdf": f"briefs/{pdf_name}",
        "json": f"briefs/{json_name}",
        "headlines": headlines,
        "articles": len(brief.get("articles", [])),
        "summary": args.summary.strip(),
        "published_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    }
    if args.sample:
        entry["sample"] = True

    index = load_index()
    editions = [e for e in index["editions"] if e.get("date") != date]
    if not args.sample:
        for e in editions:
            if e.get("sample"):
                for key in ("pdf", "json"):
                    stale = SITE / e.get(key, "")
                    if stale.is_file():
                        stale.unlink()
        editions = [e for e in editions if not e.get("sample")]
    editions.append(entry)
    editions.sort(key=lambda e: e["date"], reverse=True)
    index["editions"] = editions
    index["updated_at"] = entry["published_at"]
    with INDEX.open("w") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)

    latest = editions[0]
    REDIRECTS.write_text(
        f"/latest.pdf   /{latest['pdf']}   302\n"
        f"/latest.json  /{latest['json']}  302\n"
    )
    print(f"Published {date}: {len(headlines)} articles -> {BRIEFS / pdf_name}")
    print(f"Archive now holds {len(editions)} edition(s); latest is {latest['date']}")


if __name__ == "__main__":
    main()
