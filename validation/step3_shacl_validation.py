"""
Step 3: SHACL Shape Validation
==============================
Validates the ABox (boil-water-model.ttl) against the SHACL shapes defined
in fram-shapes.ttl, using the TBox (fram.ttl) as supporting ontology.

Part of the FRAM Ontology Validation Benchmark (EP2).
"""

import os
import time
from rdflib import Graph, Namespace
from pyshacl import validate

FRAM = Namespace("https://flowfram.com/ontology/fram/")

# Resolve paths relative to repository root
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
VALIDATION_DIR = os.path.dirname(__file__)

print("=" * 60)
print("STEP 3: SHACL SHAPE VALIDATION")
print("=" * 60)

# ── 1. Load the graphs ──
print("\n[1/3] Loading graphs...")

tbox_path = os.path.join(REPO_ROOT, "fram.ttl")
abox_path = os.path.join(VALIDATION_DIR, "boil-water-model.ttl")
shapes_path = os.path.join(REPO_ROOT, "fram-shapes.ttl")

# Data graph = TBox + ABox (so SHACL can resolve classes)
data_graph = Graph()
data_graph.parse(tbox_path, format="turtle")
tbox_count = len(data_graph)
data_graph.parse(abox_path, format="turtle")
total_data = len(data_graph)
print(f"      Data graph: {total_data} triples (TBox: {tbox_count}, ABox: {total_data - tbox_count})")

# Shapes graph
shapes_graph = Graph()
shapes_graph.parse(shapes_path, format="turtle")
print(f"      Shapes graph: {len(shapes_graph)} triples")

# ── 2. Run SHACL validation ──
print("\n[2/3] Running SHACL validation...")
start_time = time.time()

conforms, results_graph, results_text = validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference="none",  # No additional inference; already done in Step 2
    abort_on_first=False,
    meta_shacl=False,
    advanced=True,
    debug=False
)

elapsed = time.time() - start_time
print(f"      Validation completed in {elapsed:.2f}s")

# ── 3. Analyze results ──
print(f"\n[3/3] SHACL Validation Results:")
print(f"      Conforms: {conforms}")

if conforms:
    print("      [OK] All data conforms to the SHACL shapes ✅")
else:
    print("      [WARNING] Violations found:")
    print(results_text)

# ── 4. Detail the validated shapes ──
print("\n--- Validated Shapes ---")
shapes_info = [
    ("S1: FRAMModelShape", "FRAMModel must have name and at least 1 function"),
    ("S2: FunctionShape", "Function must have name, functionType, and at least 1 aspect"),
    ("S3: CouplingShape", "Coupling must have sourceFunction, targetFunction, sourceAspect, targetAspect"),
    ("S4: AspectShape", "Aspect must have valid aspectType and aspectCode"),
    ("S5: NormalDistributionShape", "NormalDistribution must have mean and stdDev > 0"),
    ("S6: PhenotypeShape", "Phenotype must have phenotypeProbability between 0 and 1"),
]

for shape_id, desc in shapes_info:
    print(f"  {shape_id}: {desc}")

# ── 5. Summary ──
print("\n" + "=" * 60)
print("STEP 3 SUMMARY")
print("=" * 60)
print(f"  Shapes defined:         6")
print(f"  Data triples:           {total_data}")
print(f"  Validation time:        {elapsed:.2f}s")
print(f"  Conforms:               {conforms}")
print(f"  Overall Result:         {'PASS ✅' if conforms else 'FAIL ❌'}")

if not conforms:
    # Save violations report
    violations_path = os.path.join(VALIDATION_DIR, "shacl_violations.txt")
    with open(violations_path, "w") as f:
        f.write(results_text)
    print(f"  Violations report saved to: shacl_violations.txt")
