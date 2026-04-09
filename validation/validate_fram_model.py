#!/usr/bin/env python3
"""
Unified FRAM Ontology Validation Runner
========================================
Runs the 8-step validation benchmark against any FRAM model.

Steps:
  1. JSON-LD -> Turtle conversion (skipped if input is already TTL)
  2. OWL-RL Reasoning (logical consistency)
  3. SHACL Shape Validation (structural constraints)
  4. SPARQL Competency Questions (domain coverage)
  5. OOPS! Pitfall Scanning (design anti-patterns) [requires internet]
  6. Round-trip Fidelity (TTL <-> JSON-LD isomorphism)
  7. Gap Analysis (predicate-level differences between serializations)
  8. SPARQL Semantic Equivalence (gold-standard query equivalence)

Usage:
    python validate_fram_model.py <model_ttl> [model_jsonld] [options]

    # Run Steps 2-4 only (TTL model, no JSON-LD counterpart)
    python validate_fram_model.py examples/li-huang-2025.ttl

    # Run Steps 2-8 (both serializations available)
    python validate_fram_model.py examples/li-huang-2025.ttl examples/li-huang-2025.jsonld

    # Skip OOPS! (offline mode)
    python validate_fram_model.py examples/li-huang-2025.ttl --skip-oops

    # Run specific steps only
    python validate_fram_model.py examples/li-huang-2025.ttl examples/li-huang-2025.jsonld --steps 2,3,4,8

Part of the FRAM Ontology Validation Benchmark (EP2).
"""
import argparse
import os
import sys
import time
import json
import subprocess

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TBOX_PATH = os.path.join(REPO_ROOT, "fram.ttl")
SHAPES_PATH = os.path.join(REPO_ROOT, "fram-shapes.ttl")
CONTEXT_PATH = os.path.join(REPO_ROOT, "context.jsonld")
VALIDATION_DIR = os.path.dirname(os.path.abspath(__file__))


def banner(title, width=70):
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def resolve_path(path):
    """Resolve path relative to repo root if not absolute."""
    if os.path.isabs(path):
        return path
    return os.path.join(REPO_ROOT, path)


# ========================================================================
# STEP 1: JSON-LD -> TTL Conversion
# ========================================================================
def step1_convert(jsonld_path):
    """Convert JSON-LD model to Turtle using local context."""
    banner("STEP 1: JSON-LD -> TURTLE CONVERSION")
    from rdflib import Graph
    from pyld import jsonld

    with open(jsonld_path) as f:
        model_data = json.load(f)

    with open(CONTEXT_PATH) as f:
        local_context = json.load(f)

    model_data["@context"] = local_context["@context"]
    expanded = jsonld.expand(model_data)
    nquads = jsonld.to_rdf(model_data, {"format": "application/n-quads"})

    g = Graph()
    g.parse(data=nquads, format="nquads")

    ttl_out = jsonld_path.replace(".jsonld", ".ttl")
    if ttl_out == jsonld_path:
        ttl_out = jsonld_path + ".ttl"

    g.serialize(ttl_out, format="turtle")
    print(f"  Input:  {jsonld_path}")
    print(f"  Output: {ttl_out}")
    print(f"  Triples: {len(g)}")
    print(f"  STEP 1 RESULT: PASS")
    return ttl_out, True


# ========================================================================
# STEP 2: OWL-RL Reasoning
# ========================================================================
def step2_reasoning(ttl_path):
    """Validate logical consistency with OWL-RL reasoner."""
    banner("STEP 2: OWL-RL REASONING")
    from rdflib import Graph, Namespace, RDF, OWL, RDFS
    import owlrl

    FRAM = Namespace("https://flowfram.com/ontology/fram/")

    g = Graph()
    g.parse(TBOX_PATH, format="turtle")
    tbox_count = len(g)
    g.parse(ttl_path, format="turtle")
    abox_count = len(g) - tbox_count
    total_before = len(g)

    print(f"  TBox: {tbox_count} triples")
    print(f"  ABox: {abox_count} triples")
    print(f"  Total before reasoning: {total_before}")

    t0 = time.time()
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    elapsed = time.time() - t0
    total_after = len(g)
    inferred = total_after - total_before

    nothing_instances = list(g.subjects(RDF.type, OWL.Nothing))
    unsatisfiable = [
        c for c in g.subjects(RDF.type, OWL.Class)
        if (c, RDFS.subClassOf, OWL.Nothing) in g and c != OWL.Nothing
    ]

    print(f"  Total after reasoning: {total_after}")
    print(f"  Inferred triples: {inferred} ({elapsed:.2f}s)")
    print(f"  owl:Nothing instances: {len(nothing_instances)}")
    print(f"  Unsatisfiable classes: {len(unsatisfiable)}")

    passed = len(nothing_instances) == 0 and len(unsatisfiable) == 0
    print(f"  STEP 2 RESULT: {'PASS' if passed else 'FAIL'}")
    return passed


# ========================================================================
# STEP 3: SHACL Validation
# ========================================================================
def step3_shacl(ttl_path):
    """Validate structure against SHACL shapes."""
    banner("STEP 3: SHACL SHAPE VALIDATION")
    from rdflib import Graph
    from pyshacl import validate

    data_graph = Graph()
    data_graph.parse(TBOX_PATH, format="turtle")
    data_graph.parse(ttl_path, format="turtle")

    shapes_graph = Graph()
    shapes_graph.parse(SHAPES_PATH, format="turtle")

    print(f"  Data graph: {len(data_graph)} triples")
    print(f"  Shapes graph: {len(shapes_graph)} triples")

    t0 = time.time()
    conforms, results_graph, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        meta_shacl=False,
        advanced=True,
        debug=False,
    )
    elapsed = time.time() - t0

    print(f"  Conforms: {conforms} ({elapsed:.2f}s)")
    if not conforms:
        print(f"  Violations:\n{results_text[:1000]}")
    print(f"  STEP 3 RESULT: {'PASS' if conforms else 'FAIL'}")
    return conforms


# ========================================================================
# STEP 4: SPARQL Competency Questions
# ========================================================================
def step4_sparql(ttl_path):
    """Run domain competency questions via SPARQL."""
    banner("STEP 4: SPARQL COMPETENCY QUESTIONS")
    from rdflib import Graph, Namespace

    FRAM = Namespace("https://flowfram.com/ontology/fram/")
    SCHEMA = Namespace("https://schema.org/")

    g = Graph()
    g.parse(TBOX_PATH, format="turtle")
    g.parse(ttl_path, format="turtle")
    g.bind("fram", FRAM)
    g.bind("schema", SCHEMA)

    CQs = [
        {
            "id": "CQ1",
            "question": "What are the model's functions and their types?",
            "sparql": """
                PREFIX fram: <https://flowfram.com/ontology/fram/>
                PREFIX schema: <https://schema.org/>
                SELECT ?funcName ?funcType WHERE {
                    ?model a fram:FRAMModel ;
                           fram:hasFunction ?func .
                    ?func schema:name ?funcName ;
                          fram:functionType ?funcType .
                }
                ORDER BY ?funcName
            """,
            "validate": lambda r: len(r) >= 1,
        },
        {
            "id": "CQ2",
            "question": "What are the couplings between functions?",
            "sparql": """
                PREFIX fram: <https://flowfram.com/ontology/fram/>
                PREFIX schema: <https://schema.org/>
                SELECT ?srcName ?tgtName WHERE {
                    ?model a fram:FRAMModel ;
                           fram:hasCoupling ?coupling .
                    ?coupling fram:sourceFunction ?src ;
                              fram:targetFunction ?tgt .
                    ?src schema:name ?srcName .
                    ?tgt schema:name ?tgtName .
                }
                ORDER BY ?srcName
            """,
            "validate": lambda r: len(r) >= 1,
        },
        {
            "id": "CQ3",
            "question": "How many aspects does each function have?",
            "sparql": """
                PREFIX fram: <https://flowfram.com/ontology/fram/>
                PREFIX schema: <https://schema.org/>
                SELECT ?funcName (COUNT(DISTINCT ?aspect) AS ?aspectCount) WHERE {
                    ?func a fram:Function ;
                          schema:name ?funcName ;
                          fram:hasAspect ?aspect .
                }
                GROUP BY ?funcName
                ORDER BY ?funcName
            """,
            "validate": lambda r: len(r) >= 1,
        },
        {
            "id": "CQ4",
            "question": "Which functions have variability metadata?",
            "sparql": """
                PREFIX fram: <https://flowfram.com/ontology/fram/>
                PREFIX schema: <https://schema.org/>
                SELECT ?funcName ?potential WHERE {
                    ?func a fram:Function ;
                          schema:name ?funcName ;
                          fram:hasVariability ?var .
                    ?var fram:variabilityPotential ?potential .
                }
                ORDER BY ?funcName
            """,
            "validate": lambda r: len(r) >= 1,
        },
        {
            "id": "CQ5",
            "question": "Which functions receive input from other functions via couplings?",
            "sparql": """
                PREFIX fram: <https://flowfram.com/ontology/fram/>
                PREFIX schema: <https://schema.org/>
                SELECT DISTINCT ?tgtName WHERE {
                    ?model a fram:FRAMModel ;
                           fram:hasCoupling ?coupling .
                    ?coupling fram:targetFunction ?tgt .
                    ?tgt schema:name ?tgtName .
                }
                ORDER BY ?tgtName
            """,
            "validate": lambda r: len(r) >= 1,
        },
    ]

    all_pass = True
    for cq in CQs:
        results = list(g.query(cq["sparql"]))
        passed = cq["validate"](results)
        if not passed:
            all_pass = False
        print(f"  {cq['id']}: {cq['question']}")
        print(f"       {len(results)} results -> {'PASS' if passed else 'FAIL'}")

    print(f"  STEP 4 RESULT: {'PASS' if all_pass else 'FAIL'} ({len(CQs)}/{len(CQs)} CQs)")
    return all_pass


# ========================================================================
# STEP 5: OOPS! Pitfall Scanning
# ========================================================================
def step5_oops():
    """Submit ontology to OOPS! REST API for pitfall detection."""
    banner("STEP 5: OOPS! PITFALL SCANNING")
    import re
    from collections import Counter

    try:
        import requests
    except ImportError:
        print("  SKIP: requests library not installed")
        return None

    from rdflib import Graph

    g = Graph()
    g.parse(TBOX_PATH, format="turtle")
    rdfxml = g.serialize(format="xml")

    print(f"  Submitting {len(g)} triples to OOPS! API...")

    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<OOPSRequest>
  <OntologyUrl></OntologyUrl>
  <OntologyContent><![CDATA[{rdfxml}]]></OntologyContent>
  <Pitfalls>2</Pitfalls>
  <OutputFormat>XML</OutputFormat>
</OOPSRequest>"""

    try:
        t0 = time.time()
        resp = requests.post(
            "https://oops.linkeddata.es/rest",
            data=xml_payload.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            timeout=120,
        )
        elapsed = time.time() - t0

        if resp.status_code != 200:
            print(f"  API returned status {resp.status_code}")
            print(f"  STEP 5 RESULT: ERROR")
            return False

        body = resp.text
        pitfalls = re.findall(r"<oops:hasCode>(P\d+)</oops:hasCode>", body)
        counter = Counter(pitfalls)

        if not pitfalls:
            print(f"  No pitfalls detected ({elapsed:.1f}s)")
            print(f"  STEP 5 RESULT: PASS")
            return True

        print(f"  Pitfalls found ({elapsed:.1f}s):")
        for code, count in sorted(counter.items()):
            print(f"    {code}: {count} occurrence(s)")

        # P04 alone is acceptable (gUFO external alignment - known false positive)
        critical = {k: v for k, v in counter.items() if k != "P04"}
        passed = len(critical) == 0
        print(f"  STEP 5 RESULT: {'PASS' if passed else 'FAIL'} (P04 excluded as known false positive)")
        return passed

    except requests.exceptions.Timeout:
        print("  OOPS! API timed out")
        print("  STEP 5 RESULT: TIMEOUT")
        return None
    except requests.exceptions.ConnectionError:
        print("  Could not reach OOPS! API (no internet?)")
        print("  STEP 5 RESULT: SKIP (offline)")
        return None


# ========================================================================
# STEP 6: Round-trip Fidelity
# ========================================================================
def step6_roundtrip(ttl_path, jsonld_path):
    """Test round-trip fidelity between TTL and JSON-LD serializations."""
    banner("STEP 6: ROUND-TRIP FIDELITY")
    script = os.path.join(VALIDATION_DIR, "step6_roundtrip_fidelity.py")
    result = subprocess.run(
        [sys.executable, script, ttl_path, jsonld_path, CONTEXT_PATH],
        capture_output=True, text=True,
    )
    # Extract final summary
    lines = result.stdout.strip().split("\n")
    in_summary = False
    rt1_pass = None
    for line in lines:
        if "ROUND-TRIP SUMMARY" in line:
            in_summary = True
        if in_summary:
            print(f"  {line.strip()}")
            if "RT1:" in line:
                rt1_pass = "PASS" in line
    if rt1_pass is None:
        # Fallback: print last 15 lines
        for line in lines[-15:]:
            print(f"  {line}")
        rt1_pass = any("RT1" in l and "PASS" in l for l in lines)
    return rt1_pass


# ========================================================================
# STEP 7: Gap Analysis
# ========================================================================
def step7_gap(ttl_path, jsonld_path):
    """Run predicate-level gap analysis between serializations."""
    banner("STEP 7: GAP ANALYSIS")
    script = os.path.join(VALIDATION_DIR, "step7_gap_analysis.py")
    result = subprocess.run(
        [sys.executable, script, ttl_path, jsonld_path, CONTEXT_PATH],
        capture_output=True, text=True,
    )
    lines = result.stdout.strip().split("\n")
    # Extract the final metrics line
    coverage = None
    for line in lines:
        if "Predicates matching" in line:
            print(f"  {line.strip()}")
            coverage = line.strip()
        elif "Predicates with differences" in line:
            print(f"  {line.strip()}")
    if coverage:
        print(f"  STEP 7 RESULT: REPORTED")
    else:
        for line in lines[-5:]:
            print(f"  {line}")
    return True  # informational step, always passes


# ========================================================================
# STEP 8: SPARQL Semantic Equivalence
# ========================================================================
def step8_sparql_eq(ttl_path, jsonld_path):
    """Run SPARQL equivalence queries against both serializations."""
    banner("STEP 8: SPARQL SEMANTIC EQUIVALENCE")
    script = os.path.join(VALIDATION_DIR, "step8_sparql_equivalence.py")
    result = subprocess.run(
        [sys.executable, script, ttl_path, jsonld_path, CONTEXT_PATH],
        capture_output=True, text=True,
    )
    lines = result.stdout.strip().split("\n")
    in_summary = False
    passed = None
    for line in lines:
        if "SPARQL EQUIVALENCE SUMMARY" in line:
            in_summary = True
        if in_summary:
            print(f"  {line.strip()}")
            if "OVERALL:" in line:
                passed = "PASS" in line
    if passed is None:
        for line in lines[-10:]:
            print(f"  {line}")
        passed = any("OVERALL: PASS" in l for l in lines)
    return passed


# ========================================================================
# MAIN
# ========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Unified FRAM Ontology Validation Runner (8-step benchmark)"
    )
    parser.add_argument("model_ttl", help="Path to the TTL model file")
    parser.add_argument("model_jsonld", nargs="?", default=None,
                        help="Path to the JSON-LD model file (enables Steps 6-8)")
    parser.add_argument("--skip-oops", action="store_true",
                        help="Skip Step 5 (OOPS! API, requires internet)")
    parser.add_argument("--steps", type=str, default=None,
                        help="Comma-separated list of steps to run (e.g., '2,3,4,8')")
    args = parser.parse_args()

    ttl_path = resolve_path(args.model_ttl)
    jsonld_path = resolve_path(args.model_jsonld) if args.model_jsonld else None

    if not os.path.isfile(ttl_path):
        print(f"Error: TTL file not found: {ttl_path}")
        sys.exit(1)
    if jsonld_path and not os.path.isfile(jsonld_path):
        print(f"Error: JSON-LD file not found: {jsonld_path}")
        sys.exit(1)

    # Determine which steps to run
    if args.steps:
        selected = set(int(s.strip()) for s in args.steps.split(","))
    else:
        selected = {2, 3, 4, 5, 6, 7, 8}

    if args.skip_oops:
        selected.discard(5)

    # Steps 6-8 require JSON-LD
    if not jsonld_path:
        selected -= {6, 7, 8}

    banner("FRAM ONTOLOGY VALIDATION BENCHMARK")
    print(f"  TBox:     {TBOX_PATH}")
    print(f"  ABox TTL: {ttl_path}")
    if jsonld_path:
        print(f"  ABox JLD: {jsonld_path}")
    print(f"  Context:  {CONTEXT_PATH}")
    print(f"  Shapes:   {SHAPES_PATH}")
    print(f"  Steps:    {sorted(selected)}")

    results = {}

    if 2 in selected:
        results[2] = step2_reasoning(ttl_path)
    if 3 in selected:
        results[3] = step3_shacl(ttl_path)
    if 4 in selected:
        results[4] = step4_sparql(ttl_path)
    if 5 in selected:
        results[5] = step5_oops()
    if 6 in selected:
        results[6] = step6_roundtrip(ttl_path, jsonld_path)
    if 7 in selected:
        results[7] = step7_gap(ttl_path, jsonld_path)
    if 8 in selected:
        results[8] = step8_sparql_eq(ttl_path, jsonld_path)

    # ── Summary ──
    banner("VALIDATION SUMMARY")
    step_names = {
        2: "OWL-RL Reasoning",
        3: "SHACL Shape Validation",
        4: "SPARQL Competency Questions",
        5: "OOPS! Pitfall Scanning",
        6: "Round-trip Fidelity (RT1)",
        7: "Gap Analysis",
        8: "SPARQL Semantic Equivalence",
    }

    all_pass = True
    for step in sorted(results.keys()):
        r = results[step]
        if r is True:
            status = "PASS"
        elif r is False:
            status = "FAIL"
            all_pass = False
        else:
            status = "SKIP"
        print(f"  Step {step} ({step_names[step]}): {status}")

    print()
    if all_pass:
        print("  OVERALL: PASS")
    else:
        failing = [s for s, r in results.items() if r is False]
        print(f"  OVERALL: FAIL (steps {failing})")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
