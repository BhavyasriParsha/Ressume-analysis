from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

import pymupdf


MAX_PDF_BYTES = 5 * 1024 * 1024

SECTION_NAMES = {
    "summary": ["summary", "profile", "professional summary", "about"],
    "skills": ["skills", "technical skills", "core competencies", "toolbox"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "education": ["education", "academic background"],
    "projects": ["projects", "selected projects", "key projects"],
    "certifications": ["certifications", "licenses", "courses", "training"],
}


def _clean_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw or "").strip()


def _read_bytes(file_obj) -> bytes:
    if hasattr(file_obj, "getvalue"):
        return file_obj.getvalue()
    if hasattr(file_obj, "read"):
        current_position = file_obj.tell() if hasattr(file_obj, "tell") else 0
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        data = file_obj.read()
        if hasattr(file_obj, "seek"):
            file_obj.seek(current_position)
        return data
    raise ValueError("The uploaded file is not a valid PDF or could not be read.")


def extract_text_from_pdf(file_obj) -> str:
    if file_obj is None:
        raise ValueError("No PDF was uploaded.")

    try:
        data = _read_bytes(file_obj)
    except ValueError:
        raise
    except Exception as exc:  # pragma: no cover - broad exception for unreadable uploads
        raise ValueError("The uploaded file is not a valid PDF or could not be read.") from exc

    if not data:
        return ""
    if len(data) > MAX_PDF_BYTES:
        raise ValueError(f"The PDF is larger than {MAX_PDF_BYTES // (1024 * 1024)} MB. Please upload a smaller file.")

    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            pages = [page.get_text("text") for page in doc]
    except Exception as exc:  # pragma: no cover - broad exception for malformed uploads
        raise ValueError("The uploaded file is not a valid PDF or could not be read.") from exc

    return "\n".join(pages)


def _match_heading(line: str) -> Tuple[Optional[str], str]:
    """Return (section_key, inline_content) if the line is a section heading.

    A heading is a line that is exactly an alias ("Skills", "Skills:") or an alias
    followed by a colon and inline content ("Skills: Python, SQL"). Lines that merely
    start with an alias word ("Training 20 new hires") are content, not headings.
    """
    normalized = line.lower().strip()
    for section_key, aliases in SECTION_NAMES.items():
        for alias in aliases:
            if normalized == alias:
                return section_key, ""
            if normalized.startswith(alias + ":"):
                return section_key, line.partition(":")[2].strip()
    return None, ""


def detect_resume_sections(text: str) -> Dict[str, str]:
    raw_text = text or ""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    sections: Dict[str, str] = {key: "" for key in SECTION_NAMES}
    current_key: Optional[str] = None

    for line in lines:
        matched_key, inline = _match_heading(line)
        if matched_key:
            current_key = matched_key
            if inline:
                sections[current_key] = f"{sections[current_key]} {inline}".strip()
            continue

        if current_key is not None:
            sections[current_key] = f"{sections[current_key]} {line}".strip()

    for key in list(sections):
        sections[key] = _clean_text(sections[key])

    if not any(sections.values()):
        sections["summary"] = _clean_text(raw_text[:600])

    return sections
