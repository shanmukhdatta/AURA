"""Reproduce Stage 7 controlled experimental matrix (no cloud/GPU needed)."""
from pathlib import Path
import json,argparse
from aura_evaluation.study import run_study

def main(out_dir): return run_study(Path(out_dir))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    a=p.parse_args(); print(json.dumps(main(a.out),indent=2))
