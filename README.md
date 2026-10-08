# PDB — mock President's Daily Brief

`SKILL.md` is the `daily-pdb` skill: it researches the last ~24 hours, writes the
brief in the house voice, and renders a PDF with `scripts/render_pdb.py`.

## Netlify dashboard

Each day's edition is published to a private Netlify site:

- Dashboard: https://pdb-daily-brief.netlify.app (Netlify team login required)
- Netlify admin: https://app.netlify.com/projects/pdb-daily-brief
- Site id: `229b8417-cffa-4fe5-96e7-fcc1b665b10c`
- `/latest.pdf` and `/latest.json` always point at the newest edition

The site is static and lives in `site/`:

| path | what |
|---|---|
| `site/index.html` | the viewer: the page *is* the PDF, rendered full-width with PDF.js, plus a slim bar to switch editions |
| `site/vendor/pdfjs/` | PDF.js 4.10.38 (`pdf.min.mjs`, `pdf.worker.min.mjs`) served locally, no CDN |
| `site/briefs/index.json` | the archive index the page reads |
| `site/briefs/PDB_<date>.pdf` / `.json` | one PDF and one brief JSON per edition |
| `site/_redirects` | the `/latest.*` redirects, rewritten on every publish |
| `netlify.toml` | publish directory `site`, no build step |

### Daily pipeline (what the scheduled routine does)

```bash
python3 scripts/render_pdb.py brief.json PDB_YYYY-MM-DD.pdf
python3 scripts/publish_site.py brief.json PDB_YYYY-MM-DD.pdf --summary "Top-line judgments…"
git add site && git commit -m "PDB YYYY-MM-DD" && git push origin main
# deploy: automatic if the Netlify site is linked to this repo (Git CD, publish dir "site");
# otherwise Netlify connector -> deploy-site (siteId above) and run the npx command it returns
```

Committing `site/` to `main` is what keeps the archive: every routine run starts from a
fresh clone, so editions that are not committed would vanish from the next deploy.
Two ways to deploy, either is fine:

1. **Git continuous deployment (preferred, no tokens):** in the Netlify admin, link the
   `pdb-daily-brief` site to `armojoe1/PDB`, production branch `main`. `netlify.toml`
   already sets the publish directory, so every push to `main` publishes the new edition.
2. **Netlify connector:** its `deploy-site` operation returns a one-shot
   `npx -y @netlify/mcp@latest --site-id … --proxy-path …` command; run it from the repo
   root and it uploads the repo and publishes `site/`.

Entries flagged `"sample": true` in the index are dropped automatically the first time a
real edition is published.
