"""
AI-POWERED COUNTY BUDGET ANALYZER
Professional-grade AI extraction & analysis pipeline
"""

from __future__ import annotations

import os
import io
import json
import time
import base64
import logging
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, List

from dotenv import load_dotenv
from openai import OpenAI
import pypdf

# --------------------------------------------------
# CONFIGURATION & LOGGING
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("county-ai-analyzer")


@dataclass(frozen=True)
class AIConfig:
    openai_model: str = "gpt-4o"
    groq_model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.1
    max_tokens: int = 1000
    min_confidence: int = 50


@dataclass
class CountyMetrics:
    total_revenue: int = 0
    total_expenditure: int = 0
    own_source_revenue: int = 0
    pending_bills: int = 0
    data_source: str = "AI extraction"
    confidence_score: int = 0


# --------------------------------------------------
# AI CLIENT FACTORY
# --------------------------------------------------

def get_ai_client(config: AIConfig) -> Tuple[Optional[OpenAI], Optional[str]]:
    """
    Resolve available AI provider and model.
    """
    if api_key := os.getenv("OPENAI_API_KEY"):
        logger.info(f"Using OpenAI backend ({config.openai_model})")
        return OpenAI(api_key=api_key), config.openai_model

    if api_key := os.getenv("GROQ_API_KEY"):
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        model = config.groq_model
        
        # Test the connection
        try:
            client.models.list()
            logger.info(f"✅ Groq connected ({model})")
            return client, model
        except Exception as e:
            logger.error(f"❌ Groq connection failed: {e}")
            return None, None

    logger.error("No AI API key configured")
    return None, None


# --------------------------------------------------
# PDF UTILITIES
# --------------------------------------------------

def extract_relevant_text(
    pdf_bytes: bytes, county: str, max_pages: int = 10
) -> str:
    """
    Extract relevant text window around a county section.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    start_page = -1

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if county.lower() in text.lower():
            start_page = i
            break

    if start_page == -1:
        return "County section not clearly identified."

    collected = []
    for i in range(start_page, min(start_page + max_pages, len(reader.pages))):
        collected.append(reader.pages[i].extract_text() or "")

    return "\n".join(collected)[:15_000]


# --------------------------------------------------
# AI EXTRACTION
# --------------------------------------------------

def build_prompt(county: str) -> str:
    return f"""
You are a senior financial analyst specializing in Kenyan County Government reports.

TASK:
Extract the following metrics for **{county} County ONLY**.

METRICS:
1. Total Revenue Available
2. Total Expenditure
3. Own-Source Revenue (OSR)
4. Pending Bills

RULES:
- Ignore all other counties
- Convert all values to integers (KES)
- If missing, return 0
- Use tables where available
- Be conservative if unsure

RETURN STRICT JSON ONLY:
{{
  "total_revenue": <int>,
  "total_expenditure": <int>,
  "own_source_revenue": <int>,
  "pending_bills": <int>,
  "data_source": "PDF page references",
  "confidence_score": 0-100
}}
"""


def extract_metrics_with_ai(
    pdf_bytes: bytes, county: str, config: AIConfig
) -> CountyMetrics:
    client, model = get_ai_client(config)
    if not client:
        raise RuntimeError("AI client unavailable")

    prompt = build_prompt(county)
    pdf_base64 = base64.b64encode(pdf_bytes).decode()

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    if "gpt-4o" in model:
        messages[0]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:application/pdf;base64,{pdf_base64}",
                    "detail": "high",
                },
            }
        )
    else:
        context = extract_relevant_text(pdf_bytes, county)
        messages[0]["content"].append(
            {"type": "text", "text": f"\nContext:\n{context}"}
        )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        response_format={"type": "json_object"},
    )

    raw = json.loads(response.choices[0].message.content)

    return CountyMetrics(
        total_revenue=int(raw.get("total_revenue", 0)),
        total_expenditure=int(raw.get("total_expenditure", 0)),
        own_source_revenue=int(raw.get("own_source_revenue", 0)),
        pending_bills=int(raw.get("pending_bills", 0)),
        data_source=raw.get("data_source", "AI"),
        confidence_score=int(raw.get("confidence_score", 0)),
    )


# --------------------------------------------------
# ANALYSIS ENGINE
# --------------------------------------------------

def analyze(metrics: CountyMetrics, config: AIConfig) -> Dict[str, Any]:
    insights: List[str] = []

    if metrics.confidence_score < config.min_confidence:
        insights.append("⚠️ Low confidence — manual verification advised")

    if metrics.total_revenue and metrics.total_expenditure:
        delta = metrics.total_revenue - metrics.total_expenditure
        insights.append(
            "✅ Budget surplus"
            if delta > 0
            else "⚠️ Budget deficit"
            if delta < 0
            else "⚖️ Balanced budget"
        )

    if metrics.total_revenue:
        ratio = (metrics.own_source_revenue / metrics.total_revenue) * 100
        insights.append(f"📊 OSR contribution: {ratio:.1f}%")

    completeness = sum(
        1
        for v in [
            metrics.total_revenue,
            metrics.total_expenditure,
            metrics.own_source_revenue,
            metrics.pending_bills,
        ]
        if v > 0
    )

    return {
        "insights": insights,
        "completeness": (completeness / 4) * 100,
        "health": "Good"
        if metrics.total_revenue >= metrics.total_expenditure
        else "Review Needed",
    }


# --------------------------------------------------
# REPORTING
# --------------------------------------------------

def format_currency(value: int) -> str:
    if value >= 1_000_000_000:
        return f"Ksh {value / 1e9:.2f} B"
    if value >= 1_000_000:
        return f"Ksh {value / 1e6:.2f} M"
    return f"Ksh {value:,}"


def generate_report(
    county: str, metrics: CountyMetrics, analysis: Dict[str, Any]
) -> str:
    return f"""
# {county} County Budget Analysis

## Key Metrics
- Total Revenue: {format_currency(metrics.total_revenue)}
- Total Expenditure: {format_currency(metrics.total_expenditure)}
- Own-Source Revenue: {format_currency(metrics.own_source_revenue)}
- Pending Bills: {format_currency(metrics.pending_bills)}

## Insights
{"".join(f"- {i}\n" for i in analysis["insights"])}

## Data Quality
- Confidence Score: {metrics.confidence_score}/100
- Completeness: {analysis["completeness"]:.0f}%
- Financial Health: {analysis["health"]}

---
Generated via AI-assisted document analysis.
"""


# --------------------------------------------------
# PIPELINE ENTRY POINT
# --------------------------------------------------

def run_pipeline(pdf_bytes: bytes, county: str) -> Dict[str, Any]:
    start = time.time()
    config = AIConfig()

    try:
        metrics = extract_metrics_with_ai(pdf_bytes, county, config)
        analysis = analyze(metrics, config)
        report = generate_report(county, metrics, analysis)

        return {
            "status": "success",
            "county": county,
            "metrics": metrics.__dict__,
            "analysis": analysis,
            "report": report,
            "processing_time_sec": round(time.time() - start, 2),
            "method": "AI-Powered",
        }

    except Exception as exc:
        logger.exception("Pipeline failure")
        return {
            "status": "error",
            "county": county,
            "error": str(exc),
            "processing_time_sec": round(time.time() - start, 2),
        }
