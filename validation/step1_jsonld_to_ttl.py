"""
Step 1: JSON-LD to Turtle Conversion
=====================================
Converts the boil-water-model.jsonld to Turtle (TTL) using rdflib,
resolving the remote @context with the local context.jsonld file.

Part of the FRAM Ontology Validation Benchmark (EP2).
"""

import json
import os
from rdflib import Graph, Namespace
from pyld import jsonld

# Resolve paths relative to repository root
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
EXAMPLES_DIR = os.path.join(REPO_ROOT, "examples")
VALIDATION_DIR = os.path.dirname(__file__)

# ── 1. Load the JSON-LD model and replace the remote @context with the local one ──
jsonld_path = os.path.join(EXAMPLES_DIR, "boil-water-model.jsonld")
context_path = os.path.join(REPO_ROOT, "context.jsonld")

with open(jsonld_path, "r") as f:
    model_data = json.load(f)

with open(context_path, "r") as f:
    local_context = json.load(f)

# Replace the remote URL with the local context
model_data["@context"] = local_context["@context"]

# ── 2. Expand the JSON-LD (resolves all terms to full IRIs) ──
expanded = jsonld.expand(model_data)
print(f"[OK] JSON-LD expanded: {len(expanded)} root node(s)")

# ── 3. Convert to N-Quads (intermediate format that rdflib understands) ──
nquads = jsonld.to_rdf(model_data, {"format": "application/n-quads"})
print(f"[OK] N-Quads generated: {len(nquads.splitlines())} triples")

# ── 4. Load into rdflib and serialize as Turtle ──
g = Graph()
g.parse(data=nquads, format="nquads")

# Add prefixes for readability
FRAM = Namespace("https://flowfram.com/ontology/fram/")
SCHEMA = Namespace("https://schema.org/")
g.bind("fram", FRAM)
g.bind("schema", SCHEMA)

# Serialize as Turtle
ttl_output = g.serialize(format="turtle")
output_path = os.path.join(VALIDATION_DIR, "boil-water-model.ttl")
with open(output_path, "w") as f:
    f.write(ttl_output)

print(f"[OK] TTL file generated: boil-water-model.ttl")
print(f"[OK] Total ABox triples in graph: {len(g)}")

# ── 5. Show the first lines of the TTL output ──
print("\n--- First 40 lines of generated TTL ---")
for i, line in enumerate(ttl_output.splitlines()[:40]):
    print(line)
