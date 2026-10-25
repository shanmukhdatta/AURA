# Proof-chain indexing limitations

`proof_chain_index.csv` contains one row per supplied 59-episode registry record. The raw registry row is retained verbatim as JSON within each row, preserving source paths when provided. The index does not auto-invent per-run certificate paths. Use the original registry source fields and zip-member registry to resolve each raw artifact. The 59 external replays do not include Stage8.1 Qwen/AppWorld.
