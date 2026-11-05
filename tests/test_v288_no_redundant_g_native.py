"""P3-EO: a supplied same-season budget must not implicitly launch G Native.

This is a control-flow test before any Native or network call. It does not
certify the budget source or approve a new-season environment.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from runner import v216_environment_build_coordinator as build


class _ReachedGStage(Exception):
    pass


class GNativeExplicitChoiceTests(TestCase):
    def test_existing_budget_suppresses_implicit_native_but_preserves_opt_in(self):
        # Exact source validation still belongs to the existing preflight.
        # A bad receipt will be rejected there, never granted G approval.
        supplied = {"components": {"G": {"rating": 2850}}}
        cases = (
            ("existing_source_default", supplied, None, False),
            ("existing_source_explicit_G", supplied, True, True),
            ("no_source_legacy_default", None, None, True),
            ("no_source_explicit_off", None, False, False),
        )
        for name, budget, override, want_binary in cases:
            with self.subTest(name=name), TemporaryDirectory() as td:
                source = {
                    "schema": "v216_fresh_source_stage_v1",
                    "source_stage": {"status": "REUSED_VERIFIED", "reused": True},
                    "environment_installed": False, "environment_ready": False,
                    "native_calls": 0,
                    **{k: None for k in ("G", "J", "F", "O", "B", "T")},
                }
                inputs = {
                    "expected_game_build": "12.1.5.70575",
                    "representative_request": {
                        "class": "mage", "spec": "frost", "target_ilevel": 334
                    },
                    "g_probe_character": None,
                    "simc_revision_hint": None,
                }
                if budget is not None:
                    inputs["same_build_budget_evidence"] = budget
                if override is not None:
                    inputs["auto_native_G_requested"] = override
                seen = []
                marker = object()

                def capture(**kwargs):
                    seen.append(kwargs["binary"])
                    raise _ReachedGStage()

                with mock.patch.object(
                    build, "collect_wago_new_season_source",
                    return_value=source
                ) as collector, mock.patch.object(
                    build.zero_history_G_native, "collect",
                    side_effect=capture
                ):
                    with self.assertRaises(_ReachedGStage):
                        build.build_environment(
                            sessions_root=Path(td) / "sessions",
                            session_folder=None, user=None, binary=marker,
                            revision=None, static_cache=None,
                            source_catalog_path=None, bootstrap_result=None,
                            fresh_collection_inputs=inputs
                        )
                self.assertEqual(seen, [marker if want_binary else None])
                self.assertEqual(collector.call_count, 1)
                self.assertNotIn(
                    "same_build_budget_evidence", collector.call_args.kwargs
                )
                self.assertFalse((Path(td) / "sessions").exists())
