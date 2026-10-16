"""HTML building blocks for the CareerPilot interface.

Every function that takes user- or model-provided text escapes it before it is
placed into markup, so resume and job-description content can never inject HTML.
"""
from __future__ import annotations

import base64
import html
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import streamlit as st

from utils.config import get_groq_api_key, is_demo_mode

ASSETS = Path(__file__).resolve().parents[1] / "assets"
CSS_PATH = ASSETS / "styles.css"
LOGO_PATH = ASSETS / "logo.svg"

# Dial geometry: a 240-degree arc open at the bottom, like a cockpit gauge.
_CX, _CY, _R = 100, 100, 78
_START, _SWEEP = 150, 240


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


escape = _e


def inject_styles() -> None:
    if CSS_PATH.exists():
        st.html(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>")


def ai_configured() -> bool:
    return bool(get_groq_api_key()) and not is_demo_mode()


def score_band(score: int) -> Tuple[str, str]:
    if score >= 75:
        return "strong", "Strong"
    if score >= 50:
        return "fair", "Fair"
    return "weak", "Needs work"


# ---------------------------------------------------------------- page chrome

def page_header(title: str, description: str) -> None:
    if ai_configured():
        status = '<span class="cp-mode cp-mode--ai" title="A Groq key is configured for resume review and job-match feedback; provider access is checked only when a request is made. Interview and roadmap guidance uses built-in rules.">Groq configured</span>'
    else:
        status = '<span class="cp-mode" title="Resume and job-match feedback uses built-in rules. Interview and roadmap guidance always uses built-in rules.">Demo mode</span>'
    st.html(
        f'<header class="cp-header"><div class="cp-header-text"><h1 class="cp-title">{_e(title)}</h1>'
        f'<p class="cp-lede">{_e(description)}</p></div>{status}</header>'
    )


def section_title(text: str, note: str = "") -> str:
    note_html = f'<p class="cp-section-note">{_e(note)}</p>' if note else ""
    return f'<div class="cp-section"><h2 class="cp-section-title">{_e(text)}</h2>{note_html}</div>'


def render_section_title(text: str, note: str = "") -> None:
    st.html(section_title(text, note))


def _svg_image(svg: str, css_class: str) -> str:
    # st.html sanitizes inline <svg>, so graphics are embedded as self-contained images.
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img class="{css_class}" src="data:image/svg+xml;base64,{encoded}" alt="" aria-hidden="true">'


_EMPTY_MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
    '<circle cx="24" cy="24" r="20" fill="none" stroke="#CFD8D3" stroke-width="2" stroke-dasharray="4 5"/>'
    '<path d="M14 31 L21 20 L28 26 L35 15" fill="none" stroke="#A3195B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def empty_state(title: str, body: str) -> None:
    st.html(
        f'<div class="cp-empty">{_svg_image(_EMPTY_MARK, "cp-empty-mark")}'
        f'<div><p class="cp-empty-title">{_e(title)}</p><p class="cp-empty-body">{_e(body)}</p></div></div>'
    )


def source_note(ai_generated: bool) -> None:
    if ai_generated:
        text = "Feedback written by AI from your resume. Scores are calculated by fixed rules, so they stay comparable between runs."
    elif ai_configured():
        text = "Groq did not return usable feedback, so this result uses built-in rules. Check the key, model availability, and network before retrying."
    else:
        text = "Feedback comes from built-in rules. Add a Groq API key in Settings for AI-written resume-review and job-match feedback."
    st.html(f'<p class="cp-source">{_e(text)}</p>')


# ---------------------------------------------------------------- instruments

def _polar(radius: float, degrees: float) -> Tuple[float, float]:
    rad = math.radians(degrees)
    return _CX + radius * math.cos(rad), _CY + radius * math.sin(rad)


def _arc(radius: float, start: float, end: float) -> str:
    x1, y1 = _polar(radius, start)
    x2, y2 = _polar(radius, end)
    large = 1 if end - start > 180 else 0
    return f"M {x1:.2f} {y1:.2f} A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f}"


_BAND_COLORS = {"strong": "#2F7D57", "fair": "#2C6E9B", "weak": "#9A6412"}

# Styles live inside the SVG because it is rendered as an image. One orchestrated
# moment: the needle and arc sweep up to the value together, unless reduced motion is set.
_DIAL_STYLE = (
    "<style>"
    ".v{animation:arc 900ms cubic-bezier(.2,.8,.2,1) both}"
    ".n{transform-origin:100px 100px;animation:needle 900ms cubic-bezier(.2,.8,.2,1) both}"
    "@keyframes arc{from{stroke-dashoffset:1}}"
    "@keyframes needle{from{transform:rotate(0deg)}}"
    "@media (prefers-reduced-motion:reduce){.v,.n{animation:none}}"
    "</style>"
)


def _dial_svg(value: Optional[int], band_key: str) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 168">{_DIAL_STYLE}',
        f'<path d="{_arc(_R, _START, _START + _SWEEP)}" fill="none" stroke="#E3E9E5" stroke-width="10" stroke-linecap="round"/>',
    ]
    for i in range(11):
        angle = _START + _SWEEP * i / 10
        major = i % 5 == 0
        x1, y1 = _polar(60 if major else 64, angle)
        x2, y2 = _polar(69, angle)
        color, width = ("#4A5868", 2) if major else ("#B9C5BF", 1.5)
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"/>')
    if value is not None:
        if value > 0:
            end = _START + _SWEEP * value / 100
            parts.append(
                f'<path class="v" d="{_arc(_R, _START, end)}" pathLength="1" stroke-dasharray="1" fill="none" '
                f'stroke="{_BAND_COLORS[band_key]}" stroke-width="10" stroke-linecap="round"/>'
            )
        nx, ny = _polar(56, _START)
        rotation = _SWEEP * value / 100
        parts.append(
            f'<g class="n" style="transform:rotate({rotation:.1f}deg)"><line x1="{_CX}" y1="{_CY}" x2="{nx:.2f}" y2="{ny:.2f}" '
            f'stroke="#A3195B" stroke-width="3.5" stroke-linecap="round"/></g>'
        )
    parts.append(f'<circle cx="{_CX}" cy="{_CY}" r="5" fill="#14233C"/></svg>')
    return "".join(parts)


def gauge(value: Optional[int], label: str, caption: str = "", size: str = "lg") -> str:
    """A cockpit-style dial. The number and band are always printed as text, not only drawn."""
    if value is None:
        band_key, band_text = "empty", caption or "Not measured yet"
        number = "—"
        aria = f"{label}: not measured yet"
    else:
        value = max(0, min(100, int(value)))
        band_key, band_text = score_band(value)
        number = str(value)
        aria = f"{label}: {value} out of 100, {band_text.lower()}"
        if caption:
            band_text = f"{band_text}. {caption}"

    return (
        f'<figure class="cp-gauge cp-gauge--{size}" role="img" aria-label="{_e(aria)}">'
        f'<div class="cp-dial">{_svg_image(_dial_svg(value, band_key), "cp-dial-art")}'
        f'<span class="cp-dial-number{" cp-dial-number--empty" if value is None else ""}">{_e(number)}</span></div>'
        f'<figcaption><span class="cp-gauge-label">{_e(label)}</span>'
        f'<span class="cp-gauge-band cp-gauge-band--{band_key}">{_e(band_text)}</span></figcaption></figure>'
    )


def gauge_row(items: Sequence[Tuple[Optional[int], str, str]]) -> None:
    # In the overview row, captions are hints for unmeasured gauges only.
    dials = "".join(gauge(v, label, caption if v is None else "", size="sm") for v, label, caption in items)
    st.html(f'<div class="cp-gauge-row">{dials}</div>')


def breakdown(scores: Dict[str, int], maxima: Dict[str, int], notes: Dict[str, str]) -> str:
    rows = []
    for key, value in scores.items():
        maximum = maxima.get(key, 100) or 100
        pct = max(0.0, min(1.0, value / maximum))
        band_key, _ = score_band(int(pct * 100))
        rows.append(
            f'<li class="cp-bar"><div class="cp-bar-head"><span class="cp-bar-name">{_e(key.title())}</span>'
            f'<span class="cp-bar-value">{value}<span class="cp-bar-max"> / {maximum}</span></span></div>'
            f'<div class="cp-bar-track" aria-hidden="true"><div class="cp-bar-fill cp-bar-fill--{band_key}" style="width:{pct * 100:.0f}%"></div></div>'
            f'<p class="cp-bar-note">{_e(notes.get(key, ""))}</p></li>'
        )
    return f'<ul class="cp-bars">{"".join(rows)}</ul>'


# ---------------------------------------------------------------- lists and chips

def chips(items: Iterable[str], tone: str = "neutral", empty: str = "") -> str:
    values = [item for item in items if str(item).strip()]
    if not values:
        return f'<p class="cp-muted">{_e(empty)}</p>' if empty else ""
    chip_items = "".join(f'<li class="cp-chip cp-chip--{tone}">{_e(v)}</li>' for v in values)
    return f'<ul class="cp-chips">{chip_items}</ul>'


def item_list(items: Iterable[str], tone: str = "neutral", empty: str = "") -> str:
    values = [item for item in items if str(item).strip()]
    if not values:
        return f'<p class="cp-muted">{_e(empty)}</p>' if empty else ""
    list_items = "".join(f"<li>{_e(v)}</li>" for v in values)
    return f'<ul class="cp-list cp-list--{tone}">{list_items}</ul>'


def muted(text: str) -> str:
    return f'<p class="cp-muted">{_e(text)}</p>'


def render_html(*parts: str) -> None:
    st.html("".join(parts))


def summary(text: str) -> str:
    return f'<p class="cp-summary">{_e(text)}</p>'


def quote_list(items: Iterable[str], empty: str = "") -> str:
    values = [item for item in items if str(item).strip()]
    if not values:
        return f'<p class="cp-muted">{_e(empty)}</p>' if empty else ""
    return "".join(f'<blockquote class="cp-quote">{_e(v)}</blockquote>' for v in values)


# ---------------------------------------------------------------- roadmap

def route(steps: List[Dict[str, object]], destination: str) -> str:
    """Render learning steps as a flight plan: numbered waypoints along one route."""
    items = []
    week = 1
    for index, step in enumerate(steps, start=1):
        weeks = int(step["estimated_weeks"])
        span = f"Week {week}" if weeks == 1 else f"Weeks {week}–{week + weeks - 1}"
        week += weeks
        priority = str(step["priority"])
        items.append(
            f'<li class="cp-waypoint"><span class="cp-wp-marker" aria-hidden="true">{index}</span>'
            f'<div class="cp-wp-body"><p class="cp-wp-meta"><span>{_e(span)}</span>'
            f'<span class="cp-pill cp-pill--{_e(priority.lower())}">{_e(priority)} priority</span></p>'
            f'<h3 class="cp-wp-title">{_e(step["title"])}</h3><p class="cp-wp-text">{_e(step["description"])}</p></div></li>'
        )
    items.append(
        f'<li class="cp-waypoint cp-waypoint--dest"><span class="cp-wp-marker" aria-hidden="true"></span>'
        f'<div class="cp-wp-body"><p class="cp-wp-meta"><span>Week {week}</span></p>'
        f'<h3 class="cp-wp-title">Apply for {_e(destination)} roles</h3></div></li>'
    )
    return f'<ol class="cp-route" aria-label="Learning plan">{"".join(items)}</ol>'


# ---------------------------------------------------------------- overview checklist

def checklist_step(number: int, title: str, detail: str, done: bool) -> str:
    state = "done" if done else "todo"
    status = "Done" if done else "Not started"
    return (
        f'<div class="cp-step cp-step--{state}"><span class="cp-step-marker" aria-hidden="true">{"✓" if done else number}</span>'
        f'<div><p class="cp-step-title">{_e(title)} <span class="cp-step-status">{status}</span></p>'
        f'<p class="cp-step-detail">{_e(detail)}</p></div></div>'
    )
