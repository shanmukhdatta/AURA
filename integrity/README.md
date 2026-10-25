# Integrity and independent readback

This directory houses the **packaging-time** original-file hashes and archive-member SHA256 checks, alongside AURA's historical task-level receipts and certificate replays.

Run after extracting the package at repository root:

```sh
python integrity/verify_archives.py
python integrity/verify_archive_members.py
python integrity/verify_evidence_links.py
```

These checks verify that files survived the packaging and copy process. They **do not** establish that a model answer is semantically correct, that a third-party upstream package is licensed for redistribution, or that a certificate uses trusted external signing. The original Stage 8.3 SHA256 manifest is located in `stage83/results/` and should be validated by the external-validation runner.

The corrected external-validation report records 246/246 for its Stage 8.3 manifest; a separate historical manifest reports 131/135 with four mismatches. These are separate integrity scopes, not contradictory counts for the same manifest.
