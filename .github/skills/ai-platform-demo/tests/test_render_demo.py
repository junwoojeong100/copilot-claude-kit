from __future__ import annotations

import copy
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import render_demo  # noqa: E402


BASE = json.loads(
    (SKILL_ROOT / "examples" / "precision-manufacturing.example.json").read_text(
        encoding="utf-8"
    )
)


class RenderDemoTests(unittest.TestCase):
    def invalid(self, mutate):
        spec = copy.deepcopy(BASE)
        mutate(spec)
        spec = render_demo.sanitize_rich_fields(spec)
        with self.assertRaises(render_demo.SpecError):
            render_demo.validate_spec(spec)

    def test_fixed_design_cannot_be_overridden(self):
        self.invalid(lambda spec: spec["design"].update(theme="light"))
        self.invalid(lambda spec: spec["design"]["tokens"].update(brand="#000"))
        self.invalid(
            lambda spec: spec["design"].update(
                conceptWords=["custom", "customer", "theme"]
            )
        )
        self.invalid(lambda spec: spec["design"].update(visualMetaphor="custom"))

    def test_selector_ids_and_semantic_colors_are_restricted(self):
        self.invalid(
            lambda spec: spec["simulator"]["inputs"][0].update(id='bad"] input')
        )
        self.invalid(
            lambda spec: spec["dashboard"]["kpis"][0].update(
                color='var(--brand);background:url("https://example.invalid")'
            )
        )
        self.invalid(lambda spec: spec["meta"].update(language="en-12"))

    def test_common_language_tags_are_supported(self):
        for language in ("ko", "en-US", "zh-Hant-TW", "de-CH-1901"):
            spec = copy.deepcopy(BASE)
            spec["meta"]["language"] = language
            spec = render_demo.sanitize_rich_fields(spec)
            render_demo.validate_spec(spec)

    def test_route_scope_supports_exactly_eight_menus(self):
        spec = copy.deepcopy(BASE)
        spec["story"]["routeScope"] = render_demo.ROUTE_IDS
        render_demo.validate_spec(render_demo.sanitize_rich_fields(spec))

    def test_route_scope_requires_all_routes_in_canonical_order(self):
        self.invalid(
            lambda spec: spec["story"].update(
                routeScope=[
                    "operations",
                    "dashboard",
                    "simulator",
                    "improvement",
                    "finance",
                    "github",
                    "foundry",
                    "appPlatform",
                ]
            )
        )
        self.invalid(
            lambda spec: spec["story"].update(
                routeScope=render_demo.ROUTE_IDS[:-1]
            )
        )

    def test_guided_journey_requires_matching_bridges_and_default(self):
        self.invalid(
            lambda spec: spec["story"]["guidedJourneys"][0]["bridges"].pop()
        )
        self.invalid(
            lambda spec: spec["story"].update(defaultJourneyId="missing")
        )

    def test_scenario_trace_connects_business_to_platform_chain(self):
        self.invalid(
            lambda spec: spec["story"]["scenarioTrace"]["steps"][2].update(
                route="appPlatform"
            )
        )

    def test_dashboard_requires_action_to_another_route(self):
        self.invalid(
            lambda spec: spec["dashboard"]["primaryAction"].update(
                targetRoute="dashboard"
            )
        )

    def test_service_sales_contract_requires_governance_coverage(self):
        self.invalid(
            lambda spec: spec["foundry"]["sales"].update(
                controlEvidence=[
                    item
                    for item in spec["foundry"]["sales"]["controlEvidence"]
                    if item["service"] != "Microsoft Purview"
                ]
            )
        )
        self.invalid(
            lambda spec: spec["github"]["sales"]["businessKpis"].pop()
        )

    def test_research_provenance_requires_timezone_timestamp(self):
        valid_research = {
            "checkedAt": "2026-07-23T10:30:00+09:00",
            "sources": [
                {"url": "https://example.com/a"},
                {"url": "https://example.com/b"},
            ],
        }
        spec = copy.deepcopy(BASE)
        spec["meta"]["research"] = valid_research
        render_demo.validate_spec(render_demo.sanitize_rich_fields(spec))

        self.invalid(
            lambda invalid_spec: invalid_spec["meta"].update(
                research={**valid_research, "checkedAt": "not-a-date"}
            )
        )
        self.invalid(
            lambda invalid_spec: invalid_spec["meta"].update(
                research={
                    **valid_research,
                    "checkedAt": "2026-07-23T10:30:00",
                }
            )
        )
        self.invalid(
            lambda invalid_spec: invalid_spec["meta"].update(
                research={
                    **valid_research,
                    "sources": [
                        {"url": "https://example.com/source#one"},
                        {"url": "https://EXAMPLE.com:443/source#two"},
                    ],
                }
            )
        )
        self.invalid(lambda invalid_spec: invalid_spec["meta"].pop("research"))

    def test_table_shape_must_match_headers(self):
        self.invalid(
            lambda spec: spec["dashboard"]["table"]["rows"][0]["cells"].append(
                "extra"
            )
        )

    def test_simulator_relationships_are_complete(self):
        self.invalid(
            lambda spec: spec["simulator"]["secondary"][0]["weights"].pop(
                spec["simulator"]["inputs"][0]["id"]
            )
        )
        self.invalid(
            lambda spec: spec["simulator"]["recommendations"].insert(
                0,
                spec["simulator"]["recommendations"].pop(),
            )
        )

    def test_action_duration_is_bounded_for_qa(self):
        self.invalid(
            lambda spec: spec["operations"]["action"].update(durationMs=15001)
        )

    def test_app_platform_initial_score_matches_visible_card(self):
        self.invalid(
            lambda spec: spec["appPlatform"]["cards"][0].update(value="91.0")
        )

    def test_app_platform_evaluation_must_change_numerically(self):
        self.invalid(
            lambda spec: spec["appPlatform"]["evaluation"].update(
                initialScore=90.0,
                finalScore=90,
            )
        )

    def test_app_platform_requires_unresolved_readiness_gap(self):
        self.invalid(
            lambda spec: [
                gap["status"].update(tone="success")
                for gap in spec["appPlatform"]["evaluation"]["gaps"]
            ]
        )

    def test_equivalent_app_platform_score_formats_are_accepted(self):
        spec = copy.deepcopy(BASE)
        spec["appPlatform"]["evaluation"]["initialScore"] = 90.0
        spec["appPlatform"]["cards"][0]["value"] = "90"
        spec = render_demo.sanitize_rich_fields(spec)
        render_demo.validate_spec(spec)

    def test_github_requires_autonomous_and_high_risk_paths(self):
        self.invalid(
            lambda spec: [
                issue.update(highRisk=True) for issue in spec["github"]["issues"]
            ]
        )
        self.invalid(
            lambda spec: [
                issue.update(highRisk=False) for issue in spec["github"]["issues"]
            ]
        )

    def test_rich_text_rejects_active_content(self):
        spec = copy.deepcopy(BASE)
        spec["foundry"]["profiles"][0]["qa"][0]["answer"] = (
            '<img src=x onerror="alert(1)">'
        )
        with self.assertRaises(render_demo.SpecError):
            render_demo.sanitize_rich_fields(spec)

    def test_script_json_escapes_end_tags_and_line_separators(self):
        encoded = render_demo.safe_json_for_script(
            {"value": "</script>\u2028next\u2029"}
        )
        self.assertNotIn("</script>", encoded)
        self.assertIn("<\\/script>", encoded)
        self.assertIn("\\u2028", encoded)
        self.assertIn("\\u2029", encoded)

    def test_repository_example_renders_self_contained_runtime(self):
        spec = render_demo.sanitize_rich_fields(BASE)
        render_demo.validate_spec(spec)
        html = render_demo.render(spec, SKILL_ROOT / "runtime")
        css = (SKILL_ROOT / "runtime" / "runtime.css").read_text(encoding="utf-8")
        canvas = re.search(r"--canvas:\s*(#[0-9a-f]{6})\s*;", css, re.I).group(1)
        self.assertIn('<script id="demo-spec" type="application/json">', html)
        self.assertNotIn("<script src=", html)
        self.assertIn("● 시연 데이터", html)
        self.assertIn("통합 운영 현황", html)
        self.assertIn("임원용 AI 운영 데모", html)
        self.assertIn('<meta name="color-scheme" content="dark">', html)
        self.assertIn(f'<meta name="theme-color" content="{canvas}">', html)
        self.assertIn("color-scheme:dark", html)
        self.assertIn("document.body.dataset.theme = 'dark-dimmed'", html)
        self.assertIn('id="journeyBar"', html)
        self.assertIn("guidedJourneys", html)
        self.assertIn("planRemediation", html)
        self.assertIn("evalProjectedScore", html)
        self.assertIn("assessmentPending", html)
        self.assertIn("businessScenarioTraceHtml", html)
        self.assertNotIn("color-scheme:light", html)
        runtime = (SKILL_ROOT / "runtime" / "runtime.js").read_text(encoding="utf-8")
        self.assertIn("escapeHtml(data.margin.unit)", runtime)
        self.assertIn("data.composition.centerSegment ?? 1", runtime)

    def test_schema_enforces_canonical_route_scope_order(self):
        schema = json.loads(
            (SKILL_ROOT / "schema" / "demo-spec.schema.json").read_text(
                encoding="utf-8"
            )
        )
        route_scope = schema["properties"]["story"]["properties"]["routeScope"]
        self.assertEqual(
            [item["const"] for item in route_scope["prefixItems"]],
            render_demo.ROUTE_IDS,
        )
        self.assertFalse(route_scope["items"])
        improvement_contract = schema["properties"]["improvement"]["allOf"][1]
        github_contract = schema["properties"]["github"]["allOf"][1]
        self.assertNotIn("sales", improvement_contract["required"])
        self.assertIn("sales", github_contract["required"])

    def test_english_runtime_copy_remains_available(self):
        spec = copy.deepcopy(BASE)
        spec["meta"]["language"] = "en"
        html = render_demo.render(spec, SKILL_ROOT / "runtime")
        self.assertIn("● DEMO DATA", html)
        self.assertIn("Operations Intelligence", html)
        self.assertIn("Executive AI Operations Demo", html)

    def test_runtime_owned_hero_html_is_rejected(self):
        self.invalid(
            lambda spec: spec["dashboard"]["hero"].update(
                actionHtml="<iframe src=https://example.invalid>"
            )
        )

    def test_soft_dark_small_text_contrast(self):
        css = (SKILL_ROOT / "runtime" / "runtime.css").read_text(encoding="utf-8")
        tokens = dict(re.findall(r"--([a-z-]+):(#[0-9a-f]{6})", css, re.I))
        step_rule = re.search(r"\.step\{([^}]*)\}", css)
        self.assertIsNotNone(step_rule)
        self.assertNotRegex(step_rule.group(1), r"opacity:\s*0?\.[0-9]+")

        def rgb(value):
            return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))

        def mix(foreground, background, alpha):
            return tuple(
                round(front * alpha + back * (1 - alpha))
                for front, back in zip(rgb(foreground), rgb(background))
            )

        def luminance(value):
            channels = [channel / 255 for channel in value]
            channels = [
                channel / 12.92
                if channel <= 0.04045
                else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return (
                0.2126 * channels[0]
                + 0.7152 * channels[1]
                + 0.0722 * channels[2]
            )

        def contrast(foreground, background):
            lighter, darker = sorted(
                (luminance(rgb(foreground)), luminance(background)),
                reverse=True,
            )
            return (lighter + 0.05) / (darker + 0.05)

        for token, alpha in {
            "info": 0.11,
            "success": 0.12,
            "warning": 0.11,
            "danger": 0.11,
            "violet": 0.11,
        }.items():
            background = mix(tokens[token], tokens["surface"], alpha)
            self.assertGreaterEqual(contrast(tokens[token], background), 4.5)

        tinted_surface = mix(tokens["brand"], tokens["surface-alt"], 0.04)
        self.assertGreaterEqual(contrast(tokens["ink-faint"], tinted_surface), 4.5)

    def test_output_collision_detects_hardlinks_and_case_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "spec.json"
            alias = Path(directory) / "alias.json"
            source.write_text("{}", encoding="utf-8")
            os.link(source, alias)
            self.assertTrue(render_demo.paths_collide(source, alias))
            self.assertTrue(
                render_demo.paths_collide(
                    Path(directory) / "Output.HTML",
                    Path(directory) / "output.html",
                )
            )
            runtime = Path(directory) / "runtime"
            runtime.mkdir()
            for name in render_demo.RUNTIME_ASSET_NAMES:
                (runtime / name).write_text(name, encoding="utf-8")
            output = Path(directory) / "demo.html"
            output.hardlink_to(runtime / "runtime.js")
            self.assertTrue(
                any(
                    render_demo.paths_collide(output, path)
                    for path in render_demo.runtime_input_paths(runtime)
                )
            )


if __name__ == "__main__":
    unittest.main()
