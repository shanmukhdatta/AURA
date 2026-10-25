# Evidence and provenance indexes

- `master_source_registry.csv`: original top-level loose files and exact archive file locations, length and SHA256.
- `master_archive_member_registry.csv`: every file member of each original ZIP, original member path, extracted GitHub path, member SHA256, and ZIP CRC32.
- `experiment_registry.csv`: the 59-row original handoff episode registry (not inclusive of the Stage 8.1 local/AppWorld experiments).
- `proof_chain_index.csv`: per-episode pointers to original registry fields and located evidence directories; no missing links are silently supplied.
- `missing_or_unverified.md`: discrepancies and non-equivalence across collections.

Archive hashes can be checked independently using the scripts under `../integrity/`. The originals remain untouched under `../archive/`.
