# OOPS! Pitfall Analysis — FRAM Ontology

## v1.6.0 Results (Current)

Submitted `fram.ttl` v1.6.0 (1133 triples, ~1560 lines) to [OOPS!](https://oops.linkeddata.es/).

### Pitfalls Detected

| Code | Name | Severity | # Elements | Details |
|------|------|----------|------------|---------|
| P04 | Unconnected ontology elements | Minor | 8 | 8 gUFO classes declared for foundational alignment — known false positive (see below) |

### P04 Analysis (gUFO False Positive)

The 8 flagged elements are external gUFO classes used as `rdfs:subClassOf` targets for foundational ontology alignment:

| gUFO Class | Used by FRAM Class | Alignment Rationale |
|------------|-------------------|---------------------|
| `gufo:QualityValue` | `Phenotype` | Point in quality space |
| `gufo:Object` | `FRAMModel`, `FRAMScenario` | Persistent endurants |
| `gufo:Event` | `Function`, `FunctionalResonance`, `EmergentPhenotypeResult` | Temporal activities |
| `gufo:IntrinsicMode` | `Aspect` | Intrinsic property of functions |
| `gufo:Disposition` | `PerformanceCondition` | Latent condition |
| `gufo:RelationalQuality` | `Coupling` | First-class relation |
| `gufo:Quality` | `Variability`, `VariabilityDimension` | Measurable properties |
| `gufo:AbstractIndividual` | `Distribution`, `PhenotypeMappingRule`, `WAIDeclaration`, `WAIWADComparison` | Abstract specifications |

**Verdict**: **False positive**. These classes are intentionally declared without importing the full gUFO ontology, following a lightweight alignment pattern. OOPS! flags them as "unconnected" because they lack domain/range usage within the FRAM namespace, but they serve as superclass anchors for 16 `rdfs:subClassOf` axioms. This is a known limitation of OOPS! and was already present in v1.3.0.

### Pitfalls Fixed During v1.6.0 Development

| Code | Name | Cause | Fix |
|------|------|-------|-----|
| P13 | Missing inverses | 5 new v1.6.0 object properties (`hasPhenotypeMappingRule`, `hasWAIDeclaration`, `hasEmergentResult`, `hasWAIWADComparison`, `mapsToDimension`) lacked inverse declarations | Added 5 inverse properties: `isPhenotypeMappingRuleOf`, `isWAIDeclarationOf`, `isEmergentResultOf`, `isWAIWADComparisonOf`, `isMappingDimensionOf` |
| P05 | Inverse property wrongly defined | Initially created `isDimensionOf` as inverse of `mapsToDimension`, conflicting with existing `isDimensionOf` (inverse of `hasDimension`) | Renamed to `isMappingDimensionOf` |
| P19 | Multiple domain/range for property | Same `isDimensionOf` naming conflict caused dual domain declarations (VariabilityDimension→Phenotype AND VariabilityDimension→PhenotypeMappingRule) | Fixed by P05 rename |

### v1.6.0 Summary

- **Critical pitfalls**: 0
- **Important pitfalls**: 0
- **Minor pitfalls**: 1 (P04 — gUFO false positive, accepted)
- **Total affected elements**: 8 (all external gUFO classes)
- **Inverse declarations**: 27 (22 from v1.2.0 + 5 new in v1.6.0)
- **Disjointness blocks**: 8 (5 from v1.2.0, 2 from v1.5.0, 1 new in v1.6.0)

---

## v1.2.0 Results (Baseline — Post-Fix)

Submitted `fram.ttl` v1.0 (~558 triples) to [OOPS!](https://oops.linkeddata.es/).

### Pitfalls Detected

| Code | Name | Severity | # Elements | Details |
|------|------|----------|------------|---------|
| P04 | Unconnected ontology elements | Minor | 3 | `DataFlow`, `Passthrough`, `InterpretationProfile` — declared but not used as domain/range of any property |
| P10 | Missing disjointness | **Important** | 1 (ontology-wide) | Sibling subclasses not declared as `owl:disjointWith` or `owl:AllDisjointClasses` |
| P11 | Missing domain or range | **Important** | 12 | `resonancePoint`, `originChain`, `criticalPath`, `variabilityHotspot`, `formula`, `unit`, `executionTimestamp`, `semanticRole`, `position`, `value`, `semanticMeaning`, `dataType` |
| P13 | Inverse relationships not declared | Minor | 20 | All 20 object properties lack `owl:inverseOf` declarations |

### v1.0 Summary

- **Critical pitfalls**: 0
- **Important pitfalls**: 2 (P10, P11)
- **Minor pitfalls**: 2 (P04, P13)
- **Total affected elements**: 36

---

## Corrections Applied (v1.1.0 → v1.2.0)

### P04 Fix — Integrated Unconnected Elements

All three classes were integrated into property relationships:

| Class | Occurrences in v1.2.0 | Integration |
|-------|----------------------|-------------|
| `DataFlow` | 1 | Used in property domain/range declarations |
| `Passthrough` | 7 | Used as domain/range in `hasPassthrough`/`isPassthroughOf`, included in disjointness block |
| `InterpretationProfile` | 6 | Used as domain/range in `hasInterpretationProfile`/`isInterpretationProfileOf`, included in disjointness block |

### P10 Fix — Disjointness Axioms Added

5 `owl:AllDisjointClasses` blocks added (tagged `P10 FIX: DISJOINTNESS AXIOMS (v1.1.0)`):

| Block | Classes | Count |
|-------|---------|-------|
| 1 | `HumanFunction`, `TechnologicalFunction`, `OrganisationalFunction`, `BackgroundFunction`, `EntryFunction`, `ExitFunction` | 6 |
| 2 | `InputAspect`, `OutputAspect`, `PreconditionAspect`, `ResourceAspect`, `ControlAspect`, `TimeAspect` | 6 |
| 3 | `TimingPhenotype`, `PrecisionPhenotype` | 2 |
| 4 | `NormalDistribution`, `UniformDistribution`, `TriangularDistribution`, `LogNormalDistribution` | 4 |
| 5 | `InternalVariability`, `ExternalVariability`, `UpstreamVariability`, `DownstreamVariability` | 4 |

### P11 Fix — Domain and Range Declarations Added

All 12 flagged properties now have both `rdfs:domain` and `rdfs:range`:

| Property | Domain | Range |
|----------|--------|-------|
| `resonancePoint` | `FunctionalResonance` | `Function` |
| `originChain` | `FunctionalResonance` | `Function` |
| `criticalPath` | `FunctionalResonance` | `Coupling` |
| `variabilityHotspot` | `FunctionalResonance` | `Function` |
| `formula` | `Variable` | `xsd:string` |
| `unit` | `Distribution` | `xsd:string` |
| `executionTimestamp` | `OutputMessage` | `xsd:dateTime` |
| `semanticRole` | `Aspect` | `xsd:string` |
| `position` | `Aspect` | `xsd:integer` |
| `value` | `Constant` | `xsd:anySimpleType` |
| `semanticMeaning` | `Constant ∪ Variable` | `xsd:string` |
| `dataType` | `Constant ∪ Variable` | `xsd:string` |

### P13 Fix — Inverse Properties Declared

22 `owl:inverseOf` declarations added (0 in v1.0 → 22 in v1.2.0):

| Base Property | Inverse Property |
|---------------|-----------------|
| `hasFunction` | `isFunctionOf` |
| `hasCoupling` | `isCouplingOf` |
| `hasAspect` | `isAspectOf` |
| `sourceFunction` | `isSourceOf` |
| `targetFunction` | `isTargetOf` |
| `sourceAspect` | `isSourceAspectOf` |
| `targetAspect` | `isTargetAspectOf` |
| `hasVariability` | `isVariabilityOf` |
| `hasPerformanceCondition` | `isPerformanceConditionOf` |
| `hasDistribution` | `isDistributionOf` |
| `hasPhenotype` | `isPhenotypeOf` |
| `hasContributingFactor` | `isContributingFactorOf` |
| `hasConstant` | `isConstantOf` |
| `hasVariable` | `isVariableOf` |
| `hasOutput` | `isOutputOf` |
| `hasScenario` | `isScenarioOf` |
| `originChain` | `isOriginOf` |
| `resonancePoint` | `isResonancePointOf` |
| `criticalPath` | `isCriticalPathOf` |
| `variabilityHotspot` | `isVariabilityHotspotOf` |
| `hasInterpretationProfile` | `isInterpretationProfileOf` |
| `hasPassthrough` | `isPassthroughOf` |

---

## v1.2.0 Results (Post-Fix)

Submitted `fram.ttl` v1.2.0 (793 triples, 1015 lines) to [OOPS!](https://oops.linkeddata.es/).

### OOPS! Response

```xml
<oops:OOPSResponse></oops:OOPSResponse>
```

**Empty response = zero pitfalls detected.**

### v1.2.0 Summary

- **Critical pitfalls**: 0
- **Important pitfalls**: 0
- **Minor pitfalls**: 0
- **Total affected elements**: 0

---

## Comparison: v1.0 → v1.2.0 → v1.6.0

| Pitfall | v1.0 | v1.2.0 | v1.6.0 | Status |
|---------|------|--------|--------|--------|
| P04 (Unconnected elements) | 3 elements | 0 | 8 (gUFO — false positive) | ⚠️ Accepted |
| P10 (Missing disjointness) | Ontology-wide | 0 | 0 | ✅ Fixed |
| P11 (Missing domain/range) | 12 properties | 0 | 0 | ✅ Fixed |
| P13 (Missing inverses) | 20 properties | 0 | 0 (fixed during dev) | ✅ Fixed |
| P05 (Wrong inverse) | — | — | 0 (fixed during dev) | ✅ Fixed |
| P19 (Multiple domains) | — | — | 0 (fixed during dev) | ✅ Fixed |

| Metric | v1.0 | v1.2.0 | v1.6.0 |
|--------|------|--------|--------|
| Triples | ~558 | 793 | 1133 |
| Lines | ~600 | 1015 | ~1560 |
| Pitfalls | 4 | 0 | 1 (false positive) |
| Inverse declarations | 0 | 22 | 27 |
| Disjointness blocks | 0 | 5 | 8 |
| gUFO alignment axioms | 0 | 0 | 16 |
