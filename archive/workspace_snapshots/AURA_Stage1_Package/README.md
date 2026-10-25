# AURA Stage 1 — Formal Specification Package

**Date:** 24 October 2026  
**Status:** Pre-implementation Stage 1 design completed; independent review pending.  
**No AURA runtime/verifier/planner code is included.**

## Start here

1. Read `AURA_Stage1_Formal_Specification_v1.pdf` or the editable `.md` version.
2. Examine the four Draft 2020-12 schemas in `schemas/`:
   - `TaskContract.schema.json`
   - `ProbeSpec.schema.json`
   - `Observation.schema.json`
   - `Certificate.schema.json`
3. Review `acceptance/acceptance_cases.csv` and the 12 corresponding `examples/` directories.
4. Inspect `examples/sample_certificate_illustrative.json` only as an interface example, **not** an actual AURA verification output.
5. Read `acceptance/authoring_validation_report.json` for the exact scope of offline validations.

## Fixture organization

Every `examples/<case>/` directory contains the `task_contract.json`, `probe_catalogue.json`, `observations.json`, `reference_possible_worlds.json`, and `expected.json` files.

The `harness_hidden/` directory contains actual-world labels used only for this **design-stage evaluation harness**. In future experiments these must be physically and logically inaccessible to the verifier, even if they exist in the research repository. No hidden truth may flow into a verification certificate or probe response.

## What is verified so far

Four JSON Schemas pass Draft 2020-12 meta-schema validation. All supplied contract, probe, and observation objects are structurally validated, as is one illustrative certificate. The 12 acceptance examples match the verdicts of a bounded offline reference check used exclusively to verify these design fixtures. Basic cross-object identifiers, fact registrations, read-only claims, source coverage, and deterministic payload hashes were checked during package construction.

These authoring tests **are not** execution benchmarks, new research findings, or a proof of the proposed AURA algorithm's correctness. Some declared semantic constraints (e.g., predicate operator typing, authentication, true snapshot atomicity, independent adapter read-only behavior) require implementation and independent testing in Stage 2 and beyond.

## Next stage

**Stage 2: Trusted Environment & Evidence Infrastructure.** Implement the isolated SQLite/filesystem sandbox, consistent snapshots and scoped diffs, read-only evidence adapters, semantic validation, and measurement of inspection costs. No adaptive CERA planner is needed yet.
