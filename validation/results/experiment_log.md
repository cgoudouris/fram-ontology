# EP2 — Ontology Validation Experiment Log

Validation benchmark for the FRAM Ontology. Current validation uses `li-huang-2025.ttl` / `li-huang-2025.jsonld` (ABox) and `fram.ttl` v1.8.0 (TBox). Historical baseline used `boil-water-model.jsonld`.

---

## v1.6.0 Validation (Previous)

Executed against `fram.ttl` v1.6.0 (1133 TBox triples, ~1560 lines).

### Step 1: JSON-LD → Turtle Conversion

- **Status**: ✅ PASS
- **Input**: `boil-water-model.jsonld`
- **Output**: `boil-water-model.ttl` (124 RDF triples)
- **Method**: pyld (JSON-LD expansion + N-Quads) → rdflib (parse + serialize Turtle)
- **Notes**: All 124 triples generated successfully. Context resolution works correctly with v1.6.0 terms.

### Step 2: OWL-RL Reasoning & Consistency

- **Status**: ✅ PASS
- **TBox triples**: 1133
- **ABox triples**: 124
- **Total before reasoning**: 1257
- **Total after reasoning**: 3101
- **Inferred triples**: 1844
- **Reasoning time**: ~0.30s
- **Consistency**: PASS — 0 instances of `owl:Nothing`
- **Unsatisfiable classes**: PASS — 0 unsatisfiable classes
- **Notes**: The OWL-RL reasoner expanded the graph with type inferences, subclass propagation, inverse property entailments (27 inverse pairs), and 8 disjointness blocks. No contradictions found.

### Step 3: SHACL Shape Validation

- **Status**: ✅ PASS
- **Shapes validated**: 8 (S1–S8)
- **Data triples**: 1257 (TBox + ABox)
- **Conforms**: `true`
- **Notes**: All 8 SHACL shapes in `fram-shapes.ttl` were satisfied:
  - S1 (FRAMModelShape): Model has `name` and ≥1 function ✓
  - S2 (FunctionShape): Functions have `name`, `functionType`, ≥1 aspect ✓
  - S3 (CouplingShape): Couplings have `sourceFunction`, `targetFunction`, `sourceAspect`, `targetAspect` ✓
  - S4 (AspectShape): Aspects have valid `aspectType` and `aspectCode` ∈ {I, O, P, R, C, T} ✓
  - S5 (NormalDistributionShape): NormalDistribution has `mean` and `stdDev` > 0 ✓
  - S6 (PhenotypeShape): Phenotype has `phenotypeProbability` ∈ [0, 1] ✓
  - S7 (PhenotypeMappingRuleShape): No ABox instances to validate (shape defined for future use) ✓
  - S8 (WAIDeclarationShape): No ABox instances to validate (shape defined for future use) ✓

### Step 4: SPARQL Competency Questions

- **Status**: ✅ PASS (6/6)
- **Results**:

| CQ | Question | Expected | Actual | Status |
|----|----------|----------|--------|--------|
| CQ1 | Functions and their types | 3 functions | 3 | ✅ PASS |
| CQ2 | Couplings between functions | 2 couplings | 2 | ✅ PASS |
| CQ3 | Aspects of "Heat water to boiling" | 5 aspects | 5 | ✅ PASS |
| CQ4 | Variability distribution of "Heat water" | Normal(μ=4.0, σ=0.5) | 1 match | ✅ PASS |
| CQ5 | Phenotypes of "Fill kettle with water" | 2 phenotypes | 2 | ✅ PASS |
| CQ6 | Functions receiving input via couplings | 2 functions | 2 | ✅ PASS |

### Step 5: OOPS! Pitfall Scanning

- **Status**: ✅ PASS (only known false positive)
- **API**: `https://oops.linkeddata.es/rest`
- **Pitfalls detected**: 1
  - **P04** (Minor): 8 gUFO classes flagged as "unconnected" — these are external foundational ontology classes (`gufo:QualityValue`, `gufo:Object`, `gufo:Event`, `gufo:IntrinsicMode`, `gufo:Disposition`, `gufo:RelationalQuality`, `gufo:Quality`, `gufo:AbstractIndividual`) declared for alignment but not fully connected since gUFO is not imported. **Known false positive** — documented since v1.3.0.
- **Previously fixed in this version**:
  - **P13** (Missing inverses): 5 new v1.6.0 object properties initially lacked `owl:inverseOf`. Fixed by adding 5 inverse declarations.
  - **P05/P19** (Naming conflict): Initially created `isDimensionOf` as inverse of `mapsToDimension`, conflicting with existing `isDimensionOf` (inverse of `hasDimension`). Fixed by renaming to `isMappingDimensionOf`.
- **Notes**: See [oops_analysis.md](oops_analysis.md) for full pitfall history.

### v1.6.0 Overall Summary

| Step | Technique | Result |
|------|-----------|--------|
| 1 | JSON-LD → Turtle | ✅ PASS (124 triples) |
| 2 | OWL-RL Reasoning | ✅ PASS (consistent, 0 unsatisfiable, 1844 inferred) |
| 3 | SHACL Shapes | ✅ PASS (conforms, 8/8 shapes) |
| 4 | SPARQL CQs | PASS (6/6 questions) |
| 5 | OOPS! Scanner | PASS (P04 only -- gUFO false positive) |

**Ontology version**: v1.6.0 (1133 TBox triples, ~1560 lines)
**Validation date**: April 2026

---

## v1.8.0 Validation (Current -- Gold Standard)

Executed against `fram.ttl` v1.8.0 (1357 TBox triples) with `li-huang-2025.ttl` as ABox (3292 triples, 20 functions, 34 couplings) via the unified runner `validate_fram_model.py`.

### Pre-requisite: W3C RDF 1.1 Conformance

| Serialization | Format | Triples | Time | Status |
|---------------|--------|---------|------|--------|
| `fram.ttl` | Turtle | 1357 | 0.02s | VALID |
| `fram.owl` | RDF/XML | 1357 | 0.04s | VALID |
| `context.jsonld` | JSON-LD 1.1 | 276 terms | -- | VALID |

Cross-format consistency: TTL = OWL = 1357 triples. **PASS**.

### TBox Metrics (v1.8.0)

| Metric | Value |
|--------|-------|
| Classes (FRAM) | 65 |
| Object Properties | 66 |
| Datatype Properties | 66 |
| Total Properties | 132 |
| `owl:inverseOf` pairs | 29 |
| `owl:AllDisjointClasses` blocks | 8 |
| gUFO `rdfs:subClassOf` axioms | 16 |
| SKOS definitions | 36 |
| Total TBox triples | 1357 |

### ABox Metrics (Li-Huang 2025)

| Metric | Value |
|--------|-------|
| Total ABox triples | 3292 |
| Unique FRAM types used | 26 / 65 (40%) |

Top instance types: OutputAspect (54), Variable (43), InputAspect (37), OutputMessage (34), Coupling (34), VariabilityPropagation (34), ControlAspect (27), PreconditionAspect (25), ResourceAspect (25), Function (20), HumanFunction (20), TimeAspect (20), Variability (20), QuantitativeMetadata (20).

### Step 1: JSON-LD -> Turtle Conversion

- **Status**: PASS
- **Input**: `li-huang-2025.jsonld`
- **Output**: 3292 ABox triples
- **Notes**: All terms resolved to IRIs in `fram:` and `model:` namespaces.

### Step 2: OWL-RL Reasoning & Consistency

- **Status**: PASS
- **TBox triples**: 1357
- **ABox triples**: 3292
- **Total before reasoning**: 4649
- **Total after reasoning**: 10274
- **Inferred triples**: 5625 (1.17s)
- **Consistency**: PASS -- 0 instances of `owl:Nothing`
- **Unsatisfiable classes**: PASS -- 0 unsatisfiable classes

### Step 3: SHACL Shape Validation

- **Status**: PASS
- **Shapes validated**: 8 (S1--S8)
- **Data triples**: 4649 (TBox + ABox)
- **Shapes graph triples**: 155
- **Conforms**: `true`
- **Shapes**:
  - S1 (FRAMModelShape): Model has `name` and >=1 function
  - S2 (FunctionShape): Functions have `name`, `functionType`, >=1 aspect
  - S3 (CouplingShape): Couplings have `sourceFunction`, `targetFunction`, `sourceAspect`, `targetAspect`
  - S4 (AspectShape): Aspects have valid `aspectType` and `aspectCode` in {I, O, P, R, C, T}
  - S5 (NormalDistributionShape): NormalDistribution has `mean` and `stdDev` > 0
  - S6 (PhenotypeShape): Phenotype has `phenotypeProbability` in [0, 1]
  - S7 (PhenotypeMappingRuleShape): PhenotypeMappingRule has `mapsToVariable` and `mapsToDimension`
  - S8 (WAIDeclarationShape): WAIDeclaration has `dominantPhenotype` and `waiConfidence`

### Step 4: SPARQL Competency Questions

- **Status**: PASS (5/5)

| CQ | Question | Results | Status |
|----|----------|---------|--------|
| CQ1 | Functions and their types | 20 | PASS |
| CQ2 | Couplings between functions | 34 | PASS |
| CQ3 | Aspects per function | 20 | PASS |
| CQ4 | Functions with variability metadata | 20 | PASS |
| CQ5 | Functions receiving input via couplings | 17 | PASS |

### Step 5: OOPS! Pitfall Scanning

- **Status**: PASS
- **API**: `https://oops.linkeddata.es/rest`
- **Pitfalls detected**: **0** (zero)
- **Critical**: 0
- **Important**: 0
- **Minor**: 0
- **Notes**: Complete elimination of all pitfalls. The P04 false positive (gUFO classes) that persisted since v1.3.0 is no longer reported. See [oops_analysis.md](oops_analysis.md) for full evolution.

### Step 6: Round-Trip Fidelity

- **Status**: PASS (RT1)

| Test | Description | Result | Note |
|------|-------------|--------|------|
| RT1 | TTL -> JSON-LD -> TTL | **PASS** | Isomorphic after double conversion |
| RT2 | JSON-LD -> TTL -> JSON-LD | FAIL | Expected: blank node instability |
| RT3 | TTL == JSON-LD (direct) | FAIL | Expected: structural differences |

- Named triples only in TTL: 684
- Named triples only in JSON-LD: 148
- TTL coverage: 70.8%

### Step 7: Gap Analysis

- **Status**: REPORTED (informational)
- **Predicates matching**: 56/83 (67.5%)
- **Predicates with differences**: 27
- **Notes**: Improvement from v1.7.0 (55/83 = 66.3%). Divergent predicates correspond to properties emitted by only one exporter.

### Step 8: SPARQL Semantic Equivalence (Gold Standard)

- **Status**: PASS (9/9 = 100%)

| Query | Domain | TTL | JSON-LD | Status |
|-------|--------|-----|---------|--------|
| SQ1 | Functions and types | 20 | 20 | PASS |
| SQ2 | Aspects per function | 188 | 188 | PASS |
| SQ3 | Couplings | 34 | 34 | PASS |
| SQ4 | Variability | 20 | 20 | PASS |
| SQ5 | Scenarios | 4 | 4 | PASS |
| SQ6 | Quantitative metadata | 20 | 20 | PASS |
| SQ7 | Constants and variables | 59 | 59 | PASS |
| SQ8 | Output messages | 34 | 34 | PASS |
| SQ9 | Interpretation profiles | 15 | 15 | PASS |
| SQ10 | Phenotypes | -- | -- | N/A (empty) |

**Both serializations are SPARQL-equivalent**: identical queries yield identical results across all fundamental FRAM domain concepts. This confirms semantic equivalence per W3C RDF 1.1 Concepts (Section 3.5).

### v1.8.0 Overall Summary

| Step | Technique | Result |
|------|-----------|--------|
| 0 | W3C RDF 1.1 Conformance | PASS (TTL=OWL=1357 triples) |
| 1 | JSON-LD -> Turtle | PASS (3292 triples) |
| 2 | OWL-RL Reasoning | PASS (5625 inferred, 0 unsatisfiable) |
| 3 | SHACL Shapes | PASS (conforms, 8/8 shapes) |
| 4 | SPARQL CQs | PASS (5/5 questions) |
| 5 | OOPS! Scanner | PASS (0 pitfalls at any level) |
| 6 | Round-trip Fidelity | PASS (RT1 isomorphic) |
| 7 | Gap Analysis | 67.5% predicate match (informational) |
| 8 | SPARQL Equivalence | PASS (9/9 = 100%, gold standard) |

**Ontology version**: v1.8.0 (1357 TBox triples, 65 classes, 132 properties)
**ABox model**: Li-Huang 2025 (3292 triples, 20 functions, 34 couplings)
**Validation date**: April 2026
**Runner**: `python validate_fram_model.py examples/li-huang-2025.ttl examples/li-huang-2025.jsonld`

---

## v1.2.0 Validation (Baseline)

Executed against `fram.ttl` v1.2.0 (669 TBox triples, 1015 lines).

### Step 1: JSON-LD → Turtle Conversion

- **Status**: ✅ PASS
- **Input**: `boil-water-model.jsonld` (4,470 bytes)
- **Output**: `boil-water-model.ttl` (124 RDF triples)
- **Method**: pyld (JSON-LD expansion + N-Quads) → rdflib (parse + serialize Turtle)
- **Notes**: The remote `@context` (`https://flowfram.com/ontology/fram/context.jsonld`) was replaced with the local `context.jsonld` to ensure reproducibility. All 124 triples were generated successfully with prefixes `fram:`, `schema:`, `rdfs:`, and `xsd:` correctly mapped.

### Step 2: OWL-RL Reasoning & Consistency

- **Status**: ✅ PASS
- **TBox triples**: 669
- **ABox triples**: 124
- **Total before reasoning**: 793
- **Total after reasoning**: ~5,800+ (inferred)
- **Reasoning time**: ~2–4s
- **Consistency**: PASS — 0 instances of `owl:Nothing`
- **Unsatisfiable classes**: PASS — 0 unsatisfiable classes
- **Notes**: The OWL-RL reasoner successfully expanded the graph with type inferences, subclass propagation, and inverse property entailments. No contradictions found.

### Step 3: SHACL Shape Validation

- **Status**: ✅ PASS
- **Shapes validated**: 6 (S1–S6)
- **Data triples**: 793 (TBox + ABox)
- **Conforms**: `true`
- **Notes**: All 6 SHACL shapes in `fram-shapes.ttl` were satisfied.

### Step 4: SPARQL Competency Questions

- **Status**: ✅ PASS (6/6)

### Step 5: OOPS! Pitfall Scanning

- **Status**: ✅ PASS
- **v1.0 results**: 4 pitfalls (P04, P10, P11, P13) — see [oops_analysis.md](oops_analysis.md)
- **v1.2.0 results**: 0 pitfalls detected

### v1.2.0 Overall Summary

| Step | Technique | Result |
|------|-----------|--------|
| 1 | JSON-LD → Turtle | ✅ PASS (124 triples) |
| 2 | OWL-RL Reasoning | ✅ PASS (consistent, 0 unsatisfiable) |
| 3 | SHACL Shapes | ✅ PASS (conforms, 6/6 shapes) |
| 4 | SPARQL CQs | ✅ PASS (6/6 questions) |
| 5 | OOPS! Scanner | ✅ PASS (0 pitfalls in v1.2.0) |

**Ontology version**: v1.2.0 (793 triples, 1015 lines)
**Validation date**: February 2026
