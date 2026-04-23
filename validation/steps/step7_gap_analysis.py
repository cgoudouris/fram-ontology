"""Step 7 — Predicate-level gap analysis between TTL and JSON-LD exports.

This is an *informational* step: it reports which predicates appear in
one serialization but not the other (or with different cardinality), to
help diagnose exporter divergences. It does not produce a PASS/FAIL
verdict; the orchestrator records the metric for the validation log.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

from . import StepResult, ValidationContext, banner, shorten


STEP_ID = 7
STEP_NAME = "Gap Analysis"


def _predicate_counts(g) -> Counter:
    counts: Counter = Counter()
    for _, p, _ in g:
        counts[str(p)] += 1
    return counts


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 7: GAP ANALYSIS")

    if not ctx.jsonld_path:
        print("  SKIP: requires both TTL and JSON-LD inputs")
        return StepResult(STEP_ID, STEP_NAME, "SKIP")

    from rdflib import Graph, URIRef
    from pyld import jsonld as jsonld_lib

    g_ttl = Graph()
    g_ttl.parse(ctx.ttl_path, format="turtle")

    with open(ctx.jsonld_path) as f:
        jdata = json.load(f)
    with open(ctx.context_path) as f:
        ctx_data = json.load(f)
    jdata["@context"] = ctx_data["@context"]
    nquads = jsonld_lib.to_rdf(jdata, {"format": "application/n-quads"})
    g_jsonld = Graph()
    g_jsonld.parse(data=nquads, format="nquads")

    print(f"  TTL: {len(g_ttl)} triples  |  JSON-LD: {len(g_jsonld)} triples")
    print(f"  Difference: {len(g_jsonld) - len(g_ttl)} triples")

    ttl_preds = _predicate_counts(g_ttl)
    jsonld_preds = _predicate_counts(g_jsonld)
    all_preds = sorted(set(ttl_preds) | set(jsonld_preds))

    print(f"\n  {'Predicate':<55} {'TTL':>5} {'JSONLD':>6} {'Diff':>6}")
    print(f"  {'-' * 55} {'-' * 5} {'-' * 6} {'-' * 6}")
    for p in all_preds:
        t, j = ttl_preds.get(p, 0), jsonld_preds.get(p, 0)
        diff = j - t
        if diff != 0:
            print(f"  {shorten(p):<55} {t:>5} {j:>6} {diff:>+6}")

    only_jsonld = [(p, jsonld_preds[p]) for p in all_preds if ttl_preds.get(p, 0) == 0 and jsonld_preds.get(p, 0)]
    only_ttl = [(p, ttl_preds[p]) for p in all_preds if jsonld_preds.get(p, 0) == 0 and ttl_preds.get(p, 0)]

    if only_jsonld:
        print(f"\n  PREDICATES ONLY IN JSON-LD ({len(only_jsonld)}):")
        for p, c in only_jsonld:
            print(f"    {shorten(p):<55} count={c}")
    if only_ttl:
        print(f"\n  PREDICATES ONLY IN TTL ({len(only_ttl)}):")
        for p, c in only_ttl:
            print(f"    {shorten(p):<55} count={c}")

    same = sum(1 for p in all_preds if ttl_preds.get(p, 0) == jsonld_preds.get(p, 0))
    diff_count = len(all_preds) - same
    coverage = (same / len(all_preds) * 100) if all_preds else 0
    print(f"\n  Predicates matching: {same}/{len(all_preds)} ({coverage:.1f}%)")
    print(f"  Predicates with differences: {diff_count}")
    print("  STEP 7 RESULT: REPORTED")

    return StepResult(
        STEP_ID,
        STEP_NAME,
        "PASS",  # informational; always considered PASS once reported
        details={
            "predicates_total": len(all_preds),
            "predicates_matching": same,
            "predicates_diff": diff_count,
            "coverage_pct": round(coverage, 1),
            "only_ttl": [shorten(p) for p, _ in only_ttl],
            "only_jsonld": [shorten(p) for p, _ in only_jsonld],
        },
    )


def _cli() -> int:
    if len(sys.argv) < 3:
        print("Usage: python -m validation.steps.step7_gap_analysis <model.ttl> <model.jsonld> [context.jsonld]")
        return 1
    ttl, jsonld = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    ctx = ValidationContext(ttl_path=ttl, jsonld_path=jsonld)
    if len(sys.argv) > 3:
        ctx.context_path = os.path.abspath(sys.argv[3])
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
