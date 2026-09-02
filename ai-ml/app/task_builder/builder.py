"""Turns retrieved chunks into (a) condensed answer content and (b) a CALL-E task
string + resultSchema.

This is the contract Backend's worker calls: build_task(company_id, likely_topic)
returns {"task": ..., "result_schema": ...} — see ai-ml/README.md "Contract with Backend".

Prompt-safety rules baked into the task string:
  - The agent answers ONLY from the provided verified content.
  - It must not invent facts, prices, stock, etc.
  - When it can't answer confidently, it says so and offers a human follow-up.

If no GROQ_API_KEY is present, a deterministic template fallback is used so the
pipeline still works end-to-end for the demo.
"""
from __future__ import annotations

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from app.retriever.retriever import retrieve_for_topic, retrieve_company_context

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# CALL-E task field has a length budget; keep generated tasks comfortably under it.
MAX_TASK_LEN = 3000

RESULT_SCHEMA = {
    "type": "object",
    "required": ["question_asked", "answer_given", "resolved", "needs_human_followup"],
    "properties": {
        "question_asked": {"type": "string"},
        "answer_given": {"type": "string"},
        "resolved": {"type": "boolean"},
        "needs_human_followup": {"type": "boolean"},
    },
}

_TASK_TEMPLATE = (
    "You are {company} support. Call this customer back and greet them. "
    "Ask what they needed help with, then answer using ONLY the verified company "
    "information below. Do NOT invent addresses, prices, stock, hours or policies — "
    "if the answer is not in the provided content, tell the customer you don't know "
    "and offer to have a human follow up. Keep the call brief and end by asking if "
    "there is anything else.\n\n"
    "VERIFIED COMPANY CONTENT (use this exactly, do not add details):\n{content}"
)


def _condense_with_llm(chunks: list[str]) -> str | None:
    key = os.getenv("GROQ_API_KEY")
    if OpenAI is None or not key:
        return None
    try:
        client = OpenAI(base_url=_GROQ_BASE_URL, api_key=key)
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=1500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You condense support-document excerpts into one short block of factual, "
                        "call-ready information. Output ONLY the condensed content, no preamble. "
                        "Do not add facts that are not present in the excerpts."
                    ),
                },
                {
                    "role": "user",
                    "content": "Condense the following excerpts into a single short block "
                    "the agent can read out verbatim:\n\n" + "\n\n---\n\n".join(chunks),
                },
            ],
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or None
    except Exception:
        return None


def _build(company_id: int, chunks: list[str]) -> dict:
    """Shared assembly: condense chunks, wrap in the safety-bounded task template."""
    falls_back = False
    content = _condense_with_llm(chunks)
    if content is None:
        falls_back = True
        content = "\n".join(f"- {c}" for c in chunks)
    if not content.strip():
        content = "(No company content is available yet. Tell the customer you'll have a human call back.)"

    task = _TASK_TEMPLATE.format(company=f"company #{company_id}", content=content)
    if len(task) > MAX_TASK_LEN:
        task = task[:MAX_TASK_LEN] + "\n[content truncated]"
    if falls_back:
        task += "\n\nNote: answer from the provided content above only."
    return {"task": task, "result_schema": RESULT_SCHEMA}


def build_task(company_id: int, likely_topic: str) -> dict:
    """Build the CALL-E task string + resultSchema for a company's likely topic."""
    return _build(company_id, retrieve_for_topic(company_id, likely_topic, k=5))


def build_task_for_topics(company_id: int, likely_topics: list[str]) -> dict:
    """Variant of build_task that pre-seeds context across several likely topics."""
    return _build(company_id, retrieve_company_context(company_id, likely_topics, k_per_topic=3))