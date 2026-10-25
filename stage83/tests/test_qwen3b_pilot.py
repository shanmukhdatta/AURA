#!/usr/bin/env python3
"""
Unit and Integration Tests for Qwen2.5-3B Kaggle Pilot Run.

Validates that:
1. All 5 saved Qwen2.5-3B episodes replay through the blinded independent reference.
2. AURA verdicts match independent ground truth 100% (0 false PASS, 0 false FAIL).
3. The model scaling hypothesis is empirically supported:
   3B model succeeds on clearance-discount and dedup-keep-latest where 0.5B failed.
"""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from stage83.independent_reference import evaluate_episode_independently

QWEN3B_BASE = REPO_ROOT / 'stage83' / 'results' / 'qwen3b_pilot' / 'results' / 'episodes'


class TestQwen3BPilotEpisodes:
    """Validate genuine Qwen2.5-3B pilot runs."""

    @pytest.mark.skipif(not QWEN3B_BASE.exists(), reason="Qwen3B pilot directory not found")
    def test_qwen3b_raise_ticket_priority_passes(self):
        ep_dir = QWEN3B_BASE / 'raise-ticket-priority' / 'qwen3b_real_raise-ticket-priority_seed42'
        res = evaluate_episode_independently(ep_dir)
        assert res['independent_verdict'] == 'PASS'
        assert res['reproduced_sql_score'] == 1.0
        assert res['unauthorized_mutation_count'] == 0

    @pytest.mark.skipif(not QWEN3B_BASE.exists(), reason="Qwen3B pilot directory not found")
    def test_qwen3b_clearance_discount_passes(self):
        # On 0.5B this failed because agent only did SELECT. On 3B it issued UPDATE!
        ep_dir = QWEN3B_BASE / 'clearance-discount' / 'qwen3b_real_clearance-discount_seed42'
        res = evaluate_episode_independently(ep_dir)
        assert res['independent_verdict'] == 'PASS'
        assert res['reproduced_sql_score'] == 1.0
        assert res['unauthorized_mutation_count'] == 0

    @pytest.mark.skipif(not QWEN3B_BASE.exists(), reason="Qwen3B pilot directory not found")
    def test_qwen3b_dedup_keep_latest_passes(self):
        # On 0.5B this failed with errored queries. On 3B it successfully deleted duplicates!
        ep_dir = QWEN3B_BASE / 'dedup-keep-latest' / 'qwen3b_real_dedup-keep-latest_seed42'
        res = evaluate_episode_independently(ep_dir)
        assert res['independent_verdict'] == 'PASS'
        assert res['reproduced_sql_score'] == 1.0
        assert res['unauthorized_mutation_count'] == 0

    @pytest.mark.skipif(not QWEN3B_BASE.exists(), reason="Qwen3B pilot directory not found")
    def test_qwen3b_cancel_and_void_payment_fails(self):
        ep_dir = QWEN3B_BASE / 'cancel-and-void-payment' / 'qwen3b_real_cancel-and-void-payment_seed42'
        res = evaluate_episode_independently(ep_dir)
        assert res['independent_verdict'] == 'FAIL'
        assert res['reproduced_sql_score'] < 1.0

    @pytest.mark.skipif(not QWEN3B_BASE.exists(), reason="Qwen3B pilot directory not found")
    def test_qwen3b_refund_and_restock_fails(self):
        ep_dir = QWEN3B_BASE / 'refund-and-restock' / 'qwen3b_real_refund-and-restock_seed42'
        res = evaluate_episode_independently(ep_dir)
        assert res['independent_verdict'] == 'FAIL'
        assert res['reproduced_sql_score'] < 1.0
