# Stage 3 engineering and verification decisions

Date: 24 October 2026. This continues Stage 0 research freeze, Stage 1 formal interface definitions and Stage 2 independent evidence collection.

## Contract-defined task completion

An agent claiming that every tool returned `ok` is insufficient. The Stage 3 engine evaluates a reviewed `TaskContract`'s outcome, frame, process and external obligations against independent `Observation` records from registered read-only `ProbeSpec` adapters. It emits a `Certificate` matching the unchanged Stage 1 Schema.

**Conservative evaluation:** An atomic predicate is `pass` if an accepted independent fact proves it true with required full-scope receipts; `fail` when an accepted fact demonstrates a violation; `unknown` when a required fact or its coverage is unavailable. FAIL dominates ordinary unknown. Authoritative same-epoch contradiction produces UNCERTAIN + `evidence_conflict`. The engine never uses a hidden actual-world outcome or finite-world reference catalogue.

**Frame invariant:** For `closed_world`, the contract must cover its declared mutable surfaces with independent zero-unaccounted-mutation frame predicates. The full-frame change count is computed by the Stage 2 trusted state-diff adapter against explicit allowed effects. Complete coverage receipts must substantiate that count. Snapshot-pair receipts do **not** establish absence of transient reverted writes. A declared transient-history obligation separately requires a complete-journal receipt.

**Trust boundary:** The `verify_saved_run` entry requires a real Stage 2 snapshot pair, checks hashes/epoch identity and validates the observation receipts against those snapshots. The reference fixture pathway explicitly does not substantiate its simulated snapshot references; its outputs are labeled educational only. No attempt is made to infer an external operation from a timeout or access denial.

**Certificate:** run/contract hash/epoch, three-way verdict, diagnostic status, every obligation result, inspector and evidence IDs, complete verified frame surfaces, unresolved IDs, capture/probe/verifier metered costs, and trust assumptions. Certificates are JSON and validated against the Stage 1 schema before return. A checksum is an integrity reference, not an independently authenticated proof against privileged tampering.

## Stage 1 synthetic observation migration

Stage 1 fixture JSON structures passed their authoring checks, but the original `payload_sha256` strings do not equal the canonical digest computed by Stage 2's `observation_digest`. Stage 3 generated **test-only** copies and recomputed 52 checksum fields; no facts, coverage receipts, expected verdicts, or contracts were altered. Changes are documented in `STAGE1_FIXTURE_HASH_COMPATIBILITY.json`. Original Stage 1 files remain separate and unchanged.

## Stage 3 acceptance and restrictions

- Full suite: 76 passing tests (35 inherited Stage 2 tests and 41 new verifier tests).
- Stage 1 reference cases: 12/12 expected PASS/FAIL/UNCERTAIN and `decision_status` outcomes.
- Six fresh real local controlled runs: clean PASS; missing report, collateral change, silent no-op and missed validation FAIL; denied readback UNCERTAIN.
- Negative tests reject tampered observation digests, incorrect snapshot refs, mutation frame omission, self-reported persistence, cross-epoch evidence, invalid counts and unsupported operators.
- Engine version is `conservative`, **not** the planned `bounded_exact` possible-world solver. The `same_as` comparison conservatively treats null/missing values as UNKNOWN to prevent accidental equality certification.
- Stage 3 does not implement CERA adaptive inspection planning; this is reserved for later stages and must be evaluated independently.
- No independent external benchmark, probabilistic soundness guarantee, security penetration test, or paper novelty result is claimed.

## Known limitations and follow-up

- Expected results are based on controlled demonstration tasks authored by the project; they are not evidence of out-of-distribution superiority.
- The contract schema does not express arbitrary temporal formulas or complex effect rules. Unknown patterns remain unsupported.
- A PASS applies only to the declared mutable frame in the quiescent sandbox and observed process clauses.
- More general conditional-trust acceptance for third-party service receipts needs a verified provider protocol; current version does not promote conditionally trusted probes into authoritative facts.
- Complete-journal capture for transient effects remains unimplemented; the engine will return UNCERTAIN when such evidence is required.
- Inspection/capture cost recorded here is for development diagnostics, not an experimental cost-benefit result.
