from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ResumeAnalysis(BaseModel):
    summary: str
    quality_score: int = Field(ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    score_breakdown: Dict[str, int] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    sections: Dict[str, str] = Field(default_factory=dict)
    ai_generated: bool = False


class JobMatchResult(BaseModel):
    summary: str
    match_score: int = Field(ge=0, le=100)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    keywords_to_add: List[str] = Field(default_factory=list)
    relevant_experience: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    requirements_not_demonstrated: List[str] = Field(default_factory=list)
    ai_generated: bool = False


class InterviewQuestion(BaseModel):
    question: str
    category: str
    difficulty: str
    answer_expectations: List[str] = Field(default_factory=list)


class InterviewFeedback(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    coaching: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)


class RoadmapStep(BaseModel):
    title: str
    description: str
    priority: str
    estimated_weeks: int


class CareerRoadmap(BaseModel):
    summary: str
    strengths: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    learning_sequence: List[RoadmapStep] = Field(default_factory=list)
    weekly_milestones: List[str] = Field(default_factory=list)
    # Fit with the target job description; None when no job description was given.
    progress: Optional[int] = Field(default=None, ge=0, le=100)
