from __future__ import annotations

from typing import Any, Dict

from services.ai_service import AIService
from services.resume_parser import detect_resume_sections, extract_text_from_pdf


def analyze_resume_document(file_obj, job_description: str | None = None) -> Dict[str, Any]:
    text = extract_text_from_pdf(file_obj)
    sections = detect_resume_sections(text)
    analysis = AIService().generate_resume_analysis(text, sections, job_description or None)
    return {
        "text": text,
        "sections": sections,
        "analysis": analysis,
    }
