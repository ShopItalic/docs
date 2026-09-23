#!/usr/bin/env python3
"""Refresh the public reference only after validating the live API document."""
import json
import os
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen

SOURCE = "https://app.italic.com/api/v1/openapi.json"
ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 2_000_000


def validate(document):
    if document.get("openapi") != "3.1.0":
        raise ValueError("Expected OpenAPI 3.1.0")
    if document.get("info", {}).get("title") != "Italic API":
        raise ValueError("Unexpected API title")
    servers = document.get("servers", [])
    if not any(server.get("url") == "https://app.italic.com/api/v1" for server in servers):
        raise ValueError("Expected the production Italic API server")
    paths = document.get("paths", {})
    if not isinstance(paths, dict) or "/recordings" not in paths:
        raise ValueError("Missing recording operations")
    if "post" not in paths["/recordings"] or "get" not in paths["/recordings"]:
        raise ValueError("Missing recording read/import operations")


def main():
    request = Request(SOURCE, headers={"Accept": "application/json", "User-Agent": "Italic-API-Docs-Sync/1.0"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200 or response.url != SOURCE:
            raise ValueError("Unexpected HTTP response or redirect")
        if "application/json" not in response.headers.get("Content-Type", ""):
            raise ValueError("Expected JSON")
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("OpenAPI document exceeds size limit")
    document = json.loads(payload)
    validate(document)
    destination = ROOT / "openapi.json"
    if json.loads(destination.read_text()) == document:
        print("OpenAPI reference already matches production.")
        return
    content = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(mode="w", dir=ROOT, encoding="utf-8", delete=False) as temporary:
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_name = temporary.name
    os.replace(temporary_name, destination)
    print("Updated OpenAPI reference from production.")


if __name__ == "__main__":
    main()
