#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jinja2
import markdown
import yaml

# ==============================================================================
# Configuration & Metadata
# ==============================================================================

with open("site-metadata.yml", "r", encoding="utf-8") as f:
    site_data = yaml.safe_load(f)

SITE_CONFIG = {
    "site_title": site_data.get("site_title", ""),
    "site_subtitle": site_data.get("site_subtitle", ""),
    "site_description": site_data.get("site_description", ""),
    "site_author": site_data.get("site_author", ""),
    "site_author_title": site_data.get("site_author_title", ""),
    "ethnic_name": site_data.get("ethnic_name", ""),
    "site_email": site_data.get("site_email", ""),
    "site_affiliation": site_data.get("site_affiliation", ""),
    "github_username": site_data.get("github_username", ""),
    "linkedin_username": site_data.get("linkedin_username", ""),
    "profile_card": site_data.get("profile_card", {}),
}

NAV_ITEMS = [
    {
        **item,
        "slug": item.get("url", "/").strip("/").split("/")[0] or "home",
    }
    for item in site_data.get("nav_items", [])
]
FOOTER = site_data.get("footer", {})

# ==============================================================================
# Markdown Processor Factory
# ==============================================================================

def create_markdown_pipeline() -> markdown.Markdown:
    """Initialize a Python-Markdown parser configured with math and code extensions."""
    extensions = [
        "fenced_code",
        "tables",
        "md_in_html",
        "codehilite",
        "pymdownx.arithmatex",
    ]
    extension_configs = {
        "codehilite": {
            "guess_lang": False,
            "noclasses": False,
            "css_class": "codehilite",
        },
        "pymdownx.arithmatex": {
            "generic": True,
        },
    }
    return markdown.Markdown(extensions=extensions, extension_configs=extension_configs)


def preprocess_mermaid_blocks(text: str) -> str:
    """
    Safely isolate Mermaid code blocks so codehilite does not corrupt diagram source.
    Converts ```mermaid ... ``` into HTML elements that Mermaid.js initializes client-side.
    """
    pattern = re.compile(r"```mermaid[ \t]*\n(.*?)\n```", re.DOTALL)

    def replacer(match: re.Match[str]) -> str:
        diagram_source = match.group(1).strip()
        # Wrap in a dedicated container for client-side rendering
        return f'\n\n<div class="mermaid-container"><pre class="mermaid">\n{diagram_source}\n</pre></div>\n\n'

    return pattern.sub(replacer, text)


# ==============================================================================
# Frontmatter & Content Parsing
# ==============================================================================

def parse_frontmatter(content_str: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter between opening and closing '---' markers.
    Returns a tuple of (metadata_dict, markdown_body).
    """
    if not content_str.startswith("---"):
        return {}, content_str

    # Search for closing delimiter
    parts = content_str.split("---", 2)
    if len(parts) >= 3:
        yaml_content = parts[1]
        body_content = parts[2].lstrip("\n")
        try:
            metadata = yaml.safe_load(yaml_content) or {}
            if not isinstance(metadata, dict):
                metadata = {}
            return metadata, body_content
        except yaml.YAMLError as exc:
            print(f"[Warning] YAML syntax error in frontmatter: {exc}", file=sys.stderr)
            return {}, parts[2]
    return {}, content_str


# ==============================================================================
# Routing & Path Determination
# ==============================================================================

def compute_output_path(source_rel_path: Path, dist_dir: Path) -> Path:
    """
    Map source content file paths to clean nested directory HTML outputs.
    Examples:
        src/content/index.md           -> dist/index.html
        src/content/computer/index.md  -> dist/computer/index.html
        src/content/notes/example.md   -> dist/notes/example/index.html
    """
    parts = list(source_rel_path.parts)

    if parts[-1] in ("index.md", "index.markdown"):
        # Keep directory structure: e.g. computer/index.md -> dist/computer/index.html
        if len(parts) == 1:
            return dist_dir / "index.html"
        return dist_dir / Path(*parts[:-1]) / "index.html"
    else:
        # File without index.md -> nested clean directory with index.html
        stem = source_rel_path.stem
        if len(parts) == 1:
            return dist_dir / stem / "index.html"
        return dist_dir / Path(*parts[:-1]) / stem / "index.html"


def compute_relative_base(target_file: Path, dist_dir: Path) -> str:
    """
    Calculate relative path prefix (e.g. '', '../', '../../') from target file
    back to the dist root for maximum portability across any host/subpath.
    """
    rel_to_dist = target_file.relative_to(dist_dir)
    depth = len(rel_to_dist.parts) - 1
    if depth <= 0:
        return "./"
    return "../" * depth


def determine_current_slug(output_file: Path, dist_dir: Path) -> str:
    """Determine the active navigation section slug based on the output directory."""
    rel = output_file.relative_to(dist_dir)
    parts = rel.parts
    if len(parts) <= 1 or parts[0] == "index.html":
        return "home"
    return parts[0]


def clean_catalog_text(text: str) -> str:
    """Remove HTML elements and their contents from catalog excerpts."""

    class VisibleTextParser(HTMLParser):
        void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.element_depth = 0
            self.visible_text: List[str] = []

        def handle_starttag(self, tag: str, attrs: Any) -> None:
            if tag not in self.void_tags:
                self.element_depth += 1

        def handle_endtag(self, tag: str) -> None:
            if self.element_depth:
                self.element_depth -= 1

        def handle_data(self, data: str) -> None:
            if self.element_depth == 0:
                self.visible_text.append(data)

    parser = VisibleTextParser()
    parser.feed(text)
    visible_text = "".join(parser.visible_text)
    return re.sub(r"\s+", " ", html.unescape(visible_text)).strip().lstrip("# ").strip()


def collect_catalog_items(
    directory: str,
    content_dir: Path,
    dist_dir: Path,
) -> List[Dict[str, Any]]:
    """Collect frontmatter and URLs for markdown files in a content directory."""
    if not directory.strip("/"):
        print("[!] Catalog layout requires a 'directory' value", file=sys.stderr)
        return []

    catalog_dir = content_dir / directory.strip("/")
    if not catalog_dir.is_dir():
        print(f"[!] Catalog directory not found: {directory}", file=sys.stderr)
        return []

    items: List[Dict[str, Any]] = []
    item_paths = list(catalog_dir.rglob("*.md")) + list(catalog_dir.rglob("*.markdown"))
    for item_path in sorted(item_paths):
        rel_content_path = item_path.relative_to(content_dir)
        if rel_content_path.name in ("index.md", "index.markdown"):
            continue

        with open(item_path, "r", encoding="utf-8") as f:
            metadata, body = parse_frontmatter(f.read())

        item = dict(metadata)
        if item.get("draft") is True:
            continue
        if not item.get("summary") and not item.get("description"):
            clean_body = clean_catalog_text(body)
            item["excerpt"] = next(
                (clean_catalog_text(line) for line in clean_body.splitlines() if clean_catalog_text(line)),
                "",
            )
        else:
            item["excerpt"] = clean_catalog_text(item.get("summary") or item.get("description"))
        item["url"] = "/" + compute_output_path(rel_content_path, dist_dir).relative_to(dist_dir).parent.as_posix() + "/"
        items.append(item)

    return sorted(
        items,
        key=lambda item: (item.get("date") is not None, str(item.get("date", ""))),
        reverse=True,
    )


# ==============================================================================
# Main Build Engine
# ==============================================================================

def build_site(
    src_dir: Path = Path("src"),
    dist_dir: Path = Path("dist"),
    clean: bool = True,
) -> None:
    """Execute the full static site generation pipeline."""
    print("=" * 65)
    print("  DIY Static Site Generator - Build Pipeline")
    print("=" * 65)

    layouts_dir = src_dir / "_layouts"
    assets_dir = src_dir / "assets"
    content_dir = src_dir / "content"

    if not layouts_dir.is_dir():
        print(f"Error: Missing layouts directory: {layouts_dir}", file=sys.stderr)
        sys.exit(1)

    if not content_dir.is_dir():
        print(f"Error: Missing content directory: {content_dir}", file=sys.stderr)
        sys.exit(1)

    # 1. Clean and initialize distribution directory
    if clean and dist_dir.exists():
        print(f"[*] Cleaning output directory: {dist_dir}")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copy static assets (CSS, images, icons)
    dist_assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        print(f"[*] Copying static assets from {assets_dir} -> {dist_assets_dir}")
        shutil.copytree(assets_dir, dist_assets_dir, dirs_exist_ok=True)
    else:
        dist_assets_dir.mkdir(parents=True, exist_ok=True)

    # 3. Initialize Jinja2 environment
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(layouts_dir)),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # 4. Discover all markdown content files
    md_files = list(content_dir.rglob("*.md")) + list(content_dir.rglob("*.markdown"))
    md_files.sort()
    print(f"[*] Found {len(md_files)} content document(s) in {content_dir}")

    # 5. Process and compile each markdown file
    generated_count = 0
    for md_path in md_files:
        rel_content_path = md_path.relative_to(content_dir)
        output_path = compute_output_path(rel_content_path, dist_dir)
        base_path = compute_relative_base(output_path, dist_dir)
        current_slug = determine_current_slug(output_path, dist_dir)

        # Read source markdown
        with open(md_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Parse YAML frontmatter and extract body
        metadata, body = parse_frontmatter(raw_text)

        # Pre-process Mermaid diagram syntax
        body_with_mermaid = preprocess_mermaid_blocks(body)

        # Convert Markdown to HTML with extensions
        md_pipeline = create_markdown_pipeline()
        rendered_body_html = md_pipeline.convert(body_with_mermaid)

        # Choose layout template
        layout_name = metadata.get("layout", "page")
        template_filename = f"{layout_name}.html"
        
        # Fallback to default.html if layout template is not found
        if not (layouts_dir / template_filename).exists():
            print(f"[!] Layout '{template_filename}' not found for {rel_content_path}. Falling back to default.html")
            template_filename = "default.html"

        try:
            template = jinja_env.get_template(template_filename)
        except jinja2.TemplateNotFound:
            print(f"[!] Error: Default template 'default.html' not found in {layouts_dir}", file=sys.stderr)
            continue

        # Prepare rendering context combining site configuration, navigation, and page metadata
        context: Dict[str, Any] = {
            **SITE_CONFIG,
            "nav_items": NAV_ITEMS,
            "footer": FOOTER,
            "base_path": base_path,
            "current_slug": current_slug,
            "page_path": str(rel_content_path),
            "content": rendered_body_html,
            **metadata,
            "draft": metadata.get("draft") is True,
        }

        if layout_name in ("catalog", "catelog"):
            context["catalog_items"] = collect_catalog_items(
                str(metadata.get("directory", "")),
                content_dir,
                dist_dir,
            )

        rendered_html = template.render(context)

        # Write output file safely
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        print(f"    -> Compiled: {rel_content_path} => {output_path.relative_to(dist_dir)}")
        generated_count += 1

    print("=" * 65)
    print(f"[✔] Successfully generated {generated_count} page(s) into '{dist_dir}/'.")
    print("=" * 65)


# ==============================================================================
# Development Server
# ==============================================================================

def serve_site(dist_dir: Path = Path("dist"), port: int = 8000) -> None:
    """Launch a local HTTP development server serving the dist directory."""
    import http.server
    import socketserver

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, directory=str(dist_dir), **kwargs)

    print(f"[*] Starting local static development server on http://localhost:{port}")
    print("    Press Ctrl+C to stop.")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Shutting down dev server.")


# ==============================================================================
# Command-Line Entry Point
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="DIY Python Static Site Generator")
    parser.add_argument(
        "--src",
        type=Path,
        default=Path("src"),
        help="Source directory containing _layouts, assets, and content (default: src)",
    )
    parser.add_argument(
        "--dist",
        type=Path,
        default=Path("dist"),
        help="Target distribution output directory (default: dist)",
    )
    parser.add_argument(
        "--serve",
        "-s",
        action="store_true",
        help="Start a local HTTP server to preview the built static site",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port for local HTTP server (default: 8000)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not wipe dist directory before building",
    )

    args = parser.parse_args()

    build_site(src_dir=args.src, dist_dir=args.dist, clean=not args.no_clean)

    if args.serve:
        serve_site(dist_dir=args.dist, port=args.port)


if __name__ == "__main__":
    main()
