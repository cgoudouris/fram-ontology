"""Step 6 — Round-trip fidelity between TTL and JSON-LD serializations.

Three round-trip tests are executed:

* RT1: TTL -> JSON-LD -> TTL (graph isomorphism check)
* RT2: JSON-LD -> TTL -> JSON-LD (graph isomorphism check)
* RT3: TTL == JSON-LD (direct cross-format graph comparison)

The step's overall status is bound to RT1 (the strongest invariant the
TBox can guarantee given the current exporters). RT2/RT3 are reported
for diagnostic purposes.
"""
from __future__ import annotations

import json
import os
import sys
import time

from . import StepResult, ValidationContext, banner, shorten


STEP_ID = 6
STEP_NAME = "Round-trip Fidelity (RT1)"


def _load_jsonld_with_context(path: str, context_path: str | None):
    from pyld import jsonld as jsonld_lib
    from rdflib import Graph

    with open(path) as f:
        jdata = json.load(f)
    if context_path:
        with open(context_path) as f:
            ctx_data = json.load(f)
        jdata["@context"] = ctx_data["@context"]
    nquads = jsonld_lib.to_rdf(jdata, {"format": "application/n-quads"})
    g = Graph()
    g.parse(data=nquads, format="nquads")
    return g


def _named_triples(g):
    from rdflib import URIRef

    out = set()
    for s, p, o in g:
        if isinstance(s, URIRef):
            o_str = str(o) if isinstance(o, URIRef) else f'"{o}"'
            out.add((str(s), str(p), o_str))
    return out


def _bnode_triple_count(g) -> int:
    from rdflib import BNode

    return sum(1 for s, _, o in g if isinstance(s, BNode) or isinstance(o, BNode))


def _triple_diff(g1, g2, label1: str, label2: str, max_show: int = 10):
    n1, n2 = _named_triples(g1), _named_triples(g2)
    only1, only2, shared = n1 - n2, n2 - n1, n1 & n2
    print(f"\n  Named triples:  {label1}={len(n1)}, {label2}={len(n2)}, shared={len(shared)}")
    print(f"  BNode triples:  {label1}={_bnode_triple_count(g1)}, {label2}={_bnode_triple_count(g2)}")
    for label, only in ((label1, only1), (label2, only2)):
        if only:
            print(f"\n  Only in {label} ({len(only)}):")
            for s, p, o in sorted(only)[:max_show]:
                print(f"    {shorten(s)}  {shorten(p)}  {shorten(o)}")
            if len(only) > max_show:
                print(f"    ... and {len(only) - max_show} more")
    if not only1 and not only2:
        print("\n  [OK] All named triples match perfectly!")
    return len(only1), len(only2), len(shared)


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 6: ROUND-TRIP FIDELITY")

    if not ctx.jsonld_path:
        print("  SKIP: requires both TTL and JSON-LD inputs")
        return StepResult(STEP_ID, STEP_NAME, "SKIP")

    from rdflib import Graph, compare

    # ------------------------------------------------------------------
    # RT1: TTL -> JSON-LD -> TTL
    # ------------------------------------------------------------------
    banner("RT1: TTL -> serialize as JSON-LD -> parse back", width=70)
    print(f"  Source: {os.path.basename(ctx.ttl_path)}")
    t0 = time.time()
    g_ttl_orig = Graph()
    g_ttl_orig.parse(ctx.ttl_path, format="turtle")
    print(f"  [1/3] Parsed TTL: {len(g_ttl_orig)} triples")
    jsonld_bytes = g_ttl_orig.serialize(format="json-ld")
    print(f"  [2/3] Serialized as JSON-LD: {len(jsonld_bytes)} bytes")
    g_ttl_rt = Graph()
    g_ttl_rt.parse(data=jsonld_bytes, format="json-ld")
    print(f"  [3/3] Parsed back: {len(g_ttl_rt)} triples")
    iso_rt1 = compare.isomorphic(g_ttl_orig, g_ttl_rt)
    print(f"\n  Isomorphic: {'YES' if iso_rt1 else 'NO'} ({time.time() - t0:.2f}s)")
    if not iso_rt1:
        _triple_diff(g_ttl_orig, g_ttl_rt, "TTL-orig", "TTL-roundtrip")

    # ------------------------------------------------------------------
    # RT2: JSON-LD -> TTL -> JSON-LD
    # ------------------------------------------------------------------
    banner("RT2: JSON-LD -> serialize as TTL -> parse back", width=70)
    print(f"  Source: {os.path.basename(ctx.jsonld_path)}")
    t0 = time.time()
    g_jsonld_orig = _load_jsonld_with_context(ctx.jsonld_path, ctx.context_path)
    print(f"  [1/3] Parsed JSON-LD (via pyld): {len(g_jsonld_orig)} triples")
    ttl_bytes = g_jsonld_orig.serialize(format="turtle")
    print(f"  [2/3] Serialized as Turtle: {len(ttl_bytes)} bytes")
    g_jsonld_rt = Graph()
    g_jsonld_rt.parse(data=ttl_bytes, format="turtle")
    print(f"  [3/3] Parsed back: {len(g_jsonld_rt)} triples")
    iso_rt2 = compare.isomorphic(g_jsonld_orig, g_jsonld_rt)
    print(f"\n  Isomorphic: {'YES' if iso_rt2 else 'NO'} ({time.time() - t0:.2f}s)")
    if not iso_rt2:
        _triple_diff(g_jsonld_orig, g_jsonld_rt, "JSONLD-orig", "JSONLD-roundtrip")

    # ------------------------------------------------------------------
    # RT3: Direct comparison
    # ------------------------------------------------------------------
    banner("RT3: Direct cross-format graph comparison", width=70)
    print(f"  TTL:     {os.path.basename(ctx.ttl_path)} ({len(g_ttl_orig)} triples)")
    print(f"  JSON-LD: {os.path.basename(ctx.jsonld_path)} ({len(g_jsonld_orig)} triples)")
    t0 = time.time()
    iso_rt3 = compare.isomorphic(g_ttl_orig, g_jsonld_orig)
    print(f"\n  Isomorphic: {'YES' if iso_rt3 else 'NO'} ({time.time() - t0:.2f}s)")
    only_ttl, only_jsonld, shared = _triple_diff(g_ttl_orig, g_jsonld_orig, "TTL", "JSON-LD")
    coverage = (shared / (shared + only_ttl) * 100) if (shared + only_ttl) else 0
    print(f"\n  TTL coverage in JSON-LD: {coverage:.1f}%")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    banner("ROUND-TRIP SUMMARY")
    tests = [
        ("RT1: TTL -> JSON-LD -> TTL", iso_rt1),
        ("RT2: JSON-LD -> TTL -> JSON-LD", iso_rt2),
        ("RT3: TTL == JSON-LD (direct)", iso_rt3),
    ]
    for name, passed in tests:
        print(f"  {name:40s} {'PASS' if passed else 'FAIL'}")

    overall_pass = iso_rt1
    print(f"\n  OVERALL: {'PASS' if overall_pass else 'FAIL'}")

    if not iso_rt3:
        if only_ttl == 0 and only_jsonld > 0:
            print(f"\n  Note: TTL is a proper subset of JSON-LD ({only_jsonld} extra named triples in JSON-LD).")
        elif only_ttl and only_jsonld:
            print(f"\n  Note: {only_ttl} named triples only in TTL, {only_jsonld} only in JSON-LD.")
        elif only_ttl and only_jsonld == 0:
            print(f"\n  Note: JSON-LD is a proper subset of TTL ({only_ttl} extra named triples in TTL).")

    return StepResult(
        STEP_ID,
        STEP_NAME,
        "PASS" if overall_pass else "FAIL",
        details={
            "rt1": iso_rt1,
            "rt2": iso_rt2,
            "rt3": iso_rt3,
            "only_ttl": only_ttl,
            "only_jsonld": only_jsonld,
            "shared": shared,
        },
    )


def _cli() -> int:
    if len(sys.argv) < 3:
        print("Usage: python -m validation.steps.step6_roundtrip <model.ttl> <model.jsonld> [context.jsonld]")
        return 1
    ttl, jsonld = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    ctx = ValidationContext(ttl_path=ttl, jsonld_path=jsonld)
    if len(sys.argv) > 3:
        ctx.context_path = os.path.abspath(sys.argv[3])
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
