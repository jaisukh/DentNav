import json
import re
from typing import Any, Dict, List

import httpx
from app.config import settings

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"

KNOWLEDGE_BASE = """
# DENTNAV KNOWLEDGE BASE — COMPRESSED REFERENCE

## PLATFORM
DentNav: Guidance platform for foreign-trained dentists pursuing U.S. dentistry. Simplifies pathways, corrects misconceptions, helps match route to profile (background, finances, visa, goals). Contact: dentnavglobal@gmail.com

## PATHWAYS
- DDS/DMD IDP: U.S. dental degree. Portal: ADEA CAAPID.
- Dental Residency: General/specialty training. Portal: ADEA PASS.
- Dental Hygiene: State-specific + NBDHE/ADEX. State dependent.
- Dental Assistant: State-specific; useful for exposure and networking.
- Applicants can apply to DDS/DMD and residency simultaneously, but should do so strategically.

## ROADMAP (ordered)
1. Clarify goal: GP/specialty/hygiene/assisting/teaching/research/state-limited pathway
2. Start cycle prep early (INBDE, TOEFL, credentials, documents)
3. Credential evaluation (e.g., ECE)
4. INBDE pass early
5. TOEFL/equivalent competitive score
6. Build profile: clinical experience, research, publications, U.S. exposure, observerships, assistant roles, community work, graduate study
7. Program selection by profile fit
8. Secure recommendations early
9. Prepare bench tests + interviews
10. Research state licensure rules (degree/residency is not auto-license)

## DDS/DMD vs RESIDENCY DECISION
Choice is profile-fit based, not popularity-based.

## MYTHS vs FACTS
- Some residencies accept foreign-trained directly.
- No pathway gives automatic licensure in any state.
- DDS/DMD qualifies you; state license still required.
- INBDE is pass/fail; selection uses whole profile.
- Residency costs and length vary.
- DDS and DMD are academically equivalent.
- Degree choice does not automatically determine immigration outcomes.

## KEY PRINCIPLES
- No universal path for every foreign-trained dentist.
- Best path = profile fit.
- Verify licensure + immigration with official authorities.
- Strategic focused applications outperform broad unfocused applications.
""".strip()


def load_analysis_mock() -> Dict[str, Any]:
    with settings.analysis_mock_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _strip_markdown_code_fence(content: str) -> str:
    trimmed = content.strip()
    if trimmed.startswith("```"):
        lines = trimmed.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return trimmed


def _stringify_answers(answers: Dict[str, Any]) -> str:
    return json.dumps(answers, ensure_ascii=False, indent=2, sort_keys=True)


def _normalize_body(value: Any) -> List[str]:
    if isinstance(value, list):
        paragraphs = [str(item).strip() for item in value if str(item).strip()]
        if paragraphs:
            return paragraphs
    if isinstance(value, str) and value.strip():
        return [chunk.strip() for chunk in value.split("\n\n") if chunk.strip()]
    return []


def _extract_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
    return None


def _estimate_performance_from_answers(answers: Dict[str, Any]) -> int:
    """
    Heuristic fallback only if model output misses/invalidates Performance.
    Keeps score profile-dependent instead of static.
    """
    score = 58.0

    inbde = str(answers.get("q8-inbde", "")).strip().lower()
    if inbde == "yes":
        score += 12
    elif inbde == "no":
        score -= 5

    years = _extract_number(answers.get("q7-clinical-years"))
    if years is not None:
        if years >= 8:
            score += 10
        elif years >= 4:
            score += 7
        elif years >= 2:
            score += 4
        elif years < 1:
            score -= 3

    toefl_band = _extract_number(answers.get("q9-toefl"))
    if toefl_band is not None:
        if toefl_band >= 5:
            score += 8
        elif toefl_band >= 4:
            score += 5
        elif toefl_band >= 3:
            score += 2
        else:
            score -= 2

    target_program = str(answers.get("q2-target-program", "")).strip().lower()
    if "i don't know" in target_program or "guidance" in target_program:
        score -= 3
    elif target_program:
        score += 2

    return int(max(35, min(95, round(score))))


def _extract_performance_score(parsed: Dict[str, Any], answers: Dict[str, Any]) -> int:
    candidate = parsed.get("Performance")

    # Accept nested model outputs like {"Performance": {"score": 74}}.
    if isinstance(candidate, dict):
        for key in ("score", "value", "performance"):
            if key in candidate:
                number = _extract_number(candidate.get(key))
                if number is not None:
                    return int(max(35, min(95, round(number))))

    number = _extract_number(candidate)
    if number is not None:
        return int(max(35, min(95, round(number))))

    # Keep non-static fallback when model omits/mangles this field.
    return _estimate_performance_from_answers(answers)


def _normalize_response(parsed: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
    country = str(parsed.get("Country") or answers.get("q1-degree-country") or "Unknown").strip()
    degree = str(parsed.get("degree") or answers.get("q1b-degree-type") or "Not specified").strip()
    years_of_exp = str(parsed.get("yearsOfExp") or answers.get("q7-clinical-years") or "Not specified").strip()

    performance = _extract_performance_score(parsed, answers)

    body = _normalize_body(parsed.get("Body"))
    if not body:
        body = _normalize_body(load_analysis_mock().get("Body"))

    return {
        "Country": country,
        "degree": degree,
        "yearsOfExp": years_of_exp,
        "Performance": performance,
        "Body": body,
    }


def _build_system_prompt() -> str:
    return (
        "You are DentNav's pathway strategist for foreign-trained dentists pursuing U.S. dentistry.\n"
        "Use only relevant claims from the provided knowledge base and profile data.\n"
        "Do not promise guaranteed admission, visa outcomes, or licensure.\n"
        "Be practical, profile-specific, and action-oriented.\n\n"
        "Return ONLY valid JSON with this exact shape:\n"
        "{\n"
        '  "Country": "string",\n'
        '  "degree": "string",\n'
        '  "yearsOfExp": "string",\n'
        '  "Performance": 0,\n'
        '  "Body": ["paragraph 1", "paragraph 2", "paragraph 3"]\n'
        "}\n\n"
        "Rules:\n"
        "- Performance must be an INTEGER from 35 to 95 derived from the provided profile answers.\n"
        "- Do not return Performance as an object/string explanation; return only a single number.\n"
        "- Body must be an array of 3 to 5 paragraphs.\n"
        "- Each paragraph should be 2 to 4 sentences.\n"
        "- Paragraph 1 is an intro assessment.\n"
        "- Remaining paragraphs should include pathway fit, immediate 90-day plan, risks/misconceptions, and next milestones.\n"
        "- Keep claims consistent with state-specific and school-specific variability.\n\n"
        f"{KNOWLEDGE_BASE}"
    )


async def generate_analysis_from_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.has_groq_config:
        raise ValueError("Missing GROQ_API_KEY")

    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {
            "role": "user",
            "content": (
                "Generate a personalized U.S. dentistry pathway analysis from this questionnaire data.\n"
                f"Profile answers JSON:\n{_stringify_answers(answers)}"
            ),
        },
    ]

    payload = {
        "model": settings.groq_model,
        "temperature": 0.35,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=40.0) as client:
        response = await client.post(GROQ_CHAT_COMPLETIONS_URL, headers=headers, json=payload)
        response.raise_for_status()
        raw = response.json()

    content = raw["choices"][0]["message"]["content"]
    parsed = json.loads(_strip_markdown_code_fence(content))
    return _normalize_response(parsed, answers)
