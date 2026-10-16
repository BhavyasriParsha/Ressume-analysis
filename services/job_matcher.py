from __future__ import annotations

from services.ai_service import AIService


def perform_job_match(resume_text: str, job_description: str):
    return AIService().generate_job_match(resume_text, job_description)
