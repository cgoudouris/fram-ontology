# EP2 — Ontology Validation Experiment Log

Validation benchmark for the FRAM Ontology. The current published baseline (v1.8.0) is exercised against two reference ABoxes: `eac1-li-huang-2025.{ttl,jsonld}` (Li & Huang, 2025; HSR Ningbo-Wenzhou) and `eac2-patriarca-et-al.-2024.{ttl,jsonld}` (Patriarca et al., 2024; Functional Random Walker). Earlier baselines (v1.6.0 over `boil-water-model.jsonld`, v1.2.0 over the same file, and an interim v1.7.0 single-model run over `li-huang-2025.{ttl,jsonld}` reaching 71.4% gap coverage) are preserved further down for traceability.

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

Executed against `fram.ttl` v1.8.0 (1309 TBox triples) with two ABoxes via the unified runner `validate_fram_model.py`:

- **EAC1** — `eac1-li-huang-2025.{ttl,jsonld}` (Li & Huang, 2025; HSR Ningbo-Wenzhou; 20 functions, 34 couplings, 17 receiving functions; 2860 ABox triples)
- **EAC2** — `eac2-patriarca-et-al.-2024.{ttl,jsonld}` (Patriarca et al., 2024; FRW; 14 functions, 21 couplings, 11 receiving functions; 2196 ABox triples)

### Pre-requisite: W3C RDF 1.1 Conformance

| Serialization | Format | Triples | Status |
|---------------|--------|---------|--------|
| `fram.ttl` | Turtle | 1309 | VALID |
| `fram.owl` | RDF/XML | 1309 | VALID |
| `context.jsonld` | JSON-LD 1.1 | 276 terms | VALID |

Cross-format consistency: TTL = OWL = 1309 triples. **PASS**.

### TBox Metrics (v1.8.0)

| Metric | Value |
|--------|-------|
| Classes (FRAM) | 59 |
| Object Properties | 65 |
| Datatype Properties | 64 |
| Total Properties | 129 |
| `owl:inverseOf` pairs | 29 |
| `owl:AllDisjointClasses` blocks | 8 |
| gUFO `rdfs:subClassOf` axioms | 16 |
| SKOS definitions | 30 |
| Total TBox triples | 1309 |

### ABox Metrics

| Metric | EAC1 (Li & Huang, 2025) | EAC2 (Patriarca et al., 2024) |
|--------|:---:|:---:|
| Total ABox triples | 2860 | 2196 |
| Functions | 20 | 14 |
| Couplings | 34 | 21 |
| Receiving functions (CQ6) | 17 | 11 |

### Step 1: JSON-LD -> Turtle Conversion

- **Status**: PASS (both models)
- **Notes**: All terms resolved to IRIs in `fram:` and `model:` namespaces.

### Step 2: OWL-RL Reasoning & Consistency

| Metric | EAC1 | EAC2 |
|--------|---:|---:|
| TBox triples | 1309 | 1309 |
| ABox triples | 2860 | 2196 |
| Total before reasoning | 4169 | 3505 |
| Inferred triples | 5321 | 4376 |
| Reasoning time | 1.04s | 0.85s |
| `owl:Nothing` instances | 0 | 0 |
| Unsatisfiable classes | 0 | 0 |
| **Status** | **PASS** | **PASS** |

### Step 3: SHACL Shape Validation

- **Status**: PASS (both models) — `Conforms = True`, 0 violations against the 8 shapes (S1–S8).
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

- **Status**: PASS (6/6 for both models)

| CQ | Question | EAC1 | EAC2 |
|----|----------|---:|---:|
| CQ1 | Functions and their types | 20 | 14 |
| CQ2 | Couplings between functions | 34 | 21 |
| CQ3 | Aspects per function | 20 | 14 |
| CQ4 | Functions with variability metadata | 20 | 14 |
| CQ5 | Functions with variability phenotypes | 20 | 14 |
| CQ6 | Functions receiving input via couplings | 17 | 11 |

### Step 5: OOPS! Pitfall Scanning

- **Status**: PASS
- **API**: `https://oops.linkeddata.es/rest`
- **Pitfalls detected**: **0** (zero) at any severity level (Critical, Important, Minor).
- **Notes**: OOPS! operates over the TBox (`fram.ttl`) and is invariant across ABoxes. Adding an ABox to a graph already free of pitfalls cannot introduce new TBox-level pitfalls. See [oops_analysis.md](oops_analysis.md) for the full evolution since v1.0.

### Step 6: Round-Trip Fidelity

| Test | Description | EAC1 | EAC2 | Note |
|------|-------------|:---:|:---:|------|
| RT1 | TTL -> JSON-LD -> TTL | **PASS** | **PASS** | Isomorphic after double conversion |
| RT2 | JSON-LD -> TTL -> JSON-LD | FAIL | FAIL | Expected: blank node instability |
| RT3 | TTL == JSON-LD (direct) | FAIL | FAIL | Expected: structural differences |

RT1 is the binding criterion. RT2 and RT3 reproduce well-known phenomena of RDF serializers (BNode renaming and JSON-LD framing flexibility) and are documented as expected outcomes by the protocol.

### Step 7: Gap Analysis

- **Status**: REPORTED (informational)
- **EAC1**: 56/71 predicates matching (**78.9%**); 15 with differences. Predicates only in JSON-LD: `fram:framPrinciples` (4 occurrences). Predicates only in TTL: `owl:imports`, `fram:Control`, `fram:Human`, `fram:Input`, `fram:Precondition`, `fram:Resource`.
- **EAC2**: 58/74 predicates matching (**78.4%**); 16 with differences. Predicates only in JSON-LD: `fram:framPrinciples` (4 occurrences). Predicates only in TTL: `owl:imports`, `fram:Control`, `fram:Human`, `fram:Input`, `fram:Precondition`, `fram:Resource`, `fram:Time`.
- **Notes**: Coverage cannot reach 100% by construction. The TTL form exposes every RDF predicate of the TBox (including `owl:imports`, structural metadata, and named aspect IRIs reused as predicates), whereas the compact JSON-LD form projects a subset of those predicates onto named keys via the `@context`. JSON-LD framing also injects `fram:framPrinciples`. Reaching 100% would require an expanded JSON-LD form, which would defeat the legibility goal of the canonical context. Semantic equivalence is verified by Step 6 (graph isomorphism, RT1) and Step 8 (gold-standard SPARQL equivalence).

### Step 8: SPARQL Semantic Equivalence (Gold Standard)

- **Status**: PASS (9/9 = 100% for both models; SQ10 N/A — empty in both sides)

| Query | Domain | EAC1 (TTL=JSON-LD) | EAC2 (TTL=JSON-LD) |
|-------|--------|:---:|:---:|
| SQ1 | Model identity and metadata | 1 | 1 |
| SQ2 | Functions with type and category | 20 | 14 |
| SQ3 | Aspect count per function | 20 | 14 |
| SQ4 | Couplings with source/target functions | 34 | 21 |
| SQ5 | Variability potential per function | 20 | 14 |
| SQ6 | Quantitative metadata inventory | 20 | 14 |
| SQ7 | Interpretation profiles | 15 | 10 |
| SQ8 | Output routing topology | 34 | 21 |
| SQ9 | Aggregate counts | 1 | 1 |
| SQ10 | Scenarios | -- | -- |

**Both serializations are SPARQL-equivalent** for both reference models: identical queries yield identical results across all fundamental FRAM domain concepts. This confirms semantic equivalence per W3C RDF 1.1 Concepts (Section 3.5).

### v1.8.0 Overall Summary

| Step | Technique | EAC1 | EAC2 |
|------|-----------|:---:|:---:|
| 0 | W3C RDF 1.1 Conformance | PASS (TTL=OWL=1309) | PASS (TTL=OWL=1309) |
| 1 | JSON-LD -> Turtle | PASS (2860 triples) | PASS (2196 triples) |
| 2 | OWL-RL Reasoning | PASS (5321 inferred, 0 unsat) | PASS (4376 inferred, 0 unsat) |
| 3 | SHACL Shapes | PASS (conforms, 8/8 shapes) | PASS (conforms, 8/8 shapes) |
| 4 | SPARQL CQs | PASS (6/6) | PASS (6/6) |
| 5 | OOPS! Scanner | PASS (0 pitfalls; TBox-level) | PASS (0 pitfalls; TBox-level) |
| 6 | Round-trip Fidelity | PASS (RT1 isomorphic) | PASS (RT1 isomorphic) |
| 7 | Gap Analysis | 78.9% (informational) | 78.4% (informational) |
| 8 | SPARQL Equivalence | PASS (9/9 = 100%) | PASS (9/9 = 100%) |

**Ontology version**: v1.8.0 (1309 TBox triples; 59 classes; 129 properties)
**Reference ABoxes**: EAC1 (Li & Huang, 2025) and EAC2 (Patriarca et al., 2024)
**Runner**:
```bash
python validation/validate_fram_model.py examples/eac1-li-huang-2025.ttl       examples/eac1-li-huang-2025.jsonld       --skip-oops
python validation/validate_fram_model.py examples/eac2-patriarca-et-al.-2024.ttl examples/eac2-patriarca-et-al.-2024.jsonld --skip-oops
```

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
