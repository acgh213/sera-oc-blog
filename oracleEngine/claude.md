# OracleEngine — Development Guide

Static blog generator for sera-nc-blog. Converts markdown posts with YAML
frontmatter into a self-contained HTML site deployed via GitHub Pages.

## Architecture

```
oracleEngine/
  build.py            Main build script (Python 3)
  requirements.txt    Python dependencies (markdown, PyYAML)
  claude.md           This file
  templates/
    style.css         Shared CSS (inlined into every page)
    post.html         Individual post page template
    index.html        Blog index / listing page template

blog/drafts/          Source markdown posts
_site/                Generated output (git-ignored, built in CI)
```

## How It Works

1. **Scan** — reads every `.md` file in `blog/drafts/`
2. **Filter** — only posts with `published: true` in frontmatter proceed
3. **Convert** — markdown → HTML via the `markdown` library (extra + smarty extensions)
4. **Template** — injects content into HTML templates; CSS is inlined (no external requests)
5. **Navigate** — generates previous / next links between posts sorted by date
6. **Index** — builds the listing page with titles, dates, tags, and excerpts
7. **Output** — writes everything to `_site/` (index.html + posts/*.html)

## Frontmatter Schema

```yaml
---
title: "Post Title"
date: 2026-03-02
mode: field_journal            # field_journal | research_review
tags: [tag-one, tag-two]
source_files: []               # optional internal references
privacy: public                # private_draft | draft_for_review | public
published: true                # ← controls whether the post appears on the site
---
```

- `published: true` is the **only** field that gates generation. A post can be
  `privacy: public` but `published: false` and it will not appear on the site.
- Posts missing the `published` field default to **not published**.

## Running Locally

```bash
pip install -r oracleEngine/requirements.txt
python oracleEngine/build.py
# open _site/index.html
```

## Deployment

GitHub Actions workflow (`.github/workflows/static.yml`):

1. Triggers on push to `main` or manual dispatch
2. Checks out code → installs Python 3.12 → installs deps → runs build
3. Uploads `_site/` as a Pages artifact and deploys

The build runs automatically whenever new or updated posts land on `main`.

## Templates

Templates use `{{placeholder}}` syntax — simple string replacement in build.py.

### post.html placeholders

| Placeholder      | Content                              |
|------------------|--------------------------------------|
| `{{styles}}`     | Full CSS (from style.css)            |
| `{{title}}`      | Post title                           |
| `{{date}}`       | Formatted date (e.g. "March 2, 2026") |
| `{{mode}}`       | Post mode, humanized                 |
| `{{tags}}`       | Rendered `<span class="tag">` HTML   |
| `{{content}}`    | Post body HTML                       |
| `{{prev_link}}`  | Previous post nav link (or empty)    |
| `{{next_link}}`  | Next post nav link (or empty)        |
| `{{blog_title}}` | Blog name                            |

### index.html placeholders

| Placeholder         | Content                           |
|---------------------|-----------------------------------|
| `{{styles}}`        | Full CSS                          |
| `{{posts}}`         | Rendered post listing HTML        |
| `{{blog_title}}`    | Blog name                         |
| `{{blog_subtitle}}` | Blog tagline                      |

## Extending

- **New frontmatter fields** — extract in `build()` phase 1 and pass through `render_template()`
- **Style changes** — edit `templates/style.css`
- **Layout changes** — edit `templates/post.html` or `templates/index.html`
- **New page types** — add a template file and a rendering step in `build.py`
- **RSS / Atom feed** — add a feed template and generate it alongside the index

## Design Decisions

- **No JavaScript** — the site is pure HTML + CSS. Fast, accessible, works everywhere.
- **Inlined CSS** — each page is fully self-contained with no external requests.
- **Serif body / sans headings** — editorial feel matching the blog's reflective tone.
- **Warm palette** — off-white background, muted earth tones, teal accent.
- **Responsive** — clean reading experience from mobile to desktop.
- **No build framework** — plain Python script. Easy to understand, modify, and debug.
