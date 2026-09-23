#!/usr/bin/env python3
"""Check that the hand-written guides agree with the published API contract."""

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = re.compile(r"`(GET|POST|PUT|PATCH|DELETE) (/[^`\s?]+)(?:\?[^`]*)?`")


def check() -> list[str]:
    errors = []
    config = json.loads((ROOT / "docs.json").read_text())
    contract = json.loads((ROOT / "openapi.json").read_text())
    paths = contract.get("paths", {})

    for tab in config.get("navigation", {}).get("tabs", []):
        for group in tab.get("groups", []):
            for page in group.get("pages", []):
                if not (ROOT / f"{page}.mdx").is_file():
                    errors.append(f"docs.json: missing page {page}.mdx")
        if spec := tab.get("openapi"):
            if not (ROOT / spec).is_file():
                errors.append(f"docs.json: missing OpenAPI file {spec}")

    for asset in (*config.get("logo", {}).values(), config.get("favicon")):
        if asset and not (ROOT / asset.lstrip("/")).is_file():
            errors.append(f"docs.json: missing asset {asset}")

    for guide in [ROOT / "index.mdx", *(ROOT / "guides").glob("*.mdx")]:
        content = guide.read_text()
        if not content.startswith("---\n") or "\ntitle:" not in content or "\ndescription:" not in content:
            errors.append(f"{guide.relative_to(ROOT)}: missing title or description frontmatter")
        for match in ENDPOINT.finditer(content):
            method, path = match.groups()
            if path not in paths or method.lower() not in paths[path]:
                errors.append(f"{guide.relative_to(ROOT)}: {method} {path} is absent from openapi.json")

    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    print("Guide endpoints, navigation, frontmatter, and brand assets match the docs contract.")
