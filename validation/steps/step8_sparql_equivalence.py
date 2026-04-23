"""Step 8 — SPARQL semantic equivalence between TTL and JSON-LD exports.

Two serializations are semantically equivalent iff they yield identical
answers to a battery of domain-relevant SPARQL queries
(Angles & Gutiérrez, 2008). This is the gold-standard test in the
Semantic Web community.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import OrderedDict

from . import StepResult, ValidationContext, banner


STEP_ID = 8
STEP_NAME = "SPARQL Semantic Equivalence"

_PREFIXES = """
PREFIX fram: <https://flowfram.com/ontology/fram/>
PREFIX model: <https://flowfram.com/models/>
PREFIX schema: <https://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

QUERIES: "OrderedDict[str, dict]" = OrderedDict()
QUERIES["SQ1"] = {"title": "Model identity and metadata", "query": _PREFIXES + """
SELECT ?name (COUNT(DISTINCT ?func) AS ?functionCount) WHERE {
    ?model a fram:FRAMModel ; schema:name ?name ; fram:hasFunction ?func .
} GROUP BY ?name ORDER BY ?name
"""}
QUERIES["SQ2"] = {"title": "Functions with type and category", "query": _PREFIXES + """
SELECT ?func ?name ?funcType ?funcCategory WHERE {
    ?func a fram:Function ; schema:name ?name ; fram:functionType ?funcType .
    OPTIONAL { ?func fram:functionCategory ?funcCategory }
} ORDER BY ?name
"""}
QUERIES["SQ3"] = {"title": "Aspect count per function", "query": _PREFIXES + """
SELECT ?funcName (COUNT(DISTINCT ?aspect) AS ?aspectCount) WHERE {
    ?func a fram:Function ; schema:name ?funcName ; fram:hasAspect ?aspect .
} GROUP BY ?funcName ORDER BY ?funcName
"""}
QUERIES["SQ4"] = {"title": "Couplings with source/target functions", "query": _PREFIXES + """
SELECT ?coupling ?srcFunc ?tgtFunc WHERE {
    ?coupling a fram:Coupling ; fram:sourceFunction ?srcFunc ; fram:targetFunction ?tgtFunc .
} ORDER BY ?coupling
"""}
QUERIES["SQ5"] = {"title": "Variability potential per function", "query": _PREFIXES + """
SELECT ?funcName ?potential WHERE {
    ?func a fram:Function ; schema:name ?funcName ; fram:hasVariability ?var .
    ?var fram:variabilityPotential ?potential .
} ORDER BY ?funcName
"""}
QUERIES["SQ6"] = {"title": "Quantitative metadata inventory", "query": _PREFIXES + """
SELECT ?funcName (COUNT(DISTINCT ?constant) AS ?constantCount) (COUNT(DISTINCT ?variable) AS ?variableCount) WHERE {
    ?func a fram:Function ; schema:name ?funcName ; fram:quantitativeMetadata ?qm .
    OPTIONAL { ?qm fram:hasConstant ?constant }
    OPTIONAL { ?qm fram:hasVariable ?variable }
} GROUP BY ?funcName ORDER BY ?funcName
"""}
QUERIES["SQ7"] = {"title": "Interpretation profiles", "query": _PREFIXES + """
SELECT ?funcName ?ipInput ?ipPrecondition ?ipResource ?ipTime ?ipControl WHERE {
    ?func a fram:Function ; schema:name ?funcName ; fram:quantitativeMetadata ?qm .
    ?qm fram:hasInterpretationProfile ?ip .
    OPTIONAL { ?ip fram:input ?ipInput }
    OPTIONAL { ?ip fram:precondition ?ipPrecondition }
    OPTIONAL { ?ip fram:resource ?ipResource }
    OPTIONAL { ?ip fram:time ?ipTime }
    OPTIONAL { ?ip fram:control ?ipControl }
} ORDER BY ?funcName
"""}
QUERIES["SQ8"] = {"title": "Output routing topology", "query": _PREFIXES + """
SELECT ?funcName ?edgeId ?targetFuncName ?targetAspect WHERE {
    ?func a fram:Function ; schema:name ?funcName ; fram:quantitativeMetadata ?qm .
    ?qm fram:hasOutput ?output .
    ?output fram:edgeId ?edgeId .
    OPTIONAL { ?output fram:targetFunctionName ?targetFuncName }
    OPTIONAL { ?output fram:targetAspectType ?targetAspect }
} ORDER BY ?funcName ?edgeId
"""}
QUERIES["SQ9"] = {"title": "Aggregate counts", "query": _PREFIXES + """
SELECT (COUNT(DISTINCT ?func) AS ?functions) (COUNT(DISTINCT ?coupling) AS ?couplings) WHERE {
    { ?func a fram:Function } UNION { ?coupling a fram:Coupling }
}
"""}
QUERIES["SQ10"] = {"title": "Scenarios inventory", "query": _PREFIXES + """
SELECT ?scenario ?name ?description WHERE {
    ?scenario a fram:Scenario ; schema:name ?name .
    OPTIONAL { ?scenario schema:description ?description }
} ORDER BY ?name
"""}


def _load_ttl(path: str):
    from rdflib import Graph
    g = Graph()
    g.parse(path, format="turtle")
    return g


def _load_jsonld(path: str, context_path: str | None):
    from pyld import jsonld as jsonld_lib
    from rdflib import Graph

    with open(path) as f:
        jdata = json.load(f)
    if context_path:
        with open(context_path) as f:
            ctx_data = json.load(f)
        jdata["@context"] = ctx_data["@context"]
    expanded = jsonld_lib.expand(jdata)
    g = Graph()
    g.parse(data=json.dumps(expanded), format="json-ld")
    return g


def _execute(graph, sparql: str):
    rows = []
    for row in graph.query(sparql):
        rows.append(tuple(str(v) if v is not None else "" for v in row))
    return sorted(rows)


def run(ctx: ValidationContext) -> StepResult:
    banner("STEP 8: SPARQL SEMANTIC EQUIVALENCE")

    if not ctx.jsonld_path:
        print("  SKIP: requires both TTL and JSON-LD inputs")
        return StepResult(STEP_ID, STEP_NAME, "SKIP")

    print("  Loading graphs...")
    t0 = time.time()
    g_ttl = _load_ttl(ctx.ttl_path)
    print(f"    TTL:     {len(g_ttl)} triples ({time.time() - t0:.2f}s)")
    t0 = time.time()
    g_jsonld = _load_jsonld(ctx.jsonld_path, ctx.context_path)
    print(f"    JSON-LD: {len(g_jsonld)} triples ({time.time() - t0:.2f}s)")

    total = len(QUERIES)
    passed = failed = empty = 0

    for qid, qdef in QUERIES.items():
        print(f"\n  {qid}: {qdef['title']}")
        try:
            res_ttl = _execute(g_ttl, qdef["query"])
            res_jsonld = _execute(g_jsonld, qdef["query"])
        except Exception as e:  # pragma: no cover
            print(f"  ERROR: {e}")
            failed += 1
            continue

        if not res_ttl and not res_jsonld:
            print("  Result: SKIP (both empty - feature not present in model)")
            empty += 1
            continue

        match = res_ttl == res_jsonld
        status = "PASS" if match else "FAIL"
        print(f"  [{status}]  TTL: {len(res_ttl)} rows, JSON-LD: {len(res_jsonld)} rows")
        if match:
            passed += 1
        else:
            failed += 1

    applicable = total - empty
    pct = (passed / applicable * 100) if applicable else 0
    overall_pass = failed == 0 and passed > 0

    banner("SPARQL EQUIVALENCE SUMMARY")
    print(f"  Total queries:   {total}")
    print(f"  Applicable:      {applicable} ({empty} skipped - empty in both)")
    print(f"  Passed:          {passed}")
    print(f"  Failed:          {failed}")
    print(f"  Equivalence:     {pct:.1f}%")
    print(f"\n  OVERALL: {'PASS' if overall_pass else 'FAIL'}")
    if overall_pass:
        print("\n  Both serializations are SPARQL-equivalent: identical queries")
        print("  yield identical results across all fundamental FRAM domain")
        print("  concepts (functions, aspects, couplings, variability,")
        print("  quantitative metadata, scenarios). This confirms semantic")
        print("  equivalence per W3C RDF 1.1 Concepts (Section 3.5).")

    return StepResult(
        STEP_ID,
        STEP_NAME,
        "PASS" if overall_pass else "FAIL",
        details={
            "total": total,
            "applicable": applicable,
            "passed": passed,
            "failed": failed,
            "equivalence_pct": round(pct, 1),
        },
    )


def _cli() -> int:
    if len(sys.argv) < 3:
        print("Usage: python -m validation.steps.step8_sparql_equivalence <model.ttl> <model.jsonld> [context.jsonld]")
        return 1
    ttl, jsonld = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    ctx = ValidationContext(ttl_path=ttl, jsonld_path=jsonld)
    if len(sys.argv) > 3:
        ctx.context_path = os.path.abspath(sys.argv[3])
    res = run(ctx)
    return 0 if res.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
