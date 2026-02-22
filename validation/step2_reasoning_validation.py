"""
Step 2: Logical Validation with OWL-RL Reasoner
================================================
Loads the TBox (fram.ttl) and ABox (boil-water-model.ttl),
runs the OWL-RL reasoner and verifies:
  1. Logical consistency (no contradictions)
  2. Unsatisfiable classes (no class empty by contradiction)
  3. Inferred triples from reasoning

Part of the FRAM Ontology Validation Benchmark (EP2).
"""

import os
import sys
import time
from rdflib import Graph, Namespace, RDF, OWL, RDFS
import owlrl

FRAM = Namespace("https://flowfram.com/ontology/fram/")

# Resolve paths relative to repository root
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
VALIDATION_DIR = os.path.dirname(__file__)

# ── 1. Load TBox + ABox ──
print("=" * 60)
print("STEP 2: LOGICAL VALIDATION WITH OWL-RL REASONER")
print("=" * 60)

g = Graph()

tbox_path = os.path.join(REPO_ROOT, "fram.ttl")
abox_path = os.path.join(VALIDATION_DIR, "boil-water-model.ttl")

print(f"\n[1/4] Loading TBox (fram.ttl)...")
g.parse(tbox_path, format="turtle")
tbox_count = len(g)
print(f"      Triples loaded (TBox): {tbox_count}")

print(f"[2/4] Loading ABox (boil-water-model.ttl)...")
g.parse(abox_path, format="turtle")
abox_count = len(g) - tbox_count
total_before = len(g)
print(f"      Triples loaded (ABox): {abox_count}")
print(f"      Total before reasoning: {total_before}")

# ── 2. Run the OWL-RL Reasoner ──
print("\n[3/4] Running OWL-RL reasoner...")
start_time = time.time()

try:
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    elapsed = time.time() - start_time
    total_after = len(g)
    inferred = total_after - total_before
    print(f"      [OK] Reasoning completed in {elapsed:.2f}s")
    print(f"      Triples after reasoning: {total_after}")
    print(f"      Inferred triples: {inferred}")
    reasoning_success = True
except Exception as e:
    elapsed = time.time() - start_time
    print(f"      [ERROR] Reasoning failed after {elapsed:.2f}s: {e}")
    reasoning_success = False

# ── 3. Check Consistency ──
print("\n[4/4] Checking consistency and unsatisfiable classes...")

# Check if owl:Nothing has instances (would indicate inconsistency)
nothing_instances = list(g.subjects(RDF.type, OWL.Nothing))
if nothing_instances:
    print(f"      [FAIL] Inconsistency detected! {len(nothing_instances)} instance(s) of owl:Nothing:")
    for inst in nothing_instances:
        print(f"        - {inst}")
    consistency_ok = False
else:
    print("      [OK] No instances of owl:Nothing — ontology is consistent")
    consistency_ok = True

# Check for classes that are subclasses of owl:Nothing (unsatisfiable)
unsatisfiable = []
for cls in g.subjects(RDF.type, OWL.Class):
    if (cls, RDFS.subClassOf, OWL.Nothing) in g and cls != OWL.Nothing:
        unsatisfiable.append(cls)

if unsatisfiable:
    print(f"      [FAIL] {len(unsatisfiable)} unsatisfiable class(es):")
    for cls in unsatisfiable:
        print(f"        - {cls}")
    satisfiability_ok = False
else:
    print("      [OK] No unsatisfiable classes detected")
    satisfiability_ok = True

# ── 4. List some relevant inferences ──
print("\n--- Examples of Inferred Facts ---")

# Check if functions were inferred as correct subclasses
inference_examples = []
for s, p, o in g.triples((None, RDF.type, FRAM.Function)):
    # Check if also inferred as specific subclass
    types = list(g.objects(s, RDF.type))
    type_names = [str(t).split("/")[-1] for t in types if "fram" in str(t)]
    if len(type_names) > 1:
        inference_examples.append((s, type_names))

for subj, types in inference_examples[:5]:
    label = list(g.objects(subj, Namespace("https://schema.org/").name))
    name = str(label[0]) if label else str(subj)
    print(f"  {name}: {', '.join(types)}")

# ── 5. Summary ──
print("\n" + "=" * 60)
print("STEP 2 SUMMARY")
print("=" * 60)
print(f"  TBox triples:           {tbox_count}")
print(f"  ABox triples:           {abox_count}")
print(f"  Total before reasoning: {total_before}")
print(f"  Total after reasoning:  {total_after if reasoning_success else 'N/A'}")
print(f"  Inferred triples:       {inferred if reasoning_success else 'N/A'}")
print(f"  Reasoning time:         {elapsed:.2f}s")
print(f"  Consistency:            {'PASS ✅' if consistency_ok else 'FAIL ❌'}")
print(f"  Unsatisfiable classes:  {'PASS ✅ (0)' if satisfiability_ok else f'FAIL ❌ ({len(unsatisfiable)})'}")
print(f"  Overall Result:         {'PASS ✅' if (reasoning_success and consistency_ok and satisfiability_ok) else 'FAIL ❌'}")
