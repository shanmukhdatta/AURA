# AURA Stage 8.1 — AppWorld root-path repair, v7

## Why the earlier v6 benchmark stopped

The genuine uploaded v6 Kaggle evidence shows that AppWorld was installed in Python 3.11 and that `appworld download data` exited 0, but `load_task_ids('dev')` failed with:

`The task directory (.../appworld_root/data/tasks) doesn't exist.`

An independent inspection of the **official AppWorld CLI source** found a concrete root-configuration mismatch: the `download data` command exposes `--root` with default `.` and calls `update_root(root)`. The v6 notebook only set the `APPWORLD_ROOT` environment variable. The CLI's default root could therefore point to Kaggle's current working directory while the runtime loader used the notebook's private `appworld_root`. This explains the observed failure and is the main defect corrected in v7. The previous ZIP does not prove whether the download otherwise succeeded, so v7 checks that as well.

Sources:
- Official CLI root configuration: https://github.com/StonyBrookNLP/appworld/blob/main/src/appworld/cli.py
- Official downloader (which may return without raising after a failed HTTP download): https://github.com/StonyBrookNLP/appworld/blob/main/src/appworld/download.py
- Expected data layout and installation: https://github.com/StonyBrookNLP/appworld#installation

## What v7 changes

1. Uses Python 3.11 and an isolated environment, as in v6.
2. Calls `python -m appworld.cli download data --root <the-exact-AppWorld-runtime-root>` rather than relying on `APPWORLD_ROOT` alone.
3. Fails closed unless the expected `data/tasks`, `data/base_dbs` and `data/datasets/dev.txt` exist and the first three selected task specification files exist.
4. Records a concise `data_preflight.json` indicating the expected root, whether files exist, how many task IDs were loaded and whether a data directory was detected elsewhere. If a download exits 0 but produces no data, it captures the download console tail in `SETUP_DIAGNOSTIC.txt`.
5. Tries an actual first AppWorld world and its official no-action evaluator **before** any GPU model download.
6. Only after successful preflight loads Qwen2.5-3B-Instruct and runs three real AppWorld `dev` tasks with native evaluation. Previous AURA local workflows **are not rerun**.
7. Exports only configuration, audited setup/evidence status, model-generated code trajectories, official result *summaries* and native API-call logs (where available); never full AppWorld databases, private grader modules, model weights or installed packages. A SHA256 manifest accompanies the ZIP.

## Kaggle execution

1. Create a **new Kaggle notebook** (not the v5/v6 notebook), import `AURA_AppWorld_RootFix_v7_Kaggle.ipynb`.
2. Enable **Internet** and **GPU** (T4 recommended).
3. Click **Run All**. The notebook will stop before GPU inference if AppWorld data installation/preflight fails; its final cell will still package the diagnostic.
4. Download `/kaggle/working/AURA_APPWORLD_STAGE8_1_v7_RESULTS.zip`.
5. Upload that ZIP to the AURA chat for independent review. If possible, also report the printed final `STAGE 8.1 APPWORLD READINESS` value.

**Interpretation:** `READY_FOR_EXTERNAL_NATIVE_BENCHMARK_ANALYSIS` means three native AppWorld dev tasks were executed and their evidence passed the notebook's packaging audit. It does **not** mean all tasks succeeded or that AURA independently validated AppWorld. Failures should be investigated from the ZIP before another rerun.

## Verification status in the author's sandbox

- Notebook is valid per `nbformat.validate`; all executable cells compile.
- Tested with a fake downloader that saves under the correct root: **PASS**.
- Fake downloader saves to the wrong root: **rejected with diagnostic**.
- Fake downloader exits 0 but prints HTTP 403: **rejected with diagnostic**.
- Setup failure ZIP, normal mocked AppWorld export and SHA256 manifest checks: **PASS**.
- Three-task mocked AppWorld subprocess exchange and native-evaluation export: **PASS**.
- Actual network/AppWorld task execution and real Qwen inference in Kaggle: **NOT RUN** in the author's sandbox. The notebook will record these outcomes when you run it.

## Research scope

The existing four local LLM/AURA episodes were already audited. This v7 run aims only to collect the missing native AppWorld external-agent evidence. Stage 8.1 cannot claim external independent **AURA** verification until AppWorld task contracts and observable state/effect evidence are translated into and checked by AURA separately from the official native evaluator.
