from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
WEB_SEARCH_ROOT = SKILL_ROOT.parent / "web-search"
sys.path.insert(0, str(SCRIPTS))

import compose_demo_spec  # noqa: E402


class ComposeDemoSpecTests(unittest.TestCase):
    def test_deep_merge_replaces_arrays_and_deletes_keys(self):
        base = {
            "a": {"keep": 1, "remove": 2},
            "formula": {"old": 1},
            "items": [1, 2],
        }
        overlay = {
            "a": {"remove": {"$delete": True}, "added": 3},
            "formula": {"$replace": {"new": 2}},
            "items": [9],
        }
        self.assertEqual(
            compose_demo_spec.deep_merge(base, overlay),
            {
                "a": {"keep": 1, "added": 3},
                "formula": {"new": 2},
                "items": [9],
            },
        )

    def test_pack_cannot_define_customer_design(self):
        document = {
            "_pack": {"id": "bad", "name": "Bad Pack"},
            "spec": {"design": {"theme": "light"}},
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_pack(document, Path("bad-pack.json"))

    def test_pack_cannot_replace_root_with_customer_sections(self):
        document = {
            "_pack": {"id": "bad", "name": "Bad Pack"},
            "spec": {
                "$replace": {
                    "meta": {"customer": "Injected"},
                    "design": {"theme": "light"},
                    "story": {"frame": "Injected"},
                }
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_pack(document, Path("bad-pack.json"))

    def test_customer_overlay_must_not_define_design(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": ["https://example.com/a", "https://example.com/b"],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
                "design": {"theme": "light"},
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_customer_required_paths_replace_instead_of_merge(self):
        base = {
            "meta": {"customer": "Base"},
            "design": {"theme": "dark-dimmed"},
            "story": {"frame": "Base"},
            "operations": {
                "hero": {
                    "title": "Base title",
                    "subtitle": "Base subtitle",
                    "icon": "◇",
                }
            },
        }
        customer = {
            "meta": {"customer": "Customer"},
            "story": {"frame": "Customer"},
            "operations": {
                "hero": {
                    "$replace": {
                        "title": "Customer title",
                        "subtitle": "Customer subtitle",
                        "icon": "◇",
                    }
                }
            },
        }
        result = compose_demo_spec.apply_customer_layer(
            base,
            customer,
            ["operations.hero"],
        )
        self.assertEqual(
            result["operations"]["hero"],
            {
                "title": "Customer title",
                "subtitle": "Customer subtitle",
                "icon": "◇",
            },
        )
        self.assertEqual(result["design"], {"theme": "dark-dimmed"})

    def test_apply_customer_layer_rejects_design_defensively(self):
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.apply_customer_layer(
                {
                    "meta": {},
                    "design": {"theme": "dark-dimmed"},
                    "story": {},
                },
                {
                    "meta": {},
                    "story": {},
                    "design": {"theme": "light"},
                },
                [],
            )

    def test_stale_research_override_is_repository_scoped(self):
        self.assertTrue(
            compose_demo_spec.stale_research_allowed(
                SKILL_ROOT / "examples" / "overlay.json",
                SKILL_ROOT,
            )
        )
        self.assertFalse(
            compose_demo_spec.stale_research_allowed(
                SKILL_ROOT.parent / "customer-overlay.json",
                SKILL_ROOT,
            )
        )

    def test_stale_override_does_not_allow_future_research(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2999-01-01T00:00:00Z",
                    "sourceUrls": ["https://example.com/a", "https://example.com/b"],
                }
            },
            "spec": {"meta": {}, "story": {}},
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_ipv6_source_url_is_canonicalized_safely(self):
        self.assertEqual(
            compose_demo_spec.canonical_source_url("https://[2001:db8::1]:443/a#fragment"),
            "https://[2001:db8::1]/a",
        )

    def test_output_paths_require_safe_extensions_and_no_aliases(self):
        inputs = {SKILL_ROOT / "examples" / "base.json"}
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_output_paths(
                SKILL_ROOT / "work" / "spec.txt", None, inputs
            )
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_output_paths(
                SKILL_ROOT / "work" / "spec.json",
                SKILL_ROOT / "work" / "SPEC.JSON",
                inputs,
            )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "base.json"
            output = Path(directory) / "output.json"
            source.write_text("{}", encoding="utf-8")
            output.hardlink_to(source)
            with self.assertRaises(compose_demo_spec.ComposeError):
                compose_demo_spec.validate_output_paths(
                    output, Path(directory) / "demo.html", {source}
                )

    def test_forbidden_acronym_uses_token_boundaries(self):
        compose_demo_spec.check_output_leaks(
            {"text": "Spinning reserve is stable."},
            ["SPI"],
        )

    def test_forbidden_term_detects_html_entity_encoding(self):
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.check_output_leaks(
                {"text": "Con&#116;oso"},
                ["Contoso"],
            )

    def test_forbidden_term_detects_inline_tag_splitting(self):
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.check_output_leaks(
                {"text": "Con<b>to</b>so"},
                ["Contoso"],
            )

    def test_research_sources_reject_non_string_values(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": ["https://example.com/a", {}],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_research_sources_reject_invalid_port_and_fragment_duplicates(self):
        base_document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": [
                        "https://example.com:bad/a",
                        "https://example.org/b",
                    ],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                base_document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

        base_document["_customer"]["research"]["sourceUrls"] = [
            "https://example.com/page#one",
            "https://example.com/page#two",
        ]
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                base_document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_fact_ledger_handoff_builds_research_metadata(self):
        ledger = json.loads(
            (WEB_SEARCH_ROOT / "examples" / "fact-ledger.example.json").read_text(
                encoding="utf-8"
            )
        )
        research, provenance = compose_demo_spec.fact_ledger_research(ledger)
        self.assertEqual(research["mode"], "live")
        self.assertEqual(research["ledgerIds"], ["F-001", "F-002"])
        self.assertEqual(len(research["sourceUrls"]), 2)
        self.assertEqual(len(provenance["sources"]), 2)
        self.assertEqual(provenance["sources"][0]["ledgerIds"], ["F-001"])

        inference = dict(ledger["facts"][0])
        inference["id"] = "I-001"
        inference["type"] = "Inference"
        ledger["facts"].append(inference)
        _, provenance = compose_demo_spec.fact_ledger_research(ledger)
        self.assertEqual(
            provenance["ledgerIds"], ["F-001", "F-002", "I-001"]
        )

        ledger["facts"] = ledger["facts"][:1]
        with self.assertRaisesRegex(
            compose_demo_spec.ComposeError, "at least two unique"
        ):
            compose_demo_spec.fact_ledger_research(ledger)

    def test_fact_ledger_rejects_schema_invalid_values(self):
        ledger = json.loads(
            (WEB_SEARCH_ROOT / "examples" / "fact-ledger.example.json").read_text(
                encoding="utf-8"
            )
        )
        ledger["schemaVersion"] = True
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.fact_ledger_research(ledger)

        ledger["schemaVersion"] = 1
        ledger["facts"][0]["accessed"] = "20260723"
        with self.assertRaisesRegex(
            compose_demo_spec.ComposeError, "YYYY-MM-DD"
        ):
            compose_demo_spec.fact_ledger_research(ledger)

        ledger["facts"][0]["accessed"] = "2026-07-23"
        ledger["facts"][0]["publishedOrUpdated"] = "not-a-date"
        with self.assertRaisesRegex(
            compose_demo_spec.ComposeError, "publishedOrUpdated"
        ):
            compose_demo_spec.fact_ledger_research(ledger)

        ledger["facts"][0]["publishedOrUpdated"] = "확인 불가"
        ledger["unexpected"] = True
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.fact_ledger_research(ledger)

    def test_fact_ledger_mismatch_with_overlay_is_rejected(self):
        ledger = json.loads(
            (WEB_SEARCH_ROOT / "examples" / "fact-ledger.example.json").read_text(
                encoding="utf-8"
            )
        )
        customer = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": ledger["checkedAt"],
                    "sourceUrls": [
                        "https://example.com/a",
                        "https://example.com/b",
                    ],
                }
            },
            "spec": {},
        }
        with self.assertRaisesRegex(
            compose_demo_spec.ComposeError, "does not match"
        ):
            compose_demo_spec.apply_fact_ledger(customer, ledger)

    def test_fact_ledger_composes_into_final_spec_and_html(self):
        with tempfile.TemporaryDirectory(prefix="demo-ledger-test-") as temp_dir:
            temp = Path(temp_dir)
            ledger = json.loads(
                (WEB_SEARCH_ROOT / "examples" / "fact-ledger.example.json").read_text(
                    encoding="utf-8"
                )
            )
            now = datetime.now().astimezone()
            ledger["checkedAt"] = now.isoformat()
            for fact in ledger["facts"]:
                fact["accessed"] = now.date().isoformat()
            ledger_path = temp / "fact-ledger.json"
            ledger_path.write_text(
                json.dumps(ledger, ensure_ascii=False),
                encoding="utf-8",
            )

            customer = json.loads(
                (
                    SKILL_ROOT
                    / "examples"
                    / "renewable-energy.customer-overlay.example.json"
                ).read_text(encoding="utf-8")
            )
            customer["_customer"].pop("research")
            customer_path = temp / "customer-overlay.json"
            customer_path.write_text(
                json.dumps(customer, ensure_ascii=False),
                encoding="utf-8",
            )
            spec_output = temp / "demo-spec.json"
            html_output = temp / "demo.html"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPTS / "compose_demo_spec.py"),
                    "--base",
                    str(SKILL_ROOT / "examples" / "precision-manufacturing.example.json"),
                    "--pack",
                    str(SKILL_ROOT / "packs" / "renewable-energy-holdings.pack.json"),
                    "--customer",
                    str(customer_path),
                    "--fact-ledger",
                    str(ledger_path),
                    "--output",
                    str(spec_output),
                    "--html-output",
                    str(html_output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_output.read_text(encoding="utf-8"))
            sources = spec["meta"]["research"]["sources"]
            self.assertEqual(len(sources), 2)
            self.assertEqual(
                spec["meta"]["research"]["ledgerIds"], ["F-001", "F-002"]
            )
            self.assertEqual(sources[0]["ledgerIds"], ["F-001"])
            html = html_output.read_text(encoding="utf-8")
            self.assertIn("https://learn.microsoft.com/training/support/mcp", html)
            self.assertIn('"ledgerIds":["F-001"]', html)

    def test_repository_example_composes_and_renders(self):
        with tempfile.TemporaryDirectory(prefix="demo-compose-test-") as temp_dir:
            temp = Path(temp_dir)
            spec_output = temp / "demo-spec.json"
            html_output = temp / "demo.html"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPTS / "compose_demo_spec.py"),
                    "--base",
                    str(SKILL_ROOT / "examples" / "precision-manufacturing.example.json"),
                    "--pack",
                    str(SKILL_ROOT / "packs" / "renewable-energy-holdings.pack.json"),
                    "--customer",
                    str(SKILL_ROOT / "examples" / "renewable-energy.customer-overlay.example.json"),
                    "--output",
                    str(spec_output),
                    "--html-output",
                    str(html_output),
                    "--allow-stale-research",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_output.read_text(encoding="utf-8"))
            self.assertEqual(spec["meta"]["customer"], "Northstar Energy Holdings")
            self.assertEqual(spec["design"]["archetype"], "trusted-executive")
            self.assertEqual(len(spec["meta"]["research"]["sources"]), 2)
            self.assertNotIn("Contoso", spec_output.read_text(encoding="utf-8"))
            self.assertIn("에너지", spec["foundry"]["placeholder"])
            self.assertNotIn("품질·공정", spec["foundry"]["placeholder"])
            lint_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "lint_spec.py"), str(spec_output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(lint_result.returncode, 0, lint_result.stdout + lint_result.stderr)
            html = html_output.read_text(encoding="utf-8")
            self.assertIn("Northstar Nexus", html)
            self.assertIn("재생에너지 발전", html)
            self.assertIn("통합 운영 현황", html)


if __name__ == "__main__":
    unittest.main()
