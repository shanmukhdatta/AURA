# Git evidence inclusion policy

The current remote `.gitignore` contains `*.zip` and `*.sqlite3`. Those patterns would otherwise omit historical research. Do **not** accidentally leave archive and SQLite files untracked. Choose either a reviewed `.gitignore` change with explicit non-cache exceptions, or force-add verified archival research paths using `git add -f`. Run `git status --ignored` and cross-check Git's tracked-file list against `evidence/master_source_registry.csv` before a final commit.

Do not force-add model weights, secrets, downloaded third-party datasets lacking redistribution rights, local virtual environments, or unrelated caches.
