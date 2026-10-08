#!/usr/bin/env python3
"""Add a rendered brief to the encrypted dashboard archive under site/.

Usage:
    python3 scripts/publish_site.py brief.json PDB_YYYY-MM-DD.pdf \
        --summary "One or two sentences on the day's top-line judgments." \
        [--sample]

What it does (paths relative to the repo root, wherever you run it from):
  * encrypts the PDF to          site/briefs/PDB_<date>.pdf.enc
  * encrypts the brief JSON to   site/briefs/PDB_<date>.json.enc
  * updates and re-encrypts the archive index   site/briefs/index.enc

Everything is encrypted to the site's public key (site/keys/public.spki), so
this script never needs the sign-in credentials. Nothing in plaintext is
written under site/. The index is kept in plaintext only in memory here:
to update it, the script decrypts the current index with the private key
if PDB_ARCHIVE_USER / PDB_ARCHIVE_PASS are set, otherwise it rebuilds the
index from the sidecar manifest site/briefs/manifest.json (dates and file
names only, no content).

The <date> comes from the brief JSON's "date" field. Re-publishing the same
date replaces that day's entry. Entries flagged "sample" are dropped as soon
as a real edition is published.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

import pdb_crypto as pc

SITE = pc.SITE
BRIEFS = SITE / "briefs"
INDEX_ENC = BRIEFS / "index.enc"
MANIFEST = BRIEFS / "manifest.json"

TAG_RE = re.compile(r"<[^>]+>")


def plain(text):
    return TAG_RE.sub("", text or "").replace("&amp;", "&").replace("&lt;", "<").strip()


def load_manifest():
    if MANIFEST.exists():
        with MANIFEST.open() as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("editions"), list):
            return data
    return {"editions": []}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brief_json")
    ap.add_argument("pdf")
    ap.add_argument("--summary", default="")
    ap.add_argument("--sample", action="store_true")
    args = ap.parse_args()

    brief_path = pathlib.Path(args.brief_json)
    pdf_path = pathlib.Path(args.pdf)
    if not brief_path.exists():
        sys.exit(f"brief JSON not found: {brief_path}")
    if not pdf_path.exists():
        sys.exit(f"PDF not found: {pdf_path}")

    brief = json.loads(brief_path.read_text())
    date = brief.get("date")
    try:
        dt.date.fromisoformat(date)
    except (TypeError, ValueError):
        sys.exit(f'brief JSON "date" must be YYYY-MM-DD, got {date!r}')

    public_key = pc.load_public_key()
    BRIEFS.mkdir(parents=True, exist_ok=True)
    pdf_name = f"PDB_{date}.pdf.enc"
    json_name = f"PDB_{date}.json.enc"
    pc.encrypt_file(pdf_path, BRIEFS / pdf_name, public_key)
    (BRIEFS / json_name).write_bytes(pc.encrypt_bytes(
        json.dumps(brief, ensure_ascii=False, indent=1).encode("utf-8"), public_key))

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

    # The manifest carries the full index entries except headlines/summary,
    # which live only inside the encrypted index. Each publish rebuilds the
    # encrypted index from manifest + the entries' stored encrypted details.
    manifest = load_manifest()
    editions = [e for e in manifest["editions"] if e.get("date") != date]
    if not args.sample:
        for e in editions:
            if e.get("sample"):
                for key in ("pdf", "json"):
                    stale = SITE / e.get(key, "")
                    if stale.is_file():
                        stale.unlink()
        editions = [e for e in editions if not e.get("sample")]

    # Headlines and summaries of earlier editions are kept encrypted per
    # edition in briefs/PDB_<date>.meta.enc so the index can be rebuilt
    # without the private key.
    meta_name = f"PDB_{date}.meta.enc"
    (BRIEFS / meta_name).write_bytes(pc.encrypt_bytes(
        json.dumps({"headlines": headlines, "summary": entry["summary"]}, ensure_ascii=False).encode("utf-8"),
        public_key))
    public_entry = {k: v for k, v in entry.items() if k not in ("headlines", "summary")}
    public_entry["meta"] = f"briefs/{meta_name}"
    editions.append(public_entry)
    editions.sort(key=lambda e: e["date"], reverse=True)
    manifest["editions"] = editions
    manifest["updated_at"] = entry["published_at"]
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))

    # Encrypted index = manifest (the browser merges in each meta.enc after sign-in).
    INDEX_ENC.write_bytes(pc.encrypt_bytes(json.dumps(manifest, ensure_ascii=False).encode("utf-8"), public_key))

    print(f"Published {date}: {len(headlines)} articles -> {BRIEFS / pdf_name}")
    print(f"Archive now holds {len(editions)} edition(s); latest is {editions[0]['date']}")


if __name__ == "__main__":
    main()
