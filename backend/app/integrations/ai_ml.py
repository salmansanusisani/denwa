"""AI/ML Integration Client for Denwa.

Provides a clean, mockable interface for retrieving verified context and building
the CALL-E task string and resultSchema.

Contract with AI/ML:
- Inputs: company_id (int), caller_number (str), optional likely_topic (str)
- Outputs: dict containing:
    {
        "context": str,
        "task": str,
        "result_schema": dict
    }
"""
import logging
import os
import sys
from typing import Any, Dict, Optional

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

    This function attempts to use the project's ai-ml builder if present,
    or falls back to a deterministic, prompt-safe template.
    """
    context = ""

    if context_override is not None:
        context = context_override
    else:
        try:
            ai_ml_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ai-ml"))
            if os.path.exists(ai_ml_dir) and ai_ml_dir not in sys.path:
                sys.path.insert(0, ai_ml_dir)

            from app.task_builder.builder import build_task 

            built = build_task(company_id=company_id, likely_topic=likely_topic)
            if built and "task" in built and "result_schema" in built:
                return {
                    "context": built.get("context", ""),
                    "task": built["task"],
                    "result_schema": built.get("result_schema", RESULT_SCHEMA),
                }
        except Exception as exc:
            logger.debug("Local ai-ml module not available or errored: %s; using internal template", exc)

    if not context.strip():
        context = "(No verified knowledge base documents available. Greet the caller, ask their question, and politely offer a human callback.)"

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
