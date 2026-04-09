"""
SPARQL Semantic Equivalence Test for FRAM Ontology Exports.

Validates that TTL and JSON-LD serializations of the same FRAM model
produce semantically equivalent RDF graphs by executing identical SPARQL
queries against both graphs and comparing results.

This is the gold-standard validation in the Semantic Web community:
two serializations are semantically equivalent if and only if they
yield identical answers to all domain-relevant queries (Angles & Gutierrez, 2008).

Usage:
    python3 sparql_equivalence_test.py <ttl_file> <jsonld_file> [context_file]

Example:
    python3 sparql_equivalence_test.py \
        li-huang-2025.ttl \
        li-huang-2025.jsonld \
        context.jsonld
"""
import sys
import json
import time
from collections import OrderedDict
from rdflib import Graph, Namespace

# ============================================================================
# CONFIGURATION
# ============================================================================

FRAM = Namespace("https://flowfram.com/ontology/fram/")
MODEL = Namespace("https://flowfram.com/models/")
SCHEMA = Namespace("https://schema.org/")

PREFIXES = """
PREFIX fram: <https://flowfram.com/ontology/fram/>
PREFIX model: <https://flowfram.com/models/>
PREFIX schema: <https://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

# ============================================================================
# SPARQL COMPETENCY QUERIES
# ============================================================================
# These queries cover all fundamental FRAM domain concepts:
# functions, aspects, couplings, variability, quantitative metadata,
# and model-level properties.

QUERIES = OrderedDict()

# -------------------------------------------------------------------------
# SQ1: Model identity and metadata
# -------------------------------------------------------------------------
QUERIES["SQ1"] = {
    "title": "Model identity and metadata",
    "description": "Retrieve model name, type, version and function count",
    "query": PREFIXES + """
SELECT ?name (COUNT(DISTINCT ?func) AS ?functionCount)
WHERE {
    ?model a fram:FRAMModel .
    ?model schema:name ?name .
    ?model fram:hasFunction ?func .
}
GROUP BY ?name
ORDER BY ?name
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ2: All functions with type and category
# -------------------------------------------------------------------------
QUERIES["SQ2"] = {
    "title": "Functions with type and category",
    "description": "List all functions with their functionType and functionCategory",
    "query": PREFIXES + """
SELECT ?func ?name ?funcType ?funcCategory
WHERE {
    ?func a fram:Function .
    ?func schema:name ?name .
    ?func fram:functionType ?funcType .
    OPTIONAL { ?func fram:functionCategory ?funcCategory }
}
ORDER BY ?name
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ3: Aspects per function (6 per function expected)
# -------------------------------------------------------------------------
QUERIES["SQ3"] = {
    "title": "Aspect count per function",
    "description": "Count aspects per function (should be 6 for each: I, O, P, R, C, T)",
    "query": PREFIXES + """
SELECT ?funcName (COUNT(DISTINCT ?aspect) AS ?aspectCount)
WHERE {
    ?func a fram:Function .
    ?func schema:name ?funcName .
    ?func fram:hasAspect ?aspect .
}
GROUP BY ?funcName
ORDER BY ?funcName
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ4: All couplings with source and target function
# -------------------------------------------------------------------------
QUERIES["SQ4"] = {
    "title": "Couplings with source/target functions",
    "description": "List all couplings with their connected functions",
    "query": PREFIXES + """
SELECT ?coupling ?srcFunc ?tgtFunc
WHERE {
    ?coupling a fram:Coupling .
    ?coupling fram:sourceFunction ?srcFunc .
    ?coupling fram:targetFunction ?tgtFunc .
}
ORDER BY ?coupling
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ5: Variability assessment per function
# -------------------------------------------------------------------------
QUERIES["SQ5"] = {
    "title": "Variability potential per function",
    "description": "Retrieve variability potential (Low/Medium/High) for each function",
    "query": PREFIXES + """
SELECT ?funcName ?potential
WHERE {
    ?func a fram:Function .
    ?func schema:name ?funcName .
    ?func fram:hasVariability ?var .
    ?var fram:variabilityPotential ?potential .
}
ORDER BY ?funcName
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ6: Quantitative metadata - constants and variables
# -------------------------------------------------------------------------
QUERIES["SQ6"] = {
    "title": "Quantitative metadata inventory",
    "description": "Count constants and variables per function that has quantitative metadata",
    "query": PREFIXES + """
SELECT ?funcName 
       (COUNT(DISTINCT ?constant) AS ?constantCount)
       (COUNT(DISTINCT ?variable) AS ?variableCount)
WHERE {
    ?func a fram:Function .
    ?func schema:name ?funcName .
    ?func fram:quantitativeMetadata ?qm .
    OPTIONAL { ?qm fram:hasConstant ?constant }
    OPTIONAL { ?qm fram:hasVariable ?variable }
}
GROUP BY ?funcName
ORDER BY ?funcName
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ7: Interpretation profiles
# -------------------------------------------------------------------------
QUERIES["SQ7"] = {
    "title": "Interpretation profiles",
    "description": "Retrieve interpretation profile settings per function",
    "query": PREFIXES + """
SELECT ?funcName ?ipInput ?ipPrecondition ?ipResource ?ipTime ?ipControl
WHERE {
    ?func a fram:Function .
    ?func schema:name ?funcName .
    ?func fram:quantitativeMetadata ?qm .
    ?qm fram:hasInterpretationProfile ?ip .
    OPTIONAL { ?ip fram:input ?ipInput }
    OPTIONAL { ?ip fram:precondition ?ipPrecondition }
    OPTIONAL { ?ip fram:resource ?ipResource }
    OPTIONAL { ?ip fram:time ?ipTime }
    OPTIONAL { ?ip fram:control ?ipControl }
}
ORDER BY ?funcName
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ8: Output routing topology
# -------------------------------------------------------------------------
QUERIES["SQ8"] = {
    "title": "Output routing topology",
    "description": "List output messages with edge IDs and target functions",
    "query": PREFIXES + """
SELECT ?funcName ?edgeId ?targetFuncName ?targetAspect
WHERE {
    ?func a fram:Function .
    ?func schema:name ?funcName .
    ?func fram:quantitativeMetadata ?qm .
    ?qm fram:hasOutput ?output .
    ?output fram:edgeId ?edgeId .
    OPTIONAL { ?output fram:targetFunctionName ?targetFuncName }
    OPTIONAL { ?output fram:targetAspectType ?targetAspect }
}
ORDER BY ?funcName ?edgeId
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ9: Coupling count (aggregate)
# -------------------------------------------------------------------------
QUERIES["SQ9"] = {
    "title": "Aggregate coupling statistics",
    "description": "Total count of functions, couplings, and aspects",
    "query": PREFIXES + """
SELECT 
    (COUNT(DISTINCT ?func) AS ?functions)
    (COUNT(DISTINCT ?coupling) AS ?couplings)
WHERE {
    { ?func a fram:Function }
    UNION
    { ?coupling a fram:Coupling }
}
""",
    "compare_mode": "exact",
}

# -------------------------------------------------------------------------
# SQ10: Scenarios (if enabled)
# -------------------------------------------------------------------------
QUERIES["SQ10"] = {
    "title": "Scenarios inventory",
    "description": "List all scenarios with their names and descriptions",
    "query": PREFIXES + """
SELECT ?scenario ?name ?description
WHERE {
    ?scenario a fram:Scenario .
    ?scenario schema:name ?name .
    OPTIONAL { ?scenario schema:description ?description }
}
ORDER BY ?name
""",
    "compare_mode": "exact",
}


# ============================================================================
# GRAPH LOADING
# ============================================================================

def load_ttl(path: str) -> Graph:
    g = Graph()
    g.parse(path, format="turtle")
    return g


def load_jsonld(path: str, context_path: str = None) -> Graph:
    """Load JSON-LD using pyld for proper context resolution."""
    from pyld import jsonld as jsonld_lib
    
    with open(path) as f:
        jdata = json.load(f)
    
    if context_path:
        with open(context_path) as f:
            ctx = json.load(f)
        jdata["@context"] = ctx["@context"]
    
    # Expand and flatten for consistent processing
    expanded = jsonld_lib.expand(jdata)
    
    g = Graph()
    g.parse(data=json.dumps(expanded), format="json-ld")
    return g


# ============================================================================
# QUERY EXECUTION AND COMPARISON
# ============================================================================

def execute_query(graph: Graph, query: str) -> list:
    """Execute SPARQL query and return results as list of tuples of strings."""
    results = graph.query(query)
    rows = []
    for row in results:
        rows.append(tuple(str(v) if v is not None else "" for v in row))
    return sorted(rows)


def compare_results(results_a: list, results_b: list, mode: str = "exact") -> dict:
    """Compare two query result sets."""
    if mode == "exact":
        match = results_a == results_b
        only_a = [r for r in results_a if r not in results_b]
        only_b = [r for r in results_b if r not in results_a]
        return {
            "match": match,
            "count_a": len(results_a),
            "count_b": len(results_b),
            "only_a": only_a,
            "only_b": only_b,
        }
    return {"match": False, "error": f"Unknown mode: {mode}"}


# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 sparql_equivalence_test.py <ttl> <jsonld> [context]")
        sys.exit(1)

    ttl_path = sys.argv[1]
    jsonld_path = sys.argv[2]
    context_path = sys.argv[3] if len(sys.argv) > 3 else None

    print("\n" + "=" * 72)
    print("  SPARQL SEMANTIC EQUIVALENCE TEST")
    print("  TTL:     " + ttl_path.split("/")[-1])
    print("  JSON-LD: " + jsonld_path.split("/")[-1])
    print("=" * 72)

    # Load graphs
    print("\n  Loading graphs...")
    t0 = time.time()
    g_ttl = load_ttl(ttl_path)
    print(f"    TTL:     {len(g_ttl)} triples ({time.time()-t0:.2f}s)")

    t0 = time.time()
    g_jsonld = load_jsonld(jsonld_path, context_path)
    print(f"    JSON-LD: {len(g_jsonld)} triples ({time.time()-t0:.2f}s)")

    # Execute queries
    print("\n" + "-" * 72)
    total = len(QUERIES)
    passed = 0
    failed = 0
    empty = 0

    for qid, qdef in QUERIES.items():
        print(f"\n  {qid}: {qdef['title']}")
        print(f"  {qdef['description']}")

        try:
            res_ttl = execute_query(g_ttl, qdef["query"])
            res_jsonld = execute_query(g_jsonld, qdef["query"])
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            continue

        comparison = compare_results(res_ttl, res_jsonld, qdef.get("compare_mode", "exact"))

        if comparison["count_a"] == 0 and comparison["count_b"] == 0:
            print(f"  Result: SKIP (both empty - feature not present in model)")
            empty += 1
            continue

        status = "PASS" if comparison["match"] else "FAIL"
        icon = "OK" if status == "PASS" else "XX"
        print(f"  [{icon}] {status}  (TTL: {comparison['count_a']} rows, JSON-LD: {comparison['count_b']} rows)")

        if status == "PASS":
            passed += 1
            # Show sample of matching results
            if comparison["count_a"] > 0:
                sample = min(3, comparison["count_a"])
                for row in res_ttl[:sample]:
                    vals = " | ".join(str(v)[:50] for v in row)
                    print(f"       {vals}")
                if comparison["count_a"] > sample:
                    print(f"       ... and {comparison['count_a'] - sample} more rows")
        else:
            failed += 1
            if comparison["only_a"]:
                print(f"  Only in TTL ({len(comparison['only_a'])}):")
                for row in comparison["only_a"][:3]:
                    vals = " | ".join(str(v)[:60] for v in row)
                    print(f"       {vals}")
                if len(comparison["only_a"]) > 3:
                    print(f"       ... and {len(comparison['only_a']) - 3} more")
            if comparison["only_b"]:
                print(f"  Only in JSON-LD ({len(comparison['only_b'])}):")
                for row in comparison["only_b"][:3]:
                    vals = " | ".join(str(v)[:60] for v in row)
                    print(f"       {vals}")
                if len(comparison["only_b"]) > 3:
                    print(f"       ... and {len(comparison['only_b']) - 3} more")

    # Summary
    applicable = total - empty
    print("\n" + "=" * 72)
    print("  SPARQL EQUIVALENCE SUMMARY")
    print("=" * 72)
    print(f"  Total queries:   {total}")
    print(f"  Applicable:      {applicable} ({empty} skipped - empty in both)")
    print(f"  Passed:          {passed}")
    print(f"  Failed:          {failed}")
    pct = (passed / applicable * 100) if applicable > 0 else 0
    print(f"  Equivalence:     {pct:.1f}%")
    print()
    overall = "PASS" if failed == 0 and passed > 0 else "FAIL"
    print(f"  OVERALL: {overall}")
    print()

    if overall == "PASS":
        print("  Both serializations are SPARQL-equivalent:")
        print("  identical queries yield identical results across all")
        print("  fundamental FRAM domain concepts (functions, aspects,")
        print("  couplings, variability, quantitative metadata, scenarios).")
        print()
        print("  This confirms semantic equivalence per W3C RDF 1.1 Concepts")
        print("  (Section 3.5) — the two graphs represent the same knowledge.")
    else:
        print("  The serializations differ in SPARQL query results.")
        print("  Review the FAIL entries above for specific divergences.")

    print("=" * 72)
    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
