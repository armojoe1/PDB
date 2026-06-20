# Brief JSON schema (input to `scripts/render_pdb.py`)

The renderer takes a single JSON object describing the day's brief and emits the PDF.
Build this object from your researched, verified content, then run:

```bash
python scripts/render_pdb.py brief.json "PDB_YYYY-MM-DD.pdf"
```

## Top-level object

| key | type | required | notes |
|---|---|---|---|
| `date` | string | yes | `YYYY-MM-DD`. Rendered day-first as "19 June 2026" (matching the real format). |
| `classification` | string | no | Banner text, top & bottom of every page. Default `TOP SECRET//NOFORN`. |
| `short_classification` | string | no | Short marking. Default `TOP SECRET`. (Reserved; not heavily used in current layout.) |
| `release_stamp` | string | no | **Omit this.** If present, prints a red stamp at the very top. The real "APPROVED FOR RELEASE BY THE DNI…" line is intentionally left off. |
| `cover` | bool | no | Default `true`. `true` → prepend the bundled cover PDF (`assets/cover.pdf`) verbatim as page 1; content begins page 2. `false` → no cover. |
| `cover_pdf` | string | no | Path to a cover PDF to prepend instead of the bundled one. Used verbatim. |
| `toc` | array | no | Optional one-line contents list (see below). Usually omit for a tight brief; include for a long multi-article book. |
| `articles` | array | yes | One or more article objects, in order. Each starts on its own page. |

## `toc` entry (optional)

```json
{ "tag": "CHINA-TAIWAN", "summary": "Beijing steps up pressure ahead of Taipei's defense review." }
```

`tag` is upper-cased automatically. No page numbers are needed.

## `article` object

| key | type | required | notes |
|---|---|---|---|
| `headline` | string | yes | Bold title-case headline, e.g. "Cyber Threats to US Election Unlikely To Alter Voting Outcomes". |
| `blocks` | array | yes | Ordered content blocks (see below). |
| `prepared_by` | string | no | Italic source line at the article's end, e.g. "Prepared by ODNI with reporting from CIA, DIA, NSA, INR, and open sources." |

## `block` objects (the body, in order)

**Lead / running paragraph:**
```json
{ "type": "para", "text": "We assess that ..." }
```

**Bulleted sub-assessments:**
```json
{ "type": "bullets", "items": [
  "Multiple checks and redundancies make it likely that ...",
  "We assess that Russia has increased the aggressiveness of ..."
] }
```

**Section divider (the ★ ★ ★ with a faint rule):**
```json
{ "type": "stars" }
```
(use `{ "type": "stars", "rule": false }` for stars without the rule above them)

Inline emphasis: `text` and bullet strings accept reportlab mini-HTML — `<b>bold</b>`,
`<i>italic</i>`, `<br/>`. Escape literal `&` as `&amp;`, `<` as `&lt;`.

## Minimal example

```json
{
  "date": "2026-06-19",
  "cover": true,
  "articles": [
    {
      "headline": "China Steps Up Pressure Around Taiwan Ahead of Defense Review",
      "blocks": [
        { "type": "para", "text": "We assess that Beijing's expanded activity ... signals resolve rather than imminent action." },
        { "type": "bullets", "items": [
          "Aircraft and naval vessels operated near the median line, consistent with recent pressure campaigns.",
          "We see no indication of the logistics buildup that would precede a major operation."
        ] },
        { "type": "stars" },
        { "type": "para", "text": "Press reporting and official statements indicate the activity is being amplified through state media." }
      ],
      "prepared_by": "Prepared by ODNI with reporting from CIA, DIA, NSA, INR, and open sources."
    }
  ]
}
```

## Layout behavior you can rely on

- Banners (`classification`) are stamped top **and** bottom of every page automatically.
- The White House emblem is drawn only at the **top of each story (its first page)**, next to the headline — not on continuation pages and not on the cover. The red corner flash and the classification banners appear on every page.
- `Continued . . .` is added automatically (bottom-right) on any page an article spills past — you don't add it yourself. It's computed in a two-pass build.
- Each article begins on a fresh page.
