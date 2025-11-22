import os
from typing import Dict, Any
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class GraphNarrator:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)
            logger.info("GraphNarrator initialized with Anthropic API.")
        else:
            self.client = None
            logger.warning("GraphNarrator: No ANTHROPIC_API_KEY found. AI features disabled.")

    def generate_briefing(self, target: str, graph_data: Dict[str, Any], risks: Dict[str, Any]) -> str:
        """
        Uses Claude to synthesize a graph into an intelligence briefing.
        """
        if not self.client:
            return "AI Intelligence Briefing unavailable (API Key missing)."

        # Serialize graph for context
        nodes_desc = []
        for uid, info in graph_data.get('nodes', {}).items():
            props = ", ".join([f"{k}={v}" for k, v in info.get('properties', {}).items()])
            nodes_desc.append(f"- Node {uid} ({info.get('type')}): {props}")
        
        edges_desc = []
        for edge in graph_data.get('edges', []):
            edges_desc.append(f"- {edge['source']} --[{edge['type']}]--> {edge['target']}")
        
        risk_desc = []
        for k, v in risks.items():
            risk_desc.append(f"- Risk for {k}: {v.get('grade')} (Score: {v.get('risk_score')}) - {v.get('notes')}")

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
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"GraphRAG generation failed: {e}")
            return "Error generating intelligence briefing."
