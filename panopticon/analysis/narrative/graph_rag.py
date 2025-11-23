import logging
import os
from typing import Any, Dict, Iterable, Tuple

from anthropic import Anthropic

logger = logging.getLogger(__name__)

MAX_GRAPH_ITEMS = int(os.environ.get("PANOPTICON_AI_GRAPH_LIMIT", "40") or 40)


def _ai_enabled() -> bool:
    return os.environ.get("PANOPTICON_ENABLE_AI_BRIEFING", "false").lower() in {
        "1",
        "true",
        "yes",
    }


class GraphNarrator:
    def __init__(self):
        self.enabled = _ai_enabled()
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if self.enabled and api_key:
            self.client = Anthropic(api_key=api_key)
            logger.info("GraphNarrator initialized with Anthropic API.")
        else:
            self.client = None
            reason = (
                "API disabled via PANOPTICON_ENABLE_AI_BRIEFING"
                if not self.enabled
                else "ANTHROPIC_API_KEY missing"
            )
            logger.warning("GraphNarrator disabled: %s.", reason)

    def generate_briefing(
        self, target: str, graph_data: Dict[str, Any], risks: Dict[str, Any]
    ) -> str:
        """
        Uses Claude to synthesize a graph into an intelligence briefing when enabled.
        Sensitive identifiers are redacted before leaving the platform.
        """
        if not (self.enabled and self.client):
            return "AI Intelligence Briefing disabled. Set PANOPTICON_ENABLE_AI_BRIEFING=true to opt in."

        nodes_desc = []
        for uid, info in self._limited_items(graph_data.get("nodes", {}).items()):
            props = ", ".join(
                [f"{k}={self._redact_value(v)}" for k, v in info.get("properties", {}).items()]
            )
            nodes_desc.append(f"- Node {self._redact_value(uid)} ({info.get('type')}): {props}")

        edges_desc = []
        for edge in self._limited_items(graph_data.get("edges", [])):
            edges_desc.append(
                f"- {self._redact_value(edge['source'])} --[{edge['type']}]--> {self._redact_value(edge['target'])}"
            )

        risk_desc = []
        for uid, summary in self._limited_items(risks.items()):
            risk_desc.append(
                f"- Risk cluster {self._redact_value(uid)}: grade {summary.get('grade')} (score {summary.get('risk_score')})"
            )

        context = "\n".join(nodes_desc + edges_desc + risk_desc)

        prompt = f"""
        You are a Senior Intelligence Analyst for Panopticon. 
        Analyze the following raw graph data regarding target '{target}'.
        
        RAW DATA:
        {context}
        
        TASK:
        Write a concise, professional intelligence briefing (2-3 paragraphs). 
        1. Identify the primary identity cluster.
        2. Highlight any links between social personas and deep web/breach data.
        3. Flag specific risks (weak passwords, suspicious IP geolocation).
        4. Conclude with an assessment of the target's digital hygiene.
        
        Do not use markdown formatting for the final output, just plain text paragraphs.
        """

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.3,
                system="You are an expert OSINT analyst. Your output is strict, factual, and risk-oriented.",
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"GraphRAG generation failed: {e}")
            return "Error generating intelligence briefing."

    def _limited_items(self, iterable: Iterable) -> Iterable:
        count = 0
        for item in iterable:
            if count >= MAX_GRAPH_ITEMS:
                break
            yield item
            count += 1

    def _redact_value(self, value: Any) -> str:
        if not isinstance(value, str):
            return str(value)
        val = value.strip()
        if "@" in val:
            name, domain = val.split("@", 1)
            return f"{name[:2]}***@{domain}"
        if val.count(".") == 3 and all(part.isdigit() for part in val.split(".")):
            return f"{val.split('.')[0]}.***.***.{val.split('.')[-1]}"
        if len(val) > 8:
            return f"{val[:4]}…{val[-2:]}"
        return val
