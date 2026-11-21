"""Validate static GitHub profile README and local SVGs without dependencies."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ASSETS = ROOT / "assets"


def html_image_sources(content: str) -> list[tuple[str, str]]:
    found = []
    for tag in re.findall(r"<img\b[^>]*>", content, re.IGNORECASE | re.DOTALL):
        src = re.search(r'\bsrc="([^"]+)"', tag)
        alt = re.search(r'\balt="([^"]*)"', tag)
        found.append((src.group(1) if src else "", alt.group(1) if alt else ""))
    return found


def validate() -> list[str]:
    if not README.exists():
        return ["Missing README.md"]
    content = README.read_text(encoding="utf-8")
    errors: list[str] = []
    if not content.strip():
        errors.append("Empty README.md")
    if re.search(r"<script\b|javascript:", content, re.IGNORECASE):
        errors.append("README must not contain scripting")
    for src, alt in html_image_sources(content):
        if not src:
            errors.append("Image is missing src")
        if not alt.strip():
            errors.append(f"Image is missing alt text: {src}")
        if src and not urlparse(src).scheme and not src.startswith("//"):
            if ".." in Path(src).parts:
                errors.append(f"Path traversal in image source: {src}")
            elif not (ROOT / src).is_file():
                errors.append(f"Missing local image: {src}")
    for svg in ASSETS.glob("*.svg"):
        try:
            root = ET.parse(svg).getroot()
        except ET.ParseError as exc:
            errors.append(f"Malformed SVG: {svg.name}: {exc}")
            continue
        if not root.tag.endswith("svg") or "viewBox" not in root.attrib:
            errors.append(f"SVG must have a viewBox: {svg.name}")
        if svg.stat().st_size > 400_000:
            errors.append(f"SVG too large (>400KB): {svg.name}")
    return errors


if __name__ == "__main__":
    errors = validate()
    if errors:
        raise SystemExit("Validation failed:\n" + "\n".join(f"- {x}" for x in errors))
    print("PASS: README references, alt text, SVG syntax and size")
