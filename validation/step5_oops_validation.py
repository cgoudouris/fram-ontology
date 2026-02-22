"""
Step 5: Automated Validation with OOPS!
========================================
Submits the ontology fram.ttl to the OOPS! (Ontology Pitfall Scanner)
validator via its REST API and analyzes the pitfall report.

Part of the FRAM Ontology Validation Benchmark (EP2).
"""

import os
import re
import time
from collections import Counter
import requests
from rdflib import Graph

# Resolve paths relative to repository root
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
VALIDATION_DIR = os.path.dirname(__file__)

print("=" * 70)
print("STEP 5: AUTOMATED VALIDATION WITH OOPS!")
print("=" * 70)

# ── 1. Convert fram.ttl to RDF/XML (format accepted by OOPS!) ──
tbox_path = os.path.join(REPO_ROOT, "fram.ttl")

print(f"\n[1/3] Converting fram.ttl to RDF/XML...")
g = Graph()
g.parse(tbox_path, format="turtle")
rdfxml = g.serialize(format="xml")
print(f"      Ontology loaded: {len(g)} triples")
print(f"      RDF/XML generated: {len(rdfxml)} bytes")

# Save for reference
rdfxml_path = os.path.join(VALIDATION_DIR, "fram_rdfxml.owl")
with open(rdfxml_path, "w") as f:
    f.write(rdfxml)

# ── 2. Submit to OOPS! via API ──
print("\n[2/3] Submitting to OOPS! (https://oops.linkeddata.es/rest)...")

oops_url = "https://oops.linkeddata.es/rest"
oops_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<OOPSRequest>
  <OntologyURI></OntologyURI>
  <OntologyContent><![CDATA[{rdfxml}]]></OntologyContent>
  <Pitfalls></Pitfalls>
  <OutputFormat>XML</OutputFormat>
</OOPSRequest>"""

headers = {"Content-Type": "application/xml"}

start_time = time.time()
try:
    response = requests.post(oops_url, data=oops_payload.encode("utf-8"), headers=headers, timeout=120)
    elapsed = time.time() - start_time
    print(f"      Status: {response.status_code} ({elapsed:.1f}s)")

    if response.status_code == 200:
        result_xml = response.text
        # Save raw response
        response_path = os.path.join(VALIDATION_DIR, "oops_response.xml")
        with open(response_path, "w") as f:
            f.write(result_xml)
        print(f"      Response saved to: oops_response.xml ({len(result_xml)} bytes)")
        api_success = True
    else:
        print(f"      [ERROR] Unexpected status: {response.status_code}")
        print(f"      Response: {response.text[:500]}")
        api_success = False
except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"      [ERROR] Timeout after {elapsed:.1f}s")
    api_success = False
except Exception as e:
    elapsed = time.time() - start_time
    print(f"      [ERROR] {type(e).__name__}: {e}")
    api_success = False

# ── 3. Analyze results ──
print(f"\n[3/3] Analyzing results...")

if api_success:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(result_xml)
    except ET.ParseError:
        # OOPS! sometimes returns non-standard XML; try to parse pitfalls manually
        print("      Parsing XML response...")
        # Count pitfalls by searching for patterns
        pitfall_pattern = re.compile(r'<oops:hasCode[^>]*>(\w+)</oops:hasCode>', re.IGNORECASE)
        pitfalls_found = pitfall_pattern.findall(result_xml)

        if not pitfalls_found:
            # Try alternative patterns
            pitfall_pattern2 = re.compile(r'<oops:hasPitfall|<Pitfall|pitfall', re.IGNORECASE)
            pitfalls_found2 = pitfall_pattern2.findall(result_xml)

            # Look for "No pitfall" or similar
            no_pitfall = re.search(r'no.?pitfall|0.?pitfall|zero.?pitfall', result_xml, re.IGNORECASE)

            if no_pitfall or (not pitfalls_found2 and len(result_xml) < 500):
                print("      [OK] No pitfalls detected by OOPS! ✅")
            else:
                # Parse the response more carefully
                print(f"      Analyzing response ({len(result_xml)} bytes)...")
                # Show a snippet
                print(f"      First 1000 chars:")
                print(result_xml[:1000])
        else:
            pitfall_counts = Counter(pitfalls_found)
            print(f"      Pitfalls found: {len(pitfalls_found)}")
            for code, count in sorted(pitfall_counts.items()):
                print(f"        {code}: {count} occurrence(s)")

    # Also try to extract severity information
    severity_pattern = re.compile(r'<oops:hasImportanceLevel[^>]*>(\w+)</oops:hasImportanceLevel>', re.IGNORECASE)
    severities = severity_pattern.findall(result_xml)
    if severities:
        sev_counts = Counter(severities)
        print(f"\n      Severity levels:")
        for sev, count in sorted(sev_counts.items()):
            print(f"        {sev}: {count}")

    # Extract specific pitfall descriptions
    desc_pattern = re.compile(r'<oops:hasDescription[^>]*>(.*?)</oops:hasDescription>', re.IGNORECASE | re.DOTALL)
    descriptions = desc_pattern.findall(result_xml)
    if descriptions:
        print(f"\n      Pitfall descriptions:")
        for i, desc in enumerate(descriptions[:10]):
            print(f"        [{i+1}] {desc.strip()[:120]}")

else:
    print("      [SKIP] Analysis not performed due to API failure")

# ── 4. Summary ──
print("\n" + "=" * 70)
print("STEP 5 SUMMARY")
print("=" * 70)
print(f"  OOPS! API:              {'Available' if api_success else 'Unavailable'}")
print(f"  Response time:          {elapsed:.1f}s")
if api_success:
    print(f"  Response:               {len(result_xml)} bytes")
    print(f"  Result:                 See analysis above")
