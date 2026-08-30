from __future__ import annotations

from dataclasses import dataclass

from app.llm.prompts import AQUAEDGE_SYSTEM_PROMPT
from app.llm.providers import BaseProvider, LLMResponse
from app.mhs_registry.registry import HardwareRegistry
from app.rag.simple_tfidf import TfidfRetriever


@dataclass(slots=True)
class AquaEdgeAgent:
    provider: BaseProvider
    model: str
    registry: HardwareRegistry
    retriever: TfidfRetriever | None = None

    def answer(self, question: str, telemetry_context: str = "") -> LLMResponse:
        retrieved = ""
        if self.retriever is not None:
            hits = self.retriever.search(question, k=3)
            retrieved = "\n\n".join(
                f"[DOC {d.doc_id} score={score:.3f}]\n{d.text}" for d, score in hits
            )

        devices = self.registry.discover()
        prompt = f"""
Operator question:
{question}

Current telemetry / diagnostic context:
{telemetry_context or 'No live telemetry supplied.'}

MHS-ready hardware registry snapshot:
{devices}

Retrieved project context:
{retrieved or 'No retrieved context.'}

Return a concise engineering answer. Separate measured facts, model inference and recommendations.
Do not imply direct actuator authority.
""".strip()
        return self.provider.chat(self.model, AQUAEDGE_SYSTEM_PROMPT, prompt)
