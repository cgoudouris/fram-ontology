# OOPS! Pitfall Analysis — FRAM Ontology

## v1.0 Results (Baseline)

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

## Comparison: v1.0 → v1.2.0

| Pitfall | v1.0 | v1.2.0 | Status |
|---------|------|--------|--------|
| P04 (Unconnected elements) | 3 elements | 0 | ✅ Fixed |
| P10 (Missing disjointness) | Ontology-wide | 0 | ✅ Fixed |
| P11 (Missing domain/range) | 12 properties | 0 | ✅ Fixed |
| P13 (Missing inverses) | 20 properties | 0 | ✅ Fixed |
| **Total** | **36 elements** | **0** | **✅ All fixed** |

| Metric | v1.0 | v1.2.0 |
|--------|------|--------|
| Triples | ~558 | 793 |
| Lines | ~600 | 1015 |
| Pitfalls | 4 | 0 |
| Inverse declarations | 0 | 22 |
| Disjointness blocks | 0 | 5 |
