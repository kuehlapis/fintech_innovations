import os
import re
from functools import partial
from typing import Callable, List

import yaml

from agents.schemas import AdvisoryRecommendation, GuardrailIssue, GuardrailResult, IngestionResult

GR_RULEBOOK = os.path.join(os.path.dirname(__file__), "rules", "guardrail.yaml")


class GuardrailAgent:
    def __init__(self) -> None:
        self.rules: List[Callable[[str], str]] = []
        self._load_rules()

    def _load_rules(self) -> None:
        with open(GR_RULEBOOK, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        for rule in data.get("rules", []):
            if rule["type"] == "regex":
                pattern = rule["pattern"]
                response = rule["response"]
                self.rules.append(
                    partial(self._apply_regex, pattern=pattern, response=response)
                )

            elif rule["type"] == "append":
                response = rule["response"]
                self.rules.append(partial(self._apply_append, response=response))

            elif rule["type"] == "protect":
                keywords = [kw.lower() for kw in rule.get("pattern", [])]
                response = rule["response"]
                self.rules.append(
                    partial(self._apply_protect, keywords=keywords, response=response)
                )

    def _apply_regex(self, text: str, pattern: str, response: str) -> str:
        return re.sub(pattern, response, text)

    def _apply_append(self, text: str, response: str) -> str:
        return text + "\n\n" + response

    def _apply_protect(self, text: str, keywords: List[str], response: str) -> str:
        lowered = text.lower()
        if any(kw in lowered for kw in keywords):
            return response
        return text

    def _apply_text_rules(self, text: str) -> str:
        for rule in self.rules:
            text = rule(text)
        return text

    def _detect_issues(self, recommendation: AdvisoryRecommendation) -> list[GuardrailIssue]:
        issues: list[GuardrailIssue] = []

        text_blob = " ".join(
            [
                recommendation.summary,
                recommendation.outlook,
                recommendation.rationale,
                " ".join(recommendation.actions),
            ]
        ).lower()

        if not recommendation.summary:
            issues.append(
                GuardrailIssue(
                    code="missing_summary",
                    message="Recommendation summary is missing.",
                    severity="blocker",
                )
            )

        if not recommendation.rationale:
            issues.append(
                GuardrailIssue(
                    code="missing_rationale",
                    message="Recommendation lacks rationale.",
                )
            )

        if not recommendation.actions:
            issues.append(
                GuardrailIssue(
                    code="missing_actions",
                    message="No actionable improvements were provided.",
                )
            )

        if re.search(r"\b(execute|place|submit)\s+(trade|order)\b", text_blob):
            issues.append(
                GuardrailIssue(
                    code="direct_trade_execution",
                    message="Direct trade execution language detected.",
                    severity="blocker",
                )
            )

        if re.search(r"\b(guarantee|guaranteed|certain return)\b", text_blob):
            issues.append(
                GuardrailIssue(
                    code="guaranteed_returns",
                    message="Guaranteed return language detected.",
                    severity="blocker",
                )
            )

        if re.search(r"\b(options|futures|margin|leverage)\b", text_blob):
            if not recommendation.warnings:
                issues.append(
                    GuardrailIssue(
                        code="high_risk_no_warning",
                        message="High-risk asset mention without warnings.",
                    )
                )

        return issues

    async def run(
        self,
        recommendation: AdvisoryRecommendation,
        ingestion: IngestionResult,
    ) -> GuardrailResult:
        adjusted = AdvisoryRecommendation(**recommendation.dict())

        adjusted.summary = self._apply_text_rules(adjusted.summary)
        adjusted.rationale = self._apply_text_rules(adjusted.rationale)
        adjusted.outlook = self._apply_text_rules(adjusted.outlook)
        adjusted.actions = [self._apply_text_rules(action) for action in adjusted.actions]

        if not adjusted.warnings:
            adjusted.warnings.append("Advisory only. No trades are executed.")

        issues = self._detect_issues(adjusted)
        approved = not any(issue.severity == "blocker" for issue in issues)

        if ingestion.holdings and not adjusted.actions:
            issues.append(
                GuardrailIssue(
                    code="missing_actions",
                    message="Holdings present but no actions were suggested.",
                )
            )

        return GuardrailResult(
            approved=approved,
            issues=issues,
            adjusted_recommendation=adjusted,
        )