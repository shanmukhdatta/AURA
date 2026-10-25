# GitHub research consolidation — safe workflow

This bundle is prepared for the existing AURA remote repository. Because the packaging environment cannot connect directly to github.com, **these files are not represented as already pushed**.

1. Clone `https://github.com/shanmukhdatta/AURA.git` on an authenticated machine.
2. Fetch the latest changes and branch from `origin/feature/external-validation-pipeline` (PR #2, fixing commit `b1e814f`).
3. Extract this bundle into a **separate** local folder (do not overwrite the clone blindly).
4. Run `python scripts/merge_into_existing_repo.py /path/to/extracted_bundle /path/to/git_clone` to add new files **without overwriting conflicting existing files**. Inspect `CONSOLIDATION_CONFLICTS.json` in the clone. Resolve any collisions manually with source diffs; do not silently choose the older workspace copy.
5. Optionally update the root README after reviewing its diff against the current feature branch. Keep `AURA_Stage7/`, `stage83/`, `paper/`, `aura_validation/` untouched where a different remote version exists.
6. Run source integrity scripts in the merged clone, the full CPU test suite, and the certificate replay using the exact environment instructions. Generate fresh logs; retain the original logs.
7. Inspect `git status`, `git diff --stat`, `git diff --check`, `git ls-files`, license/privacy scan. Reject unexpected modified/deleted files or missing artifacts.
8. Commit on a **new dedicated branch** (`feature/full-research-reproducibility`), push that branch, and open a draft PR. **Do not merge into main without explicit approval.**

Example commands (review before use):

```sh
git clone https://github.com/shanmukhdatta/AURA.git
cd AURA
git fetch origin
git switch -c feature/full-research-reproducibility origin/feature/external-validation-pipeline
python path/to/bundle/scripts/merge_into_existing_repo.py path/to/bundle .
python integrity/verify_archives.py
python integrity/verify_archive_members.py
python integrity/verify_workspace_files.py
python integrity/verify_evidence_links.py
python -m pytest AURA_Stage7/tests tests/test_validation_pipeline.py -q
git status --short
git diff --check
```

The provided merge script is intentionally conservative. It will copy only files that do not already exist; collisions remain unchanged and are reported in `CONSOLIDATION_CONFLICTS.json`. An explicit reviewed second pass is required for modifications. Existing paper LaTeX is preserved.
