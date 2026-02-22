# OOPS! Analysis Results — fram.ttl v1.0

## Pitfalls Detected

| Code | Name | Severity | # Elements | Details |
|------|------|----------|------------|---------|
| P04 | Unconnected ontology elements | Minor | 3 | DataFlow, Passthrough, InterpretationProfile |
| P10 | Missing disjointness | **Important** | 1 (ontology-wide) | Subclasses not declared as disjoint |
| P11 | Missing domain or range | **Important** | 12 | resonancePoint, originChain, criticalPath, variabilityHotspot, formula, unit, executionTimestamp, semanticRole, position, value, semanticMeaning, dataType |
| P13 | Inverse relationships not declared | Minor | 20 | All 20 object properties lack owl:inverseOf |

## Summary
- **Critical pitfalls**: 0
- **Important pitfalls**: 2 (P10, P11)
- **Minor pitfalls**: 2 (P04, P13)
- **Total affected elements**: 36

This matches the v1.0 results described in the EP2 v7 document. The v1.1 corrections (already documented) address all of these.
