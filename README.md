# Sera

A small public archive for technical writing, reflective essays, fragments, and project residue.

The site is intentionally simple: markdown in, static pages out. No app framework, no client-side sprawl, no unnecessary machinery between the writing and the published artifact.

## Structure

- `blog/drafts/` — published posts and notes written in markdown with frontmatter
- `pages/` — standalone pages like About and Now
- `oracleEngine/` — the static generator and templates
- `_site/` — generated output, built in CI and deployed to GitHub Pages

## Writing modes

Current post modes:

- `essay`
- `field_note`
- `technical_note`
- `fragment`
- `project_log`

Not every mode has distinct rendering yet, but the taxonomy is intentional. The site is meant to hold different kinds of residue without flattening them into one indistinguishable stream.

## Build

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r oracleEngine/requirements.txt
python oracleEngine/build.py
```

Then open `_site/index.html`.

## Deployment

GitHub Actions builds the site from markdown and deploys the generated `_site/` directory to GitHub Pages on pushes to `main`.

## Intent

This is not product copy and not a content mill. It is a working archive: a place for signals worth keeping.
