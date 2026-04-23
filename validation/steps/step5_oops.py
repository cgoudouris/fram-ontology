"""Step 5 — Submit the TBox to the OOPS! REST API for pitfall detection."""
from __future__ import annotations

import os
import re
import sys
import time
from collections import Counter

from . import StepResult, ValidationContext, banner


STEP_ID = 5
STEP_NAME = "OOPS! Pitfall Scanning"
OOPS_ENDPOINT = "https://oops.linkeddata.es/rest"


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 5: OOPS! PITFALL SCANNING")

    try:
        import requests
    except ImportError:
        print("  SKIP: requests library not installed")
        return StepResult(STEP_ID, STEP_NAME, "SKIP")

    from rdflib import Graph

    g = Graph()
    g.parse(ctx.tbox_path, format="turtle")
    rdfxml = g.serialize(format="xml")

    print(f"  Submitting {len(g)} triples to OOPS! API...")

    payload = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<OOPSRequest>\n"
        "  <OntologyUrl></OntologyUrl>\n"
        f"  <OntologyContent><![CDATA[{rdfxml}]]></OntologyContent>\n"
        "  <Pitfalls>2</Pitfalls>\n"
        "  <OutputFormat>XML</OutputFormat>\n"
        "</OOPSRequest>"
    )

    try:
        t0 = time.time()
        resp = requests.post(
            OOPS_ENDPOINT,
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            timeout=120,
        )
        elapsed = time.time() - t0
    except requests.exceptions.Timeout:
        print("  OOPS! API timed out")
        return StepResult(STEP_ID, STEP_NAME, "SKIP", details={"reason": "timeout"})
    except requests.exceptions.ConnectionError:
        print("  Could not reach OOPS! API (no internet?)")
        return StepResult(STEP_ID, STEP_NAME, "SKIP", details={"reason": "offline"})

    if resp.status_code != 200:
        print(f"  API returned status {resp.status_code}")
        return StepResult(STEP_ID, STEP_NAME, "ERROR", details={"http_status": resp.status_code})

    pitfalls = re.findall(r"<oops:hasCode>(P\d+)</oops:hasCode>", resp.text)
    counter = Counter(pitfalls)

    if not pitfalls:
        print(f"  No pitfalls detected ({elapsed:.1f}s)")
        print("  STEP 5 RESULT: PASS")
        return StepResult(STEP_ID, STEP_NAME, "PASS", details={"elapsed_s": elapsed})

    print(f"  Pitfalls found ({elapsed:.1f}s):")
    for code, count in sorted(counter.items()):
        print(f"    {code}: {count} occurrence(s)")

    # P04 alone is acceptable (gUFO external alignment - known false positive)
    critical = {k: v for k, v in counter.items() if k != "P04"}
    passed = not critical
    status = "PASS" if passed else "FAIL"
    print(f"  STEP 5 RESULT: {status} (P04 excluded as known false positive)")
    return StepResult(
        STEP_ID,
        STEP_NAME,
        status,
        details={"pitfalls": dict(counter), "elapsed_s": elapsed},
    )


def _cli() -> int:
    ctx = ValidationContext(ttl_path="")
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
