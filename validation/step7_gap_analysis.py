"""
Detailed gap analysis between TTL and JSON-LD exports.
Groups differences by predicate to identify real content gaps
(ignoring BNode ID artifacts).
"""
import sys, os, json
from rdflib import Graph, URIRef, BNode, Literal
from collections import Counter

TTL_PATH = sys.argv[1]
JSONLD_PATH = sys.argv[2]
CONTEXT_PATH = sys.argv[3]

def shorten(uri):
    return (str(uri)
        .replace("https://flowfram.com/models/", "model:")
        .replace("https://flowfram.com/ontology/fram/", "fram:")
        .replace("https://schema.org/", "schema:")
        .replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
        .replace("http://www.w3.org/2000/01/rdf-schema#", "rdfs:")
        .replace("http://www.w3.org/2002/07/owl#", "owl:")
        .replace("http://www.w3.org/2001/XMLSchema#", "xsd:"))

# Parse both
g_ttl = Graph()
g_ttl.parse(TTL_PATH, format="turtle")

from pyld import jsonld as jsonld_lib
with open(JSONLD_PATH) as f:
    jdata = json.load(f)
with open(CONTEXT_PATH) as f:
    ctx = json.load(f)
jdata["@context"] = ctx["@context"]
nquads = jsonld_lib.to_rdf(jdata, {"format": "application/n-quads"})
g_jsonld = Graph()
g_jsonld.parse(data=nquads, format="nquads")

print(f"TTL: {len(g_ttl)} triples  |  JSON-LD: {len(g_jsonld)} triples")
print(f"Difference: {len(g_jsonld) - len(g_ttl)} triples")

# Collect ALL predicates used, grouped by subject type pattern
def classify_subject(g, s):
    """Classify a subject by its rdf:type or IRI pattern."""
    if isinstance(s, BNode):
        return "[BNode]"
    s_str = str(s)
    if "coupling_" in s_str:
        return "Coupling"
    if "aspect_" in s_str:
        return "Aspect"
    if "function_" in s_str or "func_" in s_str:
        return "Function"
    if "model_" in s_str or "li-huang" in s_str.lower():
        return "Model"
    return "Other"

# Predicate analysis: count triples per predicate in each graph
def predicate_counts(g):
    counts = Counter()
    for s, p, o in g:
        counts[str(p)] += 1
    return counts

ttl_preds = predicate_counts(g_ttl)
jsonld_preds = predicate_counts(g_jsonld)

all_preds = sorted(set(ttl_preds.keys()) | set(jsonld_preds.keys()))

print(f"\n{'='*80}")
print(f"  PREDICATE COMPARISON (TTL vs JSON-LD)")
print(f"{'='*80}")
print(f"  {'Predicate':<55} {'TTL':>5} {'JSONLD':>6} {'Diff':>6}")
print(f"  {'-'*55} {'-'*5} {'-'*6} {'-'*6}")

for p in all_preds:
    t = ttl_preds.get(p, 0)
    j = jsonld_preds.get(p, 0)
    diff = j - t
    p_short = shorten(p)
    if diff != 0:
        marker = " <<<" if abs(diff) > 0 else ""
        print(f"  {p_short:<55} {t:>5} {j:>6} {diff:>+6}{marker}")

print(f"\n{'='*80}")
print(f"  PREDICATES ONLY IN JSON-LD (missing from TTL)")
print(f"{'='*80}")
for p in all_preds:
    t = ttl_preds.get(p, 0)
    j = jsonld_preds.get(p, 0)
    if t == 0 and j > 0:
        p_short = shorten(p)
        print(f"  {p_short:<55} count={j}")
        # Show a few examples
        examples = []
        for s, pred, o in g_jsonld:
            if str(pred) == p and len(examples) < 3:
                s_short = shorten(str(s)) if isinstance(s, URIRef) else "[bnode]"
                o_short = shorten(str(o)) if isinstance(o, URIRef) else f'"{str(o)[:60]}"'
                examples.append(f"    {s_short} -> {o_short}")
        for ex in examples:
            print(ex)
        print()

print(f"\n{'='*80}")
print(f"  PREDICATES ONLY IN TTL (missing from JSON-LD)")
print(f"{'='*80}")
for p in all_preds:
    t = ttl_preds.get(p, 0)
    j = jsonld_preds.get(p, 0)
    if j == 0 and t > 0:
        p_short = shorten(p)
        print(f"  {p_short:<55} count={t}")
        examples = []
        for s, pred, o in g_ttl:
            if str(pred) == p and len(examples) < 3:
                s_short = shorten(str(s)) if isinstance(s, URIRef) else "[bnode]"
                o_short = shorten(str(o)) if isinstance(o, URIRef) else f'"{str(o)[:60]}"'
                examples.append(f"    {s_short} -> {o_short}")
        for ex in examples:
            print(ex)
        print()

# Count predicates with same count in both
same = sum(1 for p in all_preds if ttl_preds.get(p, 0) == jsonld_preds.get(p, 0))
diff = len(all_preds) - same
print(f"\nPredicates matching: {same}/{len(all_preds)} ({same/len(all_preds)*100:.1f}%)")
print(f"Predicates with differences: {diff}")
