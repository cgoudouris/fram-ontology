#!/usr/bin/env python3
"""Apply provenance/authorship metadata from .zenodo.json to a published Zenodo record.

This adds authorship (ORCID + affiliation), supervision (Supervisor contributor
role), keywords, related identifiers and a provenance description to an existing
published deposition, without minting a new version (metadata-only edit).

Single source of truth: the repository-root .zenodo.json. Edit that file, then
run this script so the live Zenodo record matches it.

By default the target record's own version and publication_date are PRESERVED:
editing an older version's record (e.g. v1.8.0) must not re-stamp it with the
version stored in .zenodo.json. Pass --take-version to override that.

Usage:
    # token in a local file, NOT on the command line:
    echo "<token>" > ~/.config/zenodo-token && chmod 600 ~/.config/zenodo-token
    python3 scripts/update-zenodo-metadata.py --record 19959352            # dry run (prints the diff)
    python3 scripts/update-zenodo-metadata.py --record 19959352 --publish  # apply and re-publish

Token: create at https://zenodo.org/account/settings/applications/tokens/new/
with scopes deposit:write and deposit:actions. The script reads it from
$ZENODO_TOKEN or, if unset, from ~/.config/zenodo-token.

No third-party dependencies (uses the standard library only).
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ZENODO_JSON = REPO_ROOT / ".zenodo.json"


def ssl_context() -> ssl.SSLContext:
    """Return an SSL context, falling back to a system CA bundle when the
    interpreter ships without one (common on macOS python.org builds)."""
    try:
        ctx = ssl.create_default_context()
        if ctx.get_ca_certs():
            return ctx
    except Exception:
        pass
    for cafile in ("/etc/ssl/cert.pem", "/opt/homebrew/etc/ca-certificates/cert.pem"):
        if os.path.exists(cafile):
            return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()


CTX = ssl_context()


def read_token() -> str:
    tok = os.environ.get("ZENODO_TOKEN")
    if tok:
        return tok.strip()
    path = Path(os.path.expanduser("~/.config/zenodo-token"))
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    sys.exit("No token: set $ZENODO_TOKEN or write it to ~/.config/zenodo-token "
             "(scopes: deposit:write, deposit:actions).")


def api(method: str, url: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            return r.status, (json.load(r) if r.length != 0 else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body


def person(entry: dict) -> dict:
    out = {"name": entry["name"]}
    for k in ("affiliation", "orcid", "type"):
        if entry.get(k):
            out[k] = entry[k]
    return out


def build_metadata(existing: dict, take_version: bool) -> dict:
    src = json.loads(ZENODO_JSON.read_text(encoding="utf-8"))
    m = dict(existing)            # preserve everything on the record...
    m.pop("prereserve_doi", None)  # ...except server-managed fields
    # ...then overlay the provenance-bearing fields from .zenodo.json
    m["title"] = src["title"]
    m["upload_type"] = src.get("upload_type", "software")
    m["description"] = src["description"]
    m["creators"] = [person(c) for c in src.get("creators", [])]
    m["contributors"] = [person(c) for c in src.get("contributors", [])]
    m["keywords"] = src.get("keywords", m.get("keywords", []))
    m["license"] = src.get("license", m.get("license", "cc-by-sa-4.0"))
    m["related_identifiers"] = src.get("related_identifiers", m.get("related_identifiers", []))
    if take_version and src.get("version"):
        m["version"] = src["version"]
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--record", required=True, help="Zenodo deposition/record id to edit")
    ap.add_argument("--publish", action="store_true", help="Apply and re-publish (default: dry run)")
    ap.add_argument("--take-version", action="store_true",
                    help="Overwrite the record's version with .zenodo.json's (default: preserve)")
    ap.add_argument("--sandbox", action="store_true", help="Target sandbox.zenodo.org")
    args = ap.parse_args()

    tok = read_token()
    base = "https://sandbox.zenodo.org" if args.sandbox else "https://zenodo.org"
    dep = f"{base}/api/deposit/depositions/{args.record}"

    st, cur = api("GET", f"{dep}?access_token={tok}")
    if st != 200:
        sys.exit(f"Could not fetch record {args.record}: {st} {cur}")

    metadata = build_metadata(cur["metadata"], args.take_version)
    print(f"Metadata to apply to record {args.record} on {base}"
          f" (version {metadata.get('version')}, date {metadata.get('publication_date')}):\n")
    print(json.dumps({"metadata": metadata}, indent=2, ensure_ascii=False))

    if not args.publish:
        print("\nDry run. Re-run with --publish to apply and re-publish.")
        return 0

    st, res = api("POST", f"{dep}/actions/edit?access_token={tok}")
    if st not in (201, 400, 403):  # 400/403 == already editable
        sys.exit(f"edit failed: {st} {res}")

    st, res = api("PUT", f"{dep}?access_token={tok}", {"metadata": metadata})
    if st != 200:
        sys.exit(f"metadata update failed: {st} {res}")
    print("\nMetadata updated. Re-publishing...")

    st, res = api("POST", f"{dep}/actions/publish?access_token={tok}")
    if st != 202:
        sys.exit(f"publish failed: {st} {res}")
    print(f"Published. DOI: {res.get('doi_url', '(see record)')}  state: {res.get('state')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
