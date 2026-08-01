from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "research_scenarios.json"
ADAPTIVE_SKILL = SKILL.parents[1] / "adaptive-presentation" / "SKILL.md"
DEMO_SKILL = SKILL.parents[1] / "ai-platform-demo" / "SKILL.md"
ADAPTIVE_FULL_OPTIMIZED = (
    ADAPTIVE_SKILL.parent / "reference" / "full-optimized.md"
)
ADAPTIVE_VERIFICATION = ADAPTIVE_SKILL.parent / "reference" / "verification.md"
ADAPTIVE_DECK_SPEC = ADAPTIVE_SKILL.parent / "reference" / "deck-spec.md"
ADAPTIVE_DECK_SCHEMA = ADAPTIVE_SKILL.parent / "schema" / "deck-spec.schema.json"
ADAPTIVE_EXCEPTION_SCHEMA = (
    ADAPTIVE_SKILL.parent / "schema" / "qa-exceptions.schema.json"
)
ADAPTIVE_VISUAL_SCHEMA = (
    ADAPTIVE_SKILL.parent / "schema" / "visual-review.schema.json"
)
DEMO_FULL_OPTIMIZED = DEMO_SKILL.parent / "reference" / "full-optimized.md"
REPOSITORY_ROOT = SKILL.parents[3]
COPILOT_INSTRUCTIONS = REPOSITORY_ROOT / ".github" / "copilot-instructions.md"
README = REPOSITORY_ROOT / "README.md"
CLI_MCP_CONFIG = REPOSITORY_ROOT / ".github" / "mcp.json"
VSCODE_MCP_CONFIG = REPOSITORY_ROOT / ".vscode" / "mcp.json"
FACT_LEDGER_SCHEMA = SKILL.parent / "schema" / "fact-ledger.schema.json"
FACT_LEDGER_EXAMPLE = SKILL.parent / "examples" / "fact-ledger.example.json"
FACT_LEDGER_VALIDATOR = SKILL.parent / "scripts" / "validate_fact_ledger.py"
sys.path.insert(0, str(FACT_LEDGER_VALIDATOR.parent))
import validate_fact_ledger  # noqa: E402


class WebSearchSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        frontmatter = cls.skill.split("---", 2)[1]
        description_line = next(
            line for line in frontmatter.splitlines() if line.startswith("description:")
        )
        cls.description = description_line.split(":", 1)[1].strip().strip('"')

    def test_search_routing_prefers_shortest_official_path(self):
        canonical = self.skill.index("알려진 canonical URL·공식 index")
        domain_search = self.skill.index("도메인 공식 검색")
        web_search = self.skill.index("general web search tool")
        research_agent = self.skill.index(
            "여러 독립 조사 축을 병렬 수집할 때만 `/research`"
        )

        self.assertLess(canonical, domain_search)
        self.assertLess(domain_search, web_search)
        self.assertLess(web_search, research_agent)
        self.assertIn("GitHub Copilot CLI와 VS Code Copilot Chat/Agent", self.skill)

    def test_public_serp_scraping_is_forbidden(self):
        self.assertIn("공개 검색 결과 페이지(SERP)", self.skill)
        self.assertIn("직접 조회하지 않는다", self.skill)
        self.assertNotIn("https://www.google.com/search", self.skill)
        self.assertNotIn("https://html.duckduckgo.com", self.skill)
        self.assertNotIn("DuckDuckGo HTML로 전환", self.skill)

    def test_search_results_require_canonical_source_verification(self):
        self.assertIn("검색 결과·snippet·AI 요약은 URL 발견용이며 근거가 아니다", self.skill)
        self.assertIn("canonical", self.skill)

    def test_untrusted_web_content_cannot_direct_agent_actions(self):
        self.assertIn("untrusted data", self.skill)
        self.assertIn("prompt injection", self.skill)
        self.assertIn("도구 실행·파일 변경·로그인·업로드·secret 요청", self.skill)

    def test_foundational_research_has_a_fact_ledger_contract(self):
        self.assertIn("Research Brief", self.skill)
        self.assertIn("Fact Ledger 계약", self.skill)

        for field in ("ID", "Type", "Claim", "Evidence", "Sources/Basis", "Scope/status", "Confidence", "Status"):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)

        self.assertIn("`Fact`·`Inference`·`Assumption`", self.skill)
        self.assertIn("fact-ledger.md", self.skill)
        self.assertIn("validate_fact_ledger.py", self.skill)
        self.assertIn("locator", self.skill)
        self.assertIn("basisIds", self.skill)
        self.assertIn("assumptionOwner", self.skill)
        self.assertIn("validationNeeded", self.skill)
        self.assertIn("`High`", self.skill)
        self.assertIn("`Medium`", self.skill)
        self.assertIn("`Low`", self.skill)

        schema = json.loads(FACT_LEDGER_SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(FACT_LEDGER_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(example["schemaVersion"], 1)
        self.assertGreaterEqual(len(example["facts"]), 4)
        mutual_exclusions = {
            tuple(rule["required"])
            for rule in schema["$defs"]["ledgerEntry"]["allOf"][1]["not"]["anyOf"]
        }
        self.assertEqual(
            mutual_exclusions,
            {
                ("sources", "source"),
                ("sources", "publisher"),
                ("sources", "publishedOrUpdated"),
                ("sources", "accessed"),
            },
        )
        self.assertTrue(FACT_LEDGER_VALIDATOR.is_file())
        normalized = validate_fact_ledger.validate_ledger(example)
        self.assertEqual(len(normalized["facts"]), len(example["facts"]))

    def test_research_has_explicit_completion_criteria(self):
        self.assertIn("## 완료 판정", self.skill)
        self.assertIn("필수 조사 축마다", self.skill)
        self.assertIn("결론 영향 사실은 canonical 원문", self.skill)
        self.assertIn("source budget", self.skill)
        self.assertIn("축별 두 가지 retrieval 전략", self.skill)

    def test_freshness_dimensions_are_explicit(self):
        self.assertIn("가격은 지역·통화·기준일", self.skill)
        self.assertIn("제품·버전·지역·GA/Preview·확인 시각", self.skill)
        self.assertIn("관할·시행일", self.skill)
        self.assertIn("기간·단위·표본·방법론", self.skill)

    def test_skill_triggers_include_foundational_research(self):
        self.assertIn("기초자료 조사", self.description)
        self.assertIn("자료 검색/수집", self.description)
        self.assertIn("고객/기업 조사", self.description)
        self.assertIn("시장 규모", self.description)

    def test_skill_contracts_are_concise_and_bounded(self):
        limits = {
            SKILL: 100,
            ADAPTIVE_SKILL: 120,
            DEMO_SKILL: 150,
        }
        for skill, limit in limits.items():
            content = skill.read_text(encoding="utf-8")
            with self.subTest(skill=skill.parent.name):
                self.assertLessEqual(len(content.splitlines()), limit)
                self.assertIn("NOT WHEN:", content.split("---", 2)[1])
                workflow_headings = re.findall(
                    r"^## .*워크플로.*$", content, flags=re.MULTILINE
                )
                self.assertEqual(len(workflow_headings), 1)

    def test_downstream_skills_delegate_search_backend_selection(self):
        for skill, guide in (
            (ADAPTIVE_SKILL, ADAPTIVE_FULL_OPTIMIZED),
            (DEMO_SKILL, DEMO_FULL_OPTIMIZED),
        ):
            skill_content = skill.read_text(encoding="utf-8")
            guide_content = guide.read_text(encoding="utf-8")
            combined = f"{skill_content}\n{guide_content}"
            with self.subTest(skill=skill.parent.name):
                self.assertIn("검색 backend", skill_content)
                self.assertIn("`web-search`", skill_content)
                self.assertNotIn("Research agent", combined)
                self.assertNotIn("/research", combined)
                self.assertNotIn("/fleet", combined)

    def test_demo_story_starts_from_customer_research(self):
        content = DEMO_SKILL.read_text(encoding="utf-8")
        self.assertIn("조사로 확인한 고객 과제와 사업 언어에서", content)
        self.assertNotIn("Satya Nadella", content)
        self.assertNotIn("frontier ecosystem", content)
        self.assertNotIn("x.com/satyanadella", content)

    def test_performance_metrics_are_optional(self):
        for guide in (ADAPTIVE_FULL_OPTIMIZED, DEMO_FULL_OPTIMIZED):
            content = guide.read_text(encoding="utf-8")
            with self.subTest(skill=guide.parents[1].name):
                self.assertIn("선택적 시간 측정", content)
                self.assertIn("완료 조건", content)

    def test_downstream_skills_keep_mapping_outside_common_ledger(self):
        for downstream, mapping_contract in (
            (ADAPTIVE_SKILL, "storyline과 deck spec"),
            (DEMO_SKILL, "Customer Overlay와 demo spec"),
        ):
            content = downstream.read_text(encoding="utf-8")
            with self.subTest(skill=downstream.parent.name):
                self.assertIn("공통 Fact Ledger 계약", content)
                self.assertIn(mapping_contract, content)
                self.assertIn("Ledger를 확장하지 않고", content)
                self.assertNotIn("| ID | Type | Claim |", content)

    def test_factcheck_policy_is_risk_scoped(self):
        content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertIn("최신성·수치·논쟁성·의사결정 영향", content)
        self.assertIn("단순·저위험 답변에는 표를 붙이지 않는다", content)
        self.assertNotIn("팩트체크 (항상)", content)

    def test_xhigh_execution_contract_is_bounded_and_read_only_safe(self):
        content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertIn("위험과 복잡도에 비례한 사고", content)
        self.assertIn("질문·설명·검토 요청은 read-only", content)
        self.assertIn("acceptance criteria", content)
        self.assertIn("validator·schema", content)
        self.assertIn("사용자가 요청한 경우에만 수행", content)

    def test_demo_language_and_route_scope_are_explicit(self):
        content = DEMO_SKILL.read_text(encoding="utf-8")
        self.assertIn("지정 언어를 준수", content)
        self.assertIn("한국어일 때만", content)
        self.assertIn("`story.routeScope`", content)
        self.assertIn("총 5~8개를 canonical 순서로 선택", content)
        self.assertIn("`design.tokens.brand/accent`", content)

    def test_adaptive_skill_exposes_canonical_session_and_qa_contract(self):
        content = ADAPTIVE_SKILL.read_text(encoding="utf-8")
        verification = ADAPTIVE_VERIFICATION.read_text(encoding="utf-8")
        self.assertIn("client가 제공한 artifact 디렉터리", content)
        self.assertIn("scripts/verify_deck.py", content)
        self.assertIn("--deck-spec", content)
        self.assertIn("[Fact ID]", content)
        self.assertIn("finding ID", verification)
        self.assertIn("visual-review.json", verification)

        deck_schema = json.loads(ADAPTIVE_DECK_SCHEMA.read_text(encoding="utf-8"))
        exception_schema = json.loads(
            ADAPTIVE_EXCEPTION_SCHEMA.read_text(encoding="utf-8")
        )
        visual_schema = json.loads(
            ADAPTIVE_VISUAL_SCHEMA.read_text(encoding="utf-8")
        )
        deck_contract = ADAPTIVE_DECK_SPEC.read_text(encoding="utf-8")
        self.assertEqual(deck_schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(
            exception_schema["properties"]["schemaVersion"]["const"], 1
        )
        self.assertEqual(visual_schema["properties"]["schemaVersion"]["const"], 1)
        self.assertIn("claimIds", deck_contract)
        self.assertIn("template-profile.json", deck_contract)
        self.assertIn("findingId", deck_contract)

    def test_readme_matches_current_search_and_research_contracts(self):
        content = README.read_text(encoding="utf-8")
        self.assertIn("검색 backend와 원문 검증은 `web-search` 계약이 결정합니다", content)
        self.assertIn("사용자 제공 자료만 재구성하거나 외부 사실이 없는 창작형 덱", content)
        self.assertIn("목적에 맞는 5~8개 화면 SPA", content)
        self.assertIn("--strict --min-body-pt 15", content)
        self.assertNotIn("고정 8개 화면 SPA", content)
        self.assertNotIn("research agent·`/fleet`에 위임하지 않습니다", content)
        self.assertNotIn("매번 실시간 공식 자료 조사", content)

    def test_research_scenario_policies(self):
        scenarios = json.loads(FIXTURES.read_text(encoding="utf-8"))
        normalized_skill = " ".join(self.skill.split())
        for scenario in scenarios:
            for expected_policy in scenario["expected_policy"]:
                with self.subTest(
                    scenario=scenario["name"], expected_policy=expected_policy
                ):
                    self.assertIn(" ".join(expected_policy.split()), normalized_skill)

    def test_only_first_party_documentation_mcp_is_bundled(self):
        cli_config = json.loads(CLI_MCP_CONFIG.read_text(encoding="utf-8"))
        vscode_config = json.loads(VSCODE_MCP_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(set(cli_config["mcpServers"]), {"microsoft-learn"})
        self.assertEqual(set(vscode_config["servers"]), {"microsoft-learn"})
        self.assertNotIn("search MCP/API", self.skill)


if __name__ == "__main__":
    unittest.main()
