"""Live OpenAI Agents SDK integration.

The deterministic core imports this module only for live runs. Tests can inject
a fake runtime, so CI never needs an API key or network access.
"""

from __future__ import annotations

import os
from importlib.resources import files
from typing import Protocol, TypeVar

from pydantic import BaseModel

from .models import (
    ApplicationPackage,
    CandidateDocumentBundle,
    CandidateProfile,
    DiscoveryBatch,
    FitScores,
    InterviewPack,
    Opportunity,
    OutcomeLearningReport,
    QAReport,
    SearchPreferences,
    SupervisorReport,
    VerificationReport,
)
from .utils import opportunity_id

T = TypeVar("T", bound=BaseModel)


class AgentRuntime(Protocol):
    """Interface consumed by Orchestrator; implemented by OpenAI and test fakes."""

    async def extract_profile(self, bundle: CandidateDocumentBundle) -> CandidateProfile: ...

    async def discover(
        self, profile: CandidateProfile, preferences: SearchPreferences, max_results: int
    ) -> DiscoveryBatch: ...

    async def verify(
        self, opportunity: Opportunity, preferences: SearchPreferences
    ) -> VerificationReport: ...

    async def fit(
        self, profile: CandidateProfile, opportunity: Opportunity, preferences: SearchPreferences
    ) -> FitScores: ...

    async def research_supervisor(
        self, profile: CandidateProfile, opportunity: Opportunity
    ) -> SupervisorReport: ...

    async def draft_application(
        self,
        profile: CandidateProfile,
        opportunity: Opportunity,
        supervisor_report: SupervisorReport | None,
    ) -> ApplicationPackage: ...

    async def review_application(
        self,
        profile: CandidateProfile,
        opportunity: Opportunity,
        supervisor_report: SupervisorReport | None,
        package: ApplicationPackage,
    ) -> QAReport: ...

    async def prepare_interview(
        self,
        profile: CandidateProfile,
        opportunity: Opportunity,
        supervisor_report: SupervisorReport | None,
    ) -> InterviewPack: ...

    async def analyze_outcomes(
        self, profile: CandidateProfile, history_json: str
    ) -> OutcomeLearningReport: ...


def _prompt(name: str) -> str:
    return files("phd_search_agent.agent_prompts").joinpath(name).read_text(encoding="utf-8")


class OpenAIAgentRuntime:
    """Specialized-agent runtime backed by OpenAI Agents SDK.

    The SDK is imported lazily so deterministic tooling/tests can run even when
    a user chooses not to configure live model access.
    """

    def __init__(self, model: str | None = None):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for live agent runs")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-sol")

    @staticmethod
    def _sdk():
        try:
            from agents import Agent, Runner, WebSearchTool
        except ImportError as exc:  # pragma: no cover - installation failure path
            raise RuntimeError(
                "OpenAI Agents SDK is not installed. Run: python -m pip install -e ."
            ) from exc
        return Agent, Runner, WebSearchTool

    async def _run(self, prompt_file: str, payload: str, output_type: type[T], web: bool = False) -> T:
        Agent, Runner, WebSearchTool = self._sdk()
        tools = [WebSearchTool()] if web else []
        agent = Agent(
            name=prompt_file.removesuffix(".md").replace("_", " ").title(),
            instructions=_prompt(prompt_file),
            model=self.model,
            tools=tools,
            output_type=output_type,
        )
        result = await Runner.run(agent, payload)
        output = result.final_output
        if isinstance(output, output_type):
            return output
        # SDK structured-output runs normally return the Pydantic type. This
        # fallback makes failure explicit if provider behavior changes.
        return output_type.model_validate(output)

    async def extract_profile(self, bundle: CandidateDocumentBundle) -> CandidateProfile:
        if not bundle.documents:
            raise ValueError("No supported candidate documents were found")
        profile = await self._run("profile.md", bundle.combined_text, CandidateProfile)
        profile.source_files = [doc.path for doc in bundle.documents]
        return profile

    async def discover(
        self, profile: CandidateProfile, preferences: SearchPreferences, max_results: int
    ) -> DiscoveryBatch:
        payload = (
            "CANDIDATE PROFILE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nSEARCH PREFERENCES:\n"
            + preferences.model_dump_json(indent=2)
            + f"\n\nReturn at most {max_results} strong, recent leads."
        )
        batch = await self._run("discovery.md", payload, DiscoveryBatch, web=True)
        # Replace model-generated IDs with deterministic IDs to make deduping
        # stable across repeated autonomous cycles.
        for opp in batch.opportunities:
            opp.id = opportunity_id(opp.title, opp.university, opp.url)
        return batch

    async def verify(
        self, opportunity: Opportunity, preferences: SearchPreferences
    ) -> VerificationReport:
        payload = (
            "DISCOVERED OPPORTUNITY:\n"
            + opportunity.model_dump_json(indent=2)
            + "\n\nUSER CONSTRAINTS (used to prioritize what must be verified):\n"
            + preferences.model_dump_json(indent=2)
        )
        return await self._run("verification.md", payload, VerificationReport, web=True)

    async def fit(
        self, profile: CandidateProfile, opportunity: Opportunity, preferences: SearchPreferences
    ) -> FitScores:
        payload = (
            "CANDIDATE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nVERIFIED/AVAILABLE OPPORTUNITY:\n"
            + opportunity.model_dump_json(indent=2)
            + "\n\nPREFERENCES:\n"
            + preferences.model_dump_json(indent=2)
        )
        return await self._run("fit.md", payload, FitScores)

    async def research_supervisor(
        self, profile: CandidateProfile, opportunity: Opportunity
    ) -> SupervisorReport:
        payload = (
            "CANDIDATE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nOPPORTUNITY:\n"
            + opportunity.model_dump_json(indent=2)
        )
        return await self._run("supervisor.md", payload, SupervisorReport, web=True)

    async def draft_application(
        self,
        profile: CandidateProfile,
        opportunity: Opportunity,
        supervisor_report: SupervisorReport | None,
    ) -> ApplicationPackage:
        payload = (
            "CANDIDATE PROFILE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nOPPORTUNITY:\n"
            + opportunity.model_dump_json(indent=2)
            + "\n\nSUPERVISOR REPORT:\n"
            + (supervisor_report.model_dump_json(indent=2) if supervisor_report else "Not available")
        )
        return await self._run("application.md", payload, ApplicationPackage)

    async def review_application(
        self,
        profile: CandidateProfile,
        opportunity: Opportunity,
        supervisor_report: SupervisorReport | None,
        package: ApplicationPackage,
    ) -> QAReport:
        payload = (
            "CANDIDATE PROFILE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nOPPORTUNITY:\n"
            + opportunity.model_dump_json(indent=2)
            + "\n\nSUPERVISOR REPORT:\n"
            + (supervisor_report.model_dump_json(indent=2) if supervisor_report else "Not available")
            + "\n\nAPPLICATION PACKAGE:\n"
            + package.model_dump_json(indent=2)
        )
        return await self._run("qa.md", payload, QAReport)

    async def prepare_interview(
        self,
        profile: CandidateProfile,
        opportunity: Opportunity,
        supervisor_report: SupervisorReport | None,
    ) -> InterviewPack:
        payload = (
            "CANDIDATE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nOPPORTUNITY:\n"
            + opportunity.model_dump_json(indent=2)
            + "\n\nSUPERVISOR REPORT:\n"
            + (supervisor_report.model_dump_json(indent=2) if supervisor_report else "Not available")
        )
        return await self._run("interview.md", payload, InterviewPack)

    async def analyze_outcomes(
        self, profile: CandidateProfile, history_json: str
    ) -> OutcomeLearningReport:
        payload = (
            "CANDIDATE:\n"
            + profile.model_dump_json(indent=2)
            + "\n\nAPPLICATION HISTORY:\n"
            + history_json
        )
        return await self._run("outcome.md", payload, OutcomeLearningReport)
