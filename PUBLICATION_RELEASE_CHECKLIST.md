# Paper reproducibility release acceptance gates

The research archive is ready to **import**; it is not yet evidence that the full historical record was pushed to GitHub. Use this checklist in the **cloned GitHub feature branch** before opening the release PR.

- [ ] Original PR #1 and PR #2 files and Git history preserved; no deletion or force-push.
- [ ] Merge importer `CONSOLIDATION_CONFLICTS.json` reviewed; canonical verifier and validation versions selected deliberately rather than overwritten.
- [ ] All original 95 loose records, 33 ZIPs, and 70 additional workspace files present. See `evidence/` manifests; counts correspond to this generated bundle only.
- [ ] All 2,619 archived member files exist and hashes match.
- [ ] `python integrity/verify_archives.py` passes.
- [ ] `python integrity/verify_archive_members.py` passes.
- [ ] `python integrity/verify_workspace_files.py` passes.
- [ ] `python integrity/verify_evidence_links.py` passes.
- [ ] `python -m aura_validation.runner` replays all 59 saved certified episodes, 246/246 Stage 8.3 hashes, and preserves source/noninterference evidence.
- [ ] Full test suite executed on integration branch and real stdout/stderr included; original historical log remains unmodified.
- [ ] `git status --ignored` checked. **Current remote `.gitignore` ignores all `.zip` and `.sqlite3`**; explicitly include these required research artifacts and ensure no private/restricted content is added.
- [ ] `python scripts/check_git_tracking.py` passes **after** Git staging; a path that exists only in the local workspace is not yet part of the GitHub research record.
- [ ] Historical integrity manifest four mismatches reconciled or explicitly discussed in limitations, not silently overwritten. The offline assembled standalone copy lacks 11 remote-only historical files; merging the existing Git branch retains them.
- [ ] Stage8.1 local Qwen and AppWorld outcomes separated from the 59 certification episodes. Stage8.4 not claimed without verified files.
- [ ] READMEs, proofs, Kaggle notebooks, contracts, benchmark licensing, privacy, database data and publication claims reviewed.
- [ ] Only the reviewed consolidation feature branch is pushed; `main` stays unchanged until separate approval.

## Manuscript evidence statement

The public GitHub paper link should reference an **immutable commit or release tag** after all files are pushed and the checks above pass, rather than a changing feature branch. Record the final SHA in the manuscript reproducibility section.
