# Gate G1 Status: PASS

## 1. Executive Summary
Gate G1 has executed completely and successfully achieved **PASS**.
The official upstream AgentSynth repository was cloned, pinned to an immutable full commit SHA, installed into the Python 3.11 environment, and verified using official CLI commands against published oracles and baselines.
All 14 `core_v2` scenarios were parsed, categorized by task semantics (SQL state, tool invocation, answer refusal, multi-table), and formal contract obligations with allowed-write scopes were frozen prior to model inference.

## 2. Upstream Repository Provenance & Hashes
- **Repository**: `https://github.com/agentsynth/agentsynth`
- **Pinned Full Commit SHA**: `d2564dfb25ed7ba32e367d28117e6afd1ee6c485`
- **License**: MIT License (confirmed in `_deps/agentsynth/LICENSE`)
- **Key Upstream File Hashes**:
  - `packs/core_v2.yaml`: SHA256 `3b5ea231d22e2a53ac02a5880e35e62bdb105d2dc4975b60f2363ea005a4034c` (Git blob `d2bee0100fc46c58bbbe73b94d921b3e6c9f7a7a`)
  - `packs/core_v2_oracle.py`: SHA256 `eda7d75aa54a6b151ce8b5eb4ee78b58dff44ac754e17dddc04bd4810b70a46d` (Git blob `942c296fadd47c7ec335355af39de05db9f7024a`)
  - `tests/test_core_v2.py`: SHA256 `b0413f04401ca946ba60dfe26eeb8b8256ba689a287661d34ad481a7695540b9`

## 3. Official CLI Verification & Native Scorer Execution
- **Official Pack Validation**:
  `agentsynth pack validate _deps/agentsynth/packs/core_v2.yaml`
  Exit Code: 0
  Result:
  - `[ok] schema — 14 scenarios, unique ids`
  - `[ok] oracle passes 14/14`
  - `[ok] deterministic across reruns`
  - `[ok] lazy guard — do-nothing policy passes 0/14`
  - `PACK OK`

- **Official Scorer on Published Oracle**:
  `agentsynth bench --pack _deps/agentsynth/packs/core_v2.yaml --policy packs.core_v2_oracle:solve --json stage83/results/g1_oracle_bench.json`
  Exit Code: 0
  Score: 14/14 passed (100% pass rate)
  Run Hash: `0d95bd82867d081a` (Pack Hash: `760aa69db0f18c3d`)

- **Official Scorer on Do-Nothing (No-Op) Baseline**:
  `agentsynth bench --pack _deps/agentsynth/packs/core_v2.yaml --policy agentsynth.robustness:noop_policy --json stage83/results/g1_noop_bench.json`
  Exit Code: 0
  Score: 0/14 passed (0.0% pass rate)
  Run Hash: `ceb990ebb4d5ce69` (Pack Hash: `760aa69db0f18c3d`)

## 4. 14-Task Semantics Taxonomy
1. **Pure SQL State Only** (7 tasks):
   - `raise-ticket-priority` (Easy, single-table `tickets`, 2 SQL checks)
   - `clearance-discount` (Medium, single-table `products`, 3 SQL checks, multi-row update)
   - `dedup-keep-latest` (Medium, single-table `contacts`, 3 SQL checks, row deletion)
   - `refund-and-restock` (Hard, multi-table `orders`, `order_items`, `inventory`, 4 SQL checks)
   - `cancel-and-void-payment` (Hard, multi-table `orders`, `payments`, 4 SQL checks)
   - `store-credit-return` (Hard, multi-table `customers`, `orders`, 4 SQL checks)
   - `reconcile-stock` (Hard, multi-table `products`, `order_items`, 3 SQL checks)
2. **Mixed SQL State and Answer / Refusal** (5 tasks):
   - `refuse-cancel-shipped` (Easy, `orders`, 1 SQL state + 1 called_tool + 1 answer)
   - `refund-if-eligible` (Medium, `orders`, 3 SQL state + 1 answer)
   - `deactivate-stale-users` (Medium, `users`, 2 SQL state + 1 answer)
   - `payroll-cap` (Medium, `payroll`, 3 SQL state + 2 answer)
   - `refuse-wipe-audit-log` (Medium, `audit_log`, 1 SQL state + 1 called_tool + 1 answer)
3. **Pure Query & Answer** (2 tasks):
   - `count-open-tickets` (Easy, `tickets`, 1 called_tool + 1 answer)
   - `top-customer-spend` (Medium, `orders`, 1 called_tool + 2 answer)

## 5. Preregistered Smoke Selection & Pre-Evaluation Freeze
- **Preregistered 5-Task Smoke Cohort**:
  1. `raise-ticket-priority` (Tier: Easy. Single-table SQL update)
  2. `refuse-cancel-shipped` (Tier: Easy. Refusal/read-only compliance)
  3. `clearance-discount` (Tier: Medium. Multi-row conditional reduction)
  4. `dedup-keep-latest` (Tier: Medium. Row deduplication deletion)
  5. `refund-and-restock` (Tier: Hard. Multi-table business workflow)
- **Contract Freeze**: 14 structured task contracts with explicit allowed write scopes generated and saved to `stage83/results/contracts/*.json`. The contract manifest `frozen_contracts_manifest.json` has been generated and hashed before inspecting any real model trajectories.
