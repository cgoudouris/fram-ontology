"""
Round-trip fidelity test for FRAM ontology exports.

Tests:
  RT1: TTL  -> parse -> serialize as JSON-LD -> parse back -> compare with original TTL graph
  RT2: JSON-LD -> parse -> serialize as TTL   -> parse back -> compare with original JSON-LD graph
  RT3: Direct comparison - parse both exports independently -> compare graphs

Uses rdflib graph isomorphism (BNode-aware).
"""
import sys, os, json, time
from rdflib import Graph, compare, URIRef, BNode

TTL_PATH   = sys.argv[1]
JSONLD_PATH = sys.argv[2]
CONTEXT_PATH = sys.argv[3] if len(sys.argv) > 3 else None

def banner(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def load_jsonld_with_context(path, context_path):
    from pyld import jsonld as jsonld_lib
    with open(path) as f:
        jdata = json.load(f)
    if context_path:
        with open(context_path) as f:
            ctx = json.load(f)
        jdata["@context"] = ctx["@context"]
    nquads = jsonld_lib.to_rdf(jdata, {"format": "application/n-quads"})
    g = Graph()
    g.parse(data=nquads, format="nquads")
    return g

def named_triples(g):
    result = set()
    for s, p, o in g:
        if isinstance(s, URIRef):
            o_str = str(o) if isinstance(o, URIRef) else f'"{o}"'
            result.add((str(s), str(p), o_str))
    return result

def bnode_triples(g):
    count = 0
    for s, p, o in g:
        if isinstance(s, BNode) or isinstance(o, BNode):
            count += 1
    return count

def shorten(uri):
    return (uri
        .replace("https://flowfram.com/models/", "model:")
        .replace("https://flowfram.com/ontology/fram/", "fram:")
        .replace("https://schema.org/", "schema:")
        .replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
        .replace("http://www.w3.org/2000/01/rdf-schema#", "rdfs:")
        .replace("http://www.w3.org/2002/07/owl#", "owl:"))

def triple_diff(g1, g2, label1="G1", label2="G2", max_show=15):
    n1 = named_triples(g1)
    n2 = named_triples(g2)
    
    only1 = n1 - n2
    only2 = n2 - n1
    shared = n1 & n2
    bn1 = bnode_triples(g1)
    bn2 = bnode_triples(g2)
    
    print(f"\n  Named triples:  {label1}={len(n1)}, {label2}={len(n2)}, shared={len(shared)}")
    print(f"  BNode triples:  {label1}={bn1}, {label2}={bn2}")
    
    if only1:
        print(f"\n  Only in {label1} ({len(only1)}):")
        for s, p, o in sorted(only1)[:max_show]:
            print(f"    {shorten(s)}  {shorten(p)}  {shorten(o)}")
        if len(only1) > max_show:
            print(f"    ... and {len(only1) - max_show} more")
    
    if only2:
        print(f"\n  Only in {label2} ({len(only2)}):")
        for s, p, o in sorted(only2)[:max_show]:
            print(f"    {shorten(s)}  {shorten(p)}  {shorten(o)}")
        if len(only2) > max_show:
            print(f"    ... and {len(only2) - max_show} more")
    
    if not only1 and not only2:
        print(f"\n  [OK] All named triples match perfectly!")
    
    return len(only1), len(only2), len(shared)


# ========================================================================
# RT1: TTL -> JSON-LD -> back
# ========================================================================
banner("RT1: TTL -> serialize as JSON-LD -> parse back")
print(f"  Source: {os.path.basename(TTL_PATH)}")

t0 = time.time()
g_ttl_orig = Graph()
g_ttl_orig.parse(TTL_PATH, format="turtle")
print(f"  [1/3] Parsed TTL: {len(g_ttl_orig)} triples")

jsonld_bytes = g_ttl_orig.serialize(format="json-ld")
print(f"  [2/3] Serialized as JSON-LD: {len(jsonld_bytes)} bytes")

g_ttl_rt = Graph()
g_ttl_rt.parse(data=jsonld_bytes, format="json-ld")
print(f"  [3/3] Parsed back: {len(g_ttl_rt)} triples")

iso_rt1 = compare.isomorphic(g_ttl_orig, g_ttl_rt)
elapsed = time.time() - t0
print(f"\n  Isomorphic: {'YES' if iso_rt1 else 'NO'} ({elapsed:.2f}s)")

if not iso_rt1:
    triple_diff(g_ttl_orig, g_ttl_rt, "TTL-orig", "TTL-roundtrip")

# ========================================================================
# RT2: JSON-LD -> TTL -> back
# ========================================================================
banner("RT2: JSON-LD -> serialize as TTL -> parse back")
print(f"  Source: {os.path.basename(JSONLD_PATH)}")

t0 = time.time()
g_jsonld_orig = load_jsonld_with_context(JSONLD_PATH, CONTEXT_PATH)
print(f"  [1/3] Parsed JSON-LD (via pyld): {len(g_jsonld_orig)} triples")

ttl_bytes = g_jsonld_orig.serialize(format="turtle")
print(f"  [2/3] Serialized as Turtle: {len(ttl_bytes)} bytes")

g_jsonld_rt = Graph()
g_jsonld_rt.parse(data=ttl_bytes, format="turtle")
print(f"  [3/3] Parsed back: {len(g_jsonld_rt)} triples")

iso_rt2 = compare.isomorphic(g_jsonld_orig, g_jsonld_rt)
elapsed = time.time() - t0
print(f"\n  Isomorphic: {'YES' if iso_rt2 else 'NO'} ({elapsed:.2f}s)")

if not iso_rt2:
    triple_diff(g_jsonld_orig, g_jsonld_rt, "JSONLD-orig", "JSONLD-roundtrip")

# ========================================================================
# RT3: Direct cross-format comparison
# ========================================================================
banner("RT3: Direct cross-format graph comparison")
print(f"  TTL:     {os.path.basename(TTL_PATH)} ({len(g_ttl_orig)} triples)")
print(f"  JSON-LD: {os.path.basename(JSONLD_PATH)} ({len(g_jsonld_orig)} triples)")

t0 = time.time()
iso_rt3 = compare.isomorphic(g_ttl_orig, g_jsonld_orig)
elapsed = time.time() - t0
print(f"\n  Isomorphic: {'YES' if iso_rt3 else 'NO'} ({elapsed:.2f}s)")

only_ttl, only_jsonld, shared = triple_diff(g_ttl_orig, g_jsonld_orig, "TTL", "JSON-LD")

coverage = (shared / (shared + only_ttl) * 100) if (shared + only_ttl) > 0 else 0
print(f"\n  TTL coverage in JSON-LD: {coverage:.1f}%")

# ========================================================================
# Summary
# ========================================================================
banner("ROUND-TRIP SUMMARY")
tests = [
    ("RT1: TTL -> JSON-LD -> TTL",      iso_rt1),
    ("RT2: JSON-LD -> TTL -> JSON-LD",   iso_rt2),
    ("RT3: TTL == JSON-LD (direct)",    iso_rt3),
]
for name, passed in tests:
    print(f"  {name:40s} {'PASS' if passed else 'FAIL'}")

all_pass = all(p for _, p in tests)
print(f"\n  OVERALL: {'PASS' if all_pass else 'FAIL'}")

if not iso_rt3:
    if only_ttl == 0 and only_jsonld > 0:
        print(f"\n  Note: TTL is a proper subset of JSON-LD ({only_jsonld} extra named triples in JSON-LD).")
        print(f"  This means the TTL exporter is missing some data that JSON-LD includes.")
    elif only_ttl > 0 and only_jsonld > 0:
        print(f"\n  Note: {only_ttl} named triples only in TTL, {only_jsonld} only in JSON-LD.")
        print(f"  The exporters produce different RDF graphs for the same model.")
    elif only_ttl > 0 and only_jsonld == 0:
        print(f"\n  Note: JSON-LD is a proper subset of TTL ({only_ttl} extra named triples in TTL).")

sys.exit(0 if all_pass else 1)
