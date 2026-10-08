# PDB — mock President's Daily Brief

`SKILL.md` is the `daily-pdb` skill: it researches the last ~24 hours, writes the
brief in the house voice, and renders a PDF with `scripts/render_pdb.py`.

## Netlify dashboard

Each day's edition is published to a private Netlify site:

- Dashboard: https://pdb-daily-brief.netlify.app (Netlify team login, then the ODNI sign-in)
- Netlify admin: https://app.netlify.com/projects/pdb-daily-brief
- Site id: `229b8417-cffa-4fe5-96e7-fcc1b665b10c`

The site is static and lives in `site/`:

| path | what |
|---|---|
| `site/index.html` | the viewer: the page *is* the PDF, rendered full-width with PDF.js, plus a slim bar to switch editions |
| `site/vendor/pdfjs/` | PDF.js 4.10.38 (`pdf.min.mjs`, `pdf.worker.min.mjs`) served locally, no CDN |
| `site/keys/public.spki` | RSA public key; the publish step encrypts every file to it |
| `site/keys/private.enc` | RSA private key, encrypted with the sign-in user ID + passphrase (PBKDF2, AES-GCM) |
| `site/briefs/index.enc` | the encrypted archive index |
| `site/briefs/PDB_<date>.pdf.enc` / `.json.enc` / `.meta.enc` | one encrypted PDF, brief JSON and headline/summary blob per edition |
| `site/briefs/manifest.json` | dates and file names only, so publishes can run without the private key |
| `netlify.toml` | publish directory `site`, no build step |

### Encryption

Nothing under `site/` is readable without the sign-in credentials. Each PDF is encrypted with a
fresh AES-256-GCM key, that key is wrapped with the site's RSA-OAEP public key, and the private key
is stored encrypted under a key derived from `user id + passphrase`. The browser derives the key,
opens the private key, and decrypts in memory; nothing decrypted is written anywhere, and a reload
asks for the credentials again.

```bash
pip install cryptography
python3 scripts/init_keys.py --user joearmitage --passphrase 'SECRET'      # first time only
python3 scripts/init_keys.py --rotate --user joearmitage --passphrase 'OLD' --new-passphrase 'NEW'
```

Losing the credentials loses the archive: the private key exists only inside `site/keys/private.enc`.
A short passphrase can be brute-forced offline by anyone holding `private.enc`, so use a long one.

### Daily pipeline (what the scheduled routine does)

```bash
pip install reportlab pypdf cryptography
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

Entries flagged `"sample": true` in the manifest are dropped automatically the first time a
real edition is published.

### Routine requirements

The scheduled routine runs in a fresh cloud session. For it to publish on its own it needs:

- the repository `armojoe1/PDB` attached as a source of the routine with push access (or the
  session must attach it itself via `add_repo` before pushing), otherwise `git push` is refused;
- either the Netlify site linked to this repo (Git continuous deployment on `main`) or the
  Netlify connector attached to the routine.
