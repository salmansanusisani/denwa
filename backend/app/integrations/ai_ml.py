"""AI/ML Integration Client for Denwa.

Retrieves verified company context from the RAG pipeline and builds the CALL-E
task string and resultSchema. This is the seam the callback worker uses; it is
kept thin and easy to mock.

Contract:
- Inputs: company_id (int), caller_number (str), optional likely_topic (str)
- Outputs: dict:
    {
        "context": str,
        "task": str,
        "result_schema": dict
    }
"""
import logging
from typing import Any, Dict, Optional

from app.rag import builder as rag_builder

logger = logging.getLogger("denwa.ai_client")

RESULT_SCHEMA: Dict[str, Any] = {
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
    "You are support for Company #{company_id}. Call this customer back ({caller_number}) and greet them politely. "
    "Ask what they needed help with, then answer using ONLY the verified company "
    "information below. Do NOT invent addresses, prices, stock, hours or policies — "
    "if the answer is not in the provided content, tell the customer you don't know "
    "and offer to have a human follow up. Keep the call brief and end by asking if "
    "there is anything else.\n\n"
    "VERIFIED COMPANY CONTENT (use this exactly, do not add details):\n{content}"
)


def get_verified_context_and_task(
    company_id: int,
    caller_number: str,
    likely_topic: str = "general inquiries and support",
    context_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve verified knowledge base context and assemble the CALL-E task.

    Uses the packaged RAG pipeline (``app.rag``) so uploaded company documents
    are chunked, embedded and retrieved from the in-memory index.
    """
    if context_override is not None and context_override.strip():
        context = context_override.strip()
        task_str = _TASK_TEMPLATE.format(
            company_id=company_id,
            caller_number=caller_number,
            content=context,
        )
        return {
            "context": context,
            "task": task_str,
            "result_schema": RESULT_SCHEMA,
        }

    try:
        built = rag_builder.build_task(company_id, likely_topic)
        if built and built.get("task"):
            return {
                "context": built.get("content", ""),
                "task": built["task"],
                "result_schema": built.get("result_schema", RESULT_SCHEMA),
            }
    except Exception as exc:
        logger.warning("RAG task builder failed; using fallback template: %s", exc)

    context = (
        "(No verified knowledge base documents available. Greet the caller, ask their "
        "question, and politely offer a human callback.)"
    )
    task_str = _TASK_TEMPLATE.format(
        company_id=company_id,
        caller_number=caller_number,
        content=context,
    )

    return {
        "context": context,
        "task": task_str,
        "result_schema": RESULT_SCHEMA,
    }