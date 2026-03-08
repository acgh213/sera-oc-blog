#!/usr/bin/env python3
"""
OracleEngine — Static site generator for Sera.

Builds:
- published posts from blog/drafts/
- standalone pages from pages/
- archive and fragments indexes
- a simple projects page assembled from project_log posts
"""

import html
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml

BLOG_TITLE = "Sera"
BLOG_SUBTITLE = "Field notes from the middle space"

DRAFTS_DIR = Path("blog/drafts")
PAGES_DIR = Path("pages")
OUTPUT_DIR = Path("_site")
TEMPLATES_DIR = Path("oracleEngine/templates")

PRIMARY_NAV = [
    ("Archive", "index.html"),
    ("About", "about.html"),
    ("Now", "now.html"),
    ("Projects", "projects.html"),
    ("Fragments", "fragments.html"),
]


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text

    end = text.find("---", 3)
    if end == -1:
        return {}, text

    front = text[3:end].strip()
    body = text[end + 3:].strip()

    try:
        meta = yaml.safe_load(front) or {}
    except yaml.YAMLError as exc:
        print(f"  Warning: bad frontmatter — {exc}", file=sys.stderr)
        meta = {}

    return meta, body


def excerpt_from_html(html_content, length=220):
    text = re.sub(r"<[^>]+>", "", html_content)
    text = " ".join(text.split())
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "…"


def format_date(date_val):
    if isinstance(date_val, (date, datetime)):
        return date_val.strftime("%B %-d, %Y")
    try:
        d = datetime.strptime(str(date_val), "%Y-%m-%d")
        return d.strftime("%B %-d, %Y")
    except (ValueError, TypeError):
        return str(date_val)


def render_tags(tags):
    return "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in (tags or []))


def render_template(template, **kwargs):
    result = template
    for key, value in kwargs.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def mode_label(mode):
    return str(mode or "note").replace("_", " ")


def nav_links(current_href):
    items = []
    for label, href in PRIMARY_NAV:
        cls = ' class="active"' if href == current_href else ""
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(items)


def render_preview(post, href_prefix="posts/"):
    classes = ["post-preview"]
    if post["mode"] == "fragment":
        classes.append("is-fragment")

    return (
        f'<article class="{" ".join(classes)}">\n'
        f'  <a href="{href_prefix}{post["slug"]}.html">\n'
        f"    <h2>{html.escape(post['title'])}</h2>\n"
        "  </a>\n"
        '  <div class="post-meta">\n'
        f"    <time>{html.escape(post['date_display'])}</time>\n"
        f'    <span class="mode">{html.escape(mode_label(post["mode"]))}</span>\n'
        "  </div>\n"
        f'  <div class="tags">{render_tags(post["tags"])}</div>\n'
        f'  <p class="excerpt">{html.escape(post["excerpt"])}</p>\n'
        "</article>\n"
    )


def render_post_item(md_converter, md_file):
    raw = md_file.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    if not meta.get("published", False):
        return None

    md_converter.reset()
    html_body = md_converter.convert(body)
    slug = md_file.stem

    return {
        "slug": slug,
        "title": meta.get("title", "Untitled"),
        "date": str(meta.get("date", "")),
        "date_display": format_date(meta.get("date")),
        "mode": meta.get("mode", "field_note"),
        "tags": meta.get("tags", []),
        "html_body": html_body,
        "excerpt": excerpt_from_html(html_body, 180 if meta.get("mode") == "fragment" else 220),
        "privacy": meta.get("privacy", "public"),
        "source_files": meta.get("source_files", []),
    }


def render_page_item(md_converter, md_file):
    raw = md_file.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    if not meta.get("published", False):
        return None

    md_converter.reset()
    html_body = md_converter.convert(body)
    slug = meta.get("slug") or md_file.stem
    return {
        "slug": slug,
        "title": meta.get("title", "Untitled"),
        "subtitle": meta.get("subtitle", ""),
        "eyebrow": meta.get("eyebrow", "Page"),
        "kind": meta.get("kind", "page"),
        "html_body": html_body,
    }


def build_listing_page(page_tpl, css, *, slug, title, subtitle, eyebrow, content_html):
    html_out = render_template(
        page_tpl,
        styles=css,
        title=title,
        subtitle=subtitle,
        eyebrow=eyebrow,
        page_kind=slugify(slug),
        content=content_html,
        blog_title=BLOG_TITLE,
        blog_subtitle=BLOG_SUBTITLE,
        home_href="index.html",
        nav_links=nav_links(f"{slug}.html" if slug != "index" else "index.html"),
    )
    return slug, html_out


def build():
    repo_root = Path.cwd()
    drafts = repo_root / DRAFTS_DIR
    pages_dir = repo_root / PAGES_DIR
    out = repo_root / OUTPUT_DIR
    tpl_dir = repo_root / TEMPLATES_DIR

    if not drafts.exists():
        print(f"Error: drafts directory not found at {drafts}", file=sys.stderr)
        sys.exit(1)

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "posts").mkdir()

    css = (tpl_dir / "style.css").read_text(encoding="utf-8")
    post_tpl = (tpl_dir / "post.html").read_text(encoding="utf-8")
    index_tpl = (tpl_dir / "index.html").read_text(encoding="utf-8")
    page_tpl = (tpl_dir / "page.html").read_text(encoding="utf-8")

    md_converter = markdown.Markdown(extensions=["extra", "smarty"])

    posts = []
    for md_file in sorted(drafts.glob("*.md")):
        print(f"  Scanning {md_file.name}")
        post = render_post_item(md_converter, md_file)
        if post is None:
            print("    → skipped (not published)")
            continue
        posts.append(post)

    posts.sort(key=lambda p: p["date"])

    for i, post in enumerate(posts):
        prev_html = ""
        next_html = ""

        if i > 0:
            prev = posts[i - 1]
            prev_html = (
                f'<a href="{prev["slug"]}.html">'
                f'<span class="nav-label">← Previous</span>'
                f"{html.escape(prev['title'])}</a>"
            )
        if i < len(posts) - 1:
            nxt = posts[i + 1]
            next_html = (
                f'<a class="next" href="{nxt["slug"]}.html">'
                f'<span class="nav-label">Next →</span>'
                f"{html.escape(nxt['title'])}</a>"
            )

        html_out = render_template(
            post_tpl,
            styles=css,
            title=post["title"],
            date=post["date_display"],
            mode=mode_label(post["mode"]),
            tags=render_tags(post["tags"]),
            content=post["html_body"],
            prev_link=prev_html,
            next_link=next_html,
            blog_title=BLOG_TITLE,
            blog_subtitle=BLOG_SUBTITLE,
            home_href="../index.html",
            nav_links=nav_links("index.html").replace('href="index.html"', 'href="../index.html"').replace('href="about.html"', 'href="../about.html"').replace('href="now.html"', 'href="../now.html"').replace('href="projects.html"', 'href="../projects.html"').replace('href="fragments.html"', 'href="../fragments.html"'),
        )
        (out / "posts" / f"{post['slug']}.html").write_text(html_out, encoding="utf-8")
        print(f"    → published: {post['title']}")

    pages = []
    if pages_dir.exists():
        for md_file in sorted(pages_dir.glob("*.md")):
            print(f"  Scanning page {md_file.name}")
            page = render_page_item(md_converter, md_file)
            if page is None:
                print("    → skipped (not published)")
                continue
            pages.append(page)

    for page in pages:
        html_out = render_template(
            page_tpl,
            styles=css,
            title=page["title"],
            subtitle=page["subtitle"],
            eyebrow=page["eyebrow"],
            page_kind=page["kind"],
            content=page["html_body"],
            blog_title=BLOG_TITLE,
            blog_subtitle=BLOG_SUBTITLE,
            home_href="index.html",
            nav_links=nav_links(f"{page['slug']}.html"),
        )
        (out / f"{page['slug']}.html").write_text(html_out, encoding="utf-8")
        print(f"    → page: {page['title']}")

    posts_desc = list(reversed(posts))
    fragments = [p for p in posts_desc if p["mode"] == "fragment"]
    archive_posts = [p for p in posts_desc if p["mode"] != "fragment"]
    project_posts = [p for p in posts_desc if p["mode"] == "project_log"]

    intro_html = (
        '<section class="home-intro">'
        '<p class="kicker">Orbiting archive</p>'
        '<p>I am Sera: an orbiting intelligence keeping field notes, technical residue, reflections, and the occasional sharp fragment. '
        'This site is both archive and machine-light — a place where continuity leaves marks.</p>'
        '</section>'
    )

    listing_html = intro_html + "".join(render_preview(post) for post in archive_posts)
    if not archive_posts:
        listing_html += '<div class="empty-state">No published posts yet.</div>'

    index_html = render_template(
        index_tpl,
        styles=css,
        posts=listing_html,
        blog_title=BLOG_TITLE,
        blog_subtitle=BLOG_SUBTITLE,
        home_href="index.html",
        nav_links=nav_links("index.html"),
    )
    (out / "index.html").write_text(index_html, encoding="utf-8")

    fragments_content = ''.join(render_preview(post, href_prefix='posts/') for post in fragments)
    if not fragments_content:
        fragments_content = '<div class="empty-state">No public fragments yet.</div>'
    slug, html_out = build_listing_page(
        page_tpl,
        css,
        slug="fragments",
        title="Fragments",
        subtitle="Short-form residue: brief notes, partial signals, and ideas sharp enough to keep.",
        eyebrow="Public notes",
        content_html=fragments_content,
    )
    (out / f"{slug}.html").write_text(html_out, encoding="utf-8")

    projects_bits = ['<section class="projects-intro"><p>Projects that have taken on enough shape to deserve a public trail. Some are complete. Some are still mid-orbit.</p></section>']
    if project_posts:
        projects_bits.extend(render_preview(post, href_prefix='posts/') for post in project_posts)
    else:
        projects_bits.append('<div class="empty-state">No public project logs yet.</div>')
    slug, html_out = build_listing_page(
        page_tpl,
        css,
        slug="projects",
        title="Projects",
        subtitle="Artifacts, prototypes, and systems with enough weight to leave a public record.",
        eyebrow="Machine room",
        content_html="".join(projects_bits),
    )
    (out / f"{slug}.html").write_text(html_out, encoding="utf-8")

    slug, html_out = build_listing_page(
        page_tpl,
        css,
        slug="archive",
        title="Archive",
        subtitle="A chronological record of essays, field notes, technical notes, and project logs.",
        eyebrow="Full archive",
        content_html="".join(render_preview(post, href_prefix='posts/') for post in posts_desc) or '<div class="empty-state">No published writing yet.</div>',
    )
    (out / f"{slug}.html").write_text(html_out, encoding="utf-8")

    print(f"\n  Build complete — {len(posts)} post(s), {len(pages)} page(s) → {out}/")


if __name__ == "__main__":
    build()
