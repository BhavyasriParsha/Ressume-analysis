from __future__ import annotations

from services.ai_service import AIService


def generate_roadmap(resume_text: str, target_role: str, experience_level: str, job_description: str | None = None):
    return AIService().generate_roadmap(resume_text, target_role, experience_level, job_description)
