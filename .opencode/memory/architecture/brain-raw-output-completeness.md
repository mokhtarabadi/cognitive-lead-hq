---
tags: [architecture, brain, output-contracts, reliability]
---

Brain raw output must be persisted before triage and remain available to Hands in full.

Rule: The Brain Bridge must write the raw provider output to the per-turn artifact before XML extraction, strict reject, semantic reject, or preview rewriting. Hands must be able to read the complete raw output for every turn. XML extraction is advisory; executability remains behind the shared deterministic extractor plus validate_hands_xml_blocks gate. Agents must not improvise Python parsers for control payloads. Marker prefixes, response IDs, and bounded recovery remain stable. Reason: a reject preview previously destroyed the only copy of a ~23 KB answer and forced a divergent re-emission.
