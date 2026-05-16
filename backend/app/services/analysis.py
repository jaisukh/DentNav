import json
import re
from datetime import date
from typing import Any

import braintrust
from braintrust import traced, wrap_openai
from openai import AsyncOpenAI

from app.config import settings
from app.services.answers_validate import AnswerMap

# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Base — FULL verbatim content from DentNav Knowledge Base PDF
# ─────────────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = """
# DENTNAV KNOWLEDGE BASE — U.S. PATHWAYS FOR FOREIGN-TRAINED DENTISTS

A structured question-and-answer guide for foreign-trained dentists exploring U.S. dental pathways.

**Important note:** Dental licensure, visa sponsorship, residency eligibility, and state board rules
can change. This document is an educational guide and should be used alongside official school
websites, state dental boards, ADEA application portals, and immigration/legal advice when needed.

## 1. DENTNAV AT A GLANCE

DentNav is a guidance platform built for foreign-trained dentists who want to pursue dentistry in
the United States. Its purpose is to simplify confusing pathways, explain application systems,
correct common misconceptions, and help applicants choose a route that matches their background,
finances, visa status, long-term goals, and professional strengths.

Most students do not fail because they lack talent. They struggle because they do not know which
pathway fits them, when the application cycle starts, how licensing differs by state, or how to
build a competitive profile before they apply.

## 2. CORE PATHWAY OVERVIEW

Foreign-trained dentists typically explore one or more of the following pathways:

### DDS/DMD International Dentist Program (IDP)
- Typical purpose: Earn a U.S. dental degree
- Main application portal: ADEA CAAPID
- Key notes: Strong option for applicants seeking a broad general dentistry pathway and wider
  recognition.

### Dental Residency
- Typical purpose: Train in general dentistry or a specialty
- Main application portal: ADEA PASS
- Key notes: Program eligibility varies. Some specialties accept foreign-trained dentists directly;
  some may require DDS/DMD or have stricter prerequisites.

### Dental Hygiene Pathway
- Typical purpose: Work as a hygienist in states that permit the route
- Main application portal: State-specific + NBDHE/ADEX
- Key notes: Requirements differ by state; many states require CODA-linked pathways or additional
  steps.

### Dental Assistant / Related Roles
- Typical purpose: Gain U.S. exposure while preparing
- Main application portal: State-specific
- Key notes: Helpful for building U.S. experience, networking, and familiarity with clinical
  systems.

## 3. THE FOUR MOST COMMON STUDENT QUESTIONS

### How can a foreign-trained dentist practice in the U.S.?
There is no single national route. Most applicants either enter an international DDS/DMD program,
enter an eligible residency program, pursue limited or supervised state-specific pathways where
available, or transition into other dental-related roles while preparing for licensure.

### Can a foreign-trained dentist practice without additional training?
In most situations, no. The most common routes require further education, residency, or state
board–approved licensure steps. A few states may offer limited, supervised, faculty, or restricted
licenses, but these are exceptions and must be checked directly with the state board.

### Can I apply for DDS/DMD and residency at the same time?
Yes. Many applicants apply to both pathways to improve their odds, but they should be strategic
and avoid applying blindly. Each application should match the candidate's profile, specialty
background, finances, and long-term plan.

### What is the step-by-step roadmap?
A practical roadmap usually includes credential evaluation, exam preparation, English testing if
required, application planning, letters of recommendation, statement writing, U.S. exposure,
interview preparation, and state-specific licensure research.

## 4. RECOMMENDED STEP-BY-STEP ROADMAP

1. **Clarify your goal:** Decide whether your target is general practice, specialty training,
   hygiene, assisting, teaching, research, or a state-specific limited pathway.
2. **Study the application cycle early:** Many students underestimate timing. For a class or
   intake year, preparation often starts many months earlier with INBDE, TOEFL, credentials, and
   documents ready before the portal opens.
3. **Complete credential evaluation:** Use an academic evaluation service such as ECE when
   programs request it so schools can understand your transcripts in U.S. terms.
4. **Prepare for INBDE:** Most pathways require INBDE. Programs usually view it as pass/fail, but
   passing efficiently and early is important.
5. **Prepare TOEFL or equivalent when required:** A competitive English score can significantly
   affect eligibility and interview strength.
6. **Build your profile:** Strengthen the résumé through clinical experience, specialty background,
   research, publications, U.S. dental exposure, observerships, assistant roles, community work,
   or U.S. graduate study where relevant.
7. **Choose programs strategically:** Apply based on your actual strengths instead of applying
   broadly without a plan.
8. **Secure evaluations and recommendation requests early:** Do not wait until the deadline to
   contact faculty or mentors.
9. **Prepare for bench tests and interviews:** Applicants often focus only on exams and forget
   practical assessments and communication skills.
10. **Research licensure state by state:** A degree or residency does not automatically grant a
    license in every state. State boards decide licensure requirements.

## 5. DDS/DMD VS RESIDENCY: HOW TO THINK ABOUT THE CHOICE

For many applicants, the real decision is not whether one path is better in absolute terms, but
which path best matches their previous training, finances, immigration situation, and professional
goals.

A DDS/DMD route may be attractive for those seeking a broad U.S. degree pathway and access to
traditional general practice routes. A residency route may be especially attractive for applicants
who already have specialty training, significant clinical experience, or a clear specialist
identity they want to preserve and build upon.

Specialization can offer stronger identity, defined scope, and advanced procedural authority
within the U.S. system. At the same time, general dentistry remains an excellent profession, and
many applicants prefer a broader path. The correct choice is the one aligned with the candidate's
goals — not simply the one that seems more popular online.

## 6. MYTHS AND FACTS

| Myth | Better explanation |
|------|--------------------|
| You cannot do residency without a DDS/DMD. | Some residency programs accept foreign-trained dentists directly, although eligibility varies by specialty and by school. |
| Residency gives automatic license only in a few states. | No pathway gives automatic licensure everywhere. Licensure always depends on the state dental board and its process. |
| DDS/DMD automatically gives license in all 50 states. | A degree helps qualify you, but you still apply separately for a state license. |
| INBDE score determines which residency you get. | INBDE is generally reported as pass or fail. Selection depends on the entire application, not a numeric INBDE score. |
| Residency is always cheaper than DDS. | Cost varies dramatically by program, school, length, and whether the program charges tuition or offers a stipend. |
| Residency is always two years. | Program length varies. Some are one year; others are longer. |
| DDS is more valuable than DMD. | DDS and DMD are academically equivalent. The naming depends on the school. |
| Completing DDS automatically leads to a green card. | Immigration outcomes depend on visa category, employer sponsorship, and separate immigration processes, not on the dental degree alone. |

## 7. FREQUENTLY ASKED QUESTIONS BY TOPIC

### A. Application platforms

**Q. How do I apply for residency programs in the U.S.?**
A. Most dental residency programs use ADEA PASS. Applicants should review each program's
requirements individually because prerequisites and visa policies can differ.

**Q. How do I apply for an international DDS/DMD program?**
A. International dentist DDS/DMD pathways commonly use ADEA CAAPID. Programs can differ widely
in deadlines, required documents, bench tests, and interview processes.

**Q. Can I apply for both DDS/DMD and residency?**
A. Yes. Many applicants do. The key is to apply strategically, understand each pathway clearly,
and avoid a scattered application approach.

### B. Building competitiveness

**Q. What can I do in the U.S. before I enter dental school to become more competitive?**
A. Relevant options may include U.S. graduate programs, research roles, observerships, assistant
roles, public health training, or healthcare administration pathways — especially when they help
you build academic strength, U.S. exposure, or professional networking.

**Q. What are common mistakes applicants make?**
A. Not knowing their strengths, choosing the wrong programs, underestimating the timeline, failing
to prepare adequately for TOEFL, and neglecting bench test or interview preparation.

**Q. Why does the process take so long?**
A. Because the pathway usually involves multiple steps: credential evaluation, exam preparation,
English testing, application portals, school-specific requirements, interviews, immigration
planning, and then state licensure.

### C. Exams and preparation

**Q. What is ECE evaluation?**
A. ECE converts academic credentials into a U.S.-readable evaluation so schools can interpret
prior education appropriately.

**Q. What is the best INBDE preparation?**
A. The uploaded notes mention Bootcamp as a useful resource and also indicate DentNav's intention
to build structured exam preparation support. The broader lesson is that students benefit from
question practice, mock tests, condensed revision sheets, and repeated review.

**Q. Is INBDE only for DDS/DMD applicants?**
A. No. It is commonly needed across multiple pathways for foreign-trained dentists.

### D. Specialty-specific questions

**Q. How can I pursue orthodontics, pediatric dentistry, periodontics, prosthodontics, or
endodontics in the U.S.?**
A. Applicants with prior specialty training from their home country may be competitive for
related specialty residencies, but program rules vary. Direct specialty application can be a
strong path for those with matching clinical experience, thesis work, publications, and a clear
specialist profile.

**Q. How can I become an oral surgeon in the U.S.?**
A. This is usually a more complex route. Many candidates first pursue a U.S. dental degree and
then apply for OMFS, while others may choose general practice or surgically oriented routes that
expand their experience in oral surgery–related procedures.

**Q. Can prior MDS training help?**
A. Yes. It may strengthen candidacy for specialty pathways by demonstrating advanced training,
thesis experience, procedural familiarity, and academic seriousness.

### E. Jobs before licensure

**Q. Can a foreign-trained dentist work in the U.S. before becoming licensed as a dentist?**
A. Possible non-dentist roles may include research, public health, healthcare administration,
marketing or product specialist roles, data-related healthcare roles, patient coordination, or
state-permitted dental assistant roles.

**Q. How do I become a dental assistant?**
A. Rules are state-specific. Some applicants pursue DANB certification or state dental assisting
registration depending on the jurisdiction.

**Q. Can foreign-trained dentists work in dental schools without full U.S. licensure?**
A. In limited settings, some schools may hire foreign-trained dentists as faculty, instructors,
simulation educators, researchers, or other academic staff under institution-specific and
state-specific rules. This should be reviewed carefully with the school and licensing authority.

### F. Dental hygienist pathway

**Q. Can a foreign-trained dentist become a dental hygienist in the U.S.?**
A. This pathway is highly state-specific. Many jurisdictions require formal hygiene education and
licensure steps. The uploaded notes identify Florida as a state with a distinct route that may
not require additional hygiene school, but applicants still need to satisfy the state's
examination and licensing requirements.

**Q. Does being in Florida mean I can work as a hygienist automatically?**
A. No. Even in state-specific alternate pathways, applicants still need to complete the required
exams and licensure process.

### G. Licensing and states

**Q. How many states can I work in after residency?**
A. There is no single answer that applies permanently because state rules change. The uploaded
notes list several states often discussed for post-residency pathways, but students should always
verify directly with the relevant dental board before making decisions.

**Q. Does New York require residency for initial licensure?**
A. The uploaded source notes mention a PGY-1–based pathway for New York licensure. Because
licensure rules are time-sensitive, applicants should always verify the current regulation with
the New York State authority.

**Q. Is there any state where a foreign-trained dentist can work without further study?**
A. The uploaded notes discuss Minnesota's limited general dental license as a state-specific
supervised pathway. This is not a blanket national rule and should be confirmed directly through
the Minnesota Board of Dentistry.

### H. Visa and immigration questions

**Q. What is the safest or most practical way to come to the U.S. while planning a dental career?**
A. The uploaded notes favor student or scholar routes for many applicants because they allow
entry into the U.S. system, academic progression, and later transition into employment-based
options.

**Q. Can H-4 holders study dentistry?**
A. The uploaded notes indicate that H-4 holders, especially those with work authorization where
applicable, can study in the U.S., but school-level and immigration-level details should always
be checked individually.

**Q. Does having an EAD help?**
A. It can improve practical flexibility because some schools or hospital-based programs may
prefer applicants who do not require visa sponsorship.

### I. Career, salary, and long-term planning

**Q. Do specialists make more than general dentists?**
A. Income depends on procedures performed, efficiency, case mix, patient flow, and practice
model. The uploaded notes emphasize that advanced procedural skill often increases production
potential.

**Q. How are dentists typically paid?**
A. The source notes discuss production-based compensation models. Actual salary structures vary
by employer, region, specialty, and contract terms.

**Q. Is specialization worth it?**
A. For the right candidate, yes. It can provide stronger professional identity, more advanced
scope, greater procedural confidence, and often higher long-term leverage. But it is not
automatically the best choice for every applicant.

## 8. SUGGESTED QUESTIONS STUDENTS SHOULD ASK

### Pathway selection
- Based on my degree, clinical experience, finances, and visa status, should I prioritize
  DDS/DMD, residency, or another route?
- Which specialties are realistic for my background?
- Would a general practice residency or specialty residency make more sense for me?

### Application readiness
- Am I ready to apply this cycle or should I strengthen my profile first?
- What documents should I complete before ADEA CAAPID or ADEA PASS opens?
- How can I improve my CV, statement, and interview profile?

### State licensure
- Which states currently recognize my planned pathway after graduation or residency?
- What are the state board steps after I finish the program?

### Immigration and work planning
- Does my visa status support school, residency, or work?
- Should I focus on programs that sponsor visas or programs that accept EAD holders more easily?

### Return on investment
- How much time, cost, and earning potential should I expect from each pathway?
- Is my goal specialization, faster practice entry, long-term academic career, or private
  practice?

## 9. HIGH-VALUE TAKEAWAYS FOR STUDENTS

- There is no single universal path for every foreign-trained dentist in the U.S.
- The right pathway depends on profile fit, not on online popularity.
- A degree or residency does not automatically grant a license in every state.
- Students should verify all licensure and immigration issues with official authorities.
- Applying early, strategically, and with a realistic plan is far more powerful than applying
  broadly without direction.
- Prior specialty training, research, U.S. exposure, and clear career goals can dramatically
  improve application quality.

## 10. TOEFL SCALE CONTEXT (CRITICAL — APPLIES TO ALL OUTPUT)

As of January 2026, TOEFL iBT uses a **1–6 band scale in 0.5-point increments**, replacing the
old 0–120 scale. The questionnaire captures TOEFL as a band score (2, 2.5, 3, ... 6).

- Band 6 = expert-level proficiency
- Band 5.0–5.5 = very strong, above most program thresholds
- Band 4.5 = competitive threshold for most dental programs
- Band 4.0 = borderline; improvement recommended
- Band 3.0–3.5 = below threshold (most programs will flag)
- Band 2.0–2.5 = significant barrier requiring intensive preparation

**Never reference "TOEFL 90", "100/120", or any 0–120 number in recommendations.** Use band
scores only (e.g., "TOEFL band 4.5").
""".strip()


def load_analysis_mock() -> dict[str, Any]:
    return json.loads(settings.analysis_mock_path.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# State planning — model-driven (no hardcoded per-state presets)
# ─────────────────────────────────────────────────────────────────────────────
#
# State-specific facts (IDP availability, exam acceptance, sponsorship reality,
# tax posture, named programs) come from the model under the prompt rules.
# We intentionally do NOT keep a hardcoded per-state preset table — the prompt
# is responsible for accuracy and verification-grounded language. Server-side
# normalization only refuses known-false claims (e.g., wrong "no state income
# tax" claims, IDP claims for schools not on the verified short list); it does
# not provide content.

STATE_COMPETITIVENESS_BUCKETS = {
    "low": "Low",
    "moderate": "Moderate",
    "moderate-high": "Moderate-High",
    "high": "High",
}


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────


def _strip_markdown_code_fence(content: str) -> str:
    trimmed = content.strip()
    if not trimmed.startswith("```"):
        return trimmed
    lines = trimmed.splitlines()
    if lines:
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


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


def _clinical_years_score_component(answer: str) -> float:
    s = answer.strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", s)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2.0
    n = _extract_number(s)
    return n if n is not None else 0.0


def _list_of_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _toefl_band_to_legacy_total(value: Any) -> int | None:
    n = _extract_number(value)
    if n is None:
        return None
    n = max(1.0, min(6.0, n))
    return int(round(n * 20))


def _stringify_answers(answers: AnswerMap) -> str:
    return json.dumps(dict(answers), ensure_ascii=False, indent=2, sort_keys=True)


# ─────────────────────────────────────────────────────────────────────────────
# TOEFL sanitization
# ─────────────────────────────────────────────────────────────────────────────

_TOEFL_SUBSTITUTIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)\b0\s*[–-]\s*120\b"), "1–6 band"),
    (re.compile(r"(?i)\bout of\s*120\b"), "on the 1–6 band scale"),
    (re.compile(r"(?i)\b/\s*120\b"), " (1–6 band scale)"),
    (re.compile(r"(?i)\b(?:maximum|max|total)\s*(?:score\s*)?(?:of\s*)?120\b"), "maximum band 6"),
    (re.compile(r"(?i)\b120[- ]point\b"), "6-point band"),
    (
        re.compile(r"(?i)\b(TOEFL(?:\s+iBT)?)\s+(?:total\s+)?(?:score\s+)?(?:of\s+)?(8[0-9]|9[0-9]|10[0-9]|11[0-9]|120)\b"),
        r"\1 band score (1–6 scale)",
    ),
    (re.compile(r"(?i)\biBT\s*\(?\s*0\s*[–-]\s*120\s*\)?"), "iBT (1–6 band scale)"),
]


def _sanitize_legacy_toefl_text(text: str) -> str:
    if not text or not text.strip():
        return text
    for pattern, replacement in _TOEFL_SUBSTITUTIONS:
        text = pattern.sub(replacement, text)
    return text


def _sanitize_response_tree(
    obj: Any,
    skip_keys: frozenset[str] = frozenset({"toeflLegacyEquivalent120", "toeflScore"}),
) -> Any:
    if isinstance(obj, str):
        return _sanitize_legacy_toefl_text(obj)
    if isinstance(obj, list):
        return [_sanitize_response_tree(x, skip_keys) for x in obj]
    if isinstance(obj, dict):
        return {
            k: (v if k in skip_keys else _sanitize_response_tree(v, skip_keys))
            for k, v in obj.items()
        }
    return obj


# ─────────────────────────────────────────────────────────────────────────────
# Derived signals
# ─────────────────────────────────────────────────────────────────────────────


def _interpret_toefl_band(band: str) -> str:
    n = _extract_number(band)
    if n is None:
        return "unknown TOEFL value"
    legacy = _toefl_band_to_legacy_total(n)
    legacy_note = f"(approx {legacy}/120 legacy)" if legacy is not None else ""
    if n >= 5.5:
        return f"band {n} {legacy_note} — EXCELLENT. Major strength. Do NOT recommend improving English."
    if n >= 5.0:
        return f"band {n} {legacy_note} — VERY STRONG. Above threshold. Strength."
    if n >= 4.5:
        return f"band {n} {legacy_note} — COMPETITIVE. Meets threshold."
    if n >= 4.0:
        return f"band {n} {legacy_note} — BORDERLINE. Below threshold; improvement recommended."
    if n >= 3.0:
        return f"band {n} {legacy_note} — BELOW THRESHOLD. Significant prep needed."
    return f"band {n} {legacy_note} — CRITICAL GAP. Intensive prep required."


def _visa_category(visa_raw: str) -> str:
    v = visa_raw.strip().lower()
    if v in {"", "none", "not specified", "unknown"}:
        return "none"
    if v in {"b1/b2", "b1", "b2", "b-1/b-2", "b1 b2"}:
        return "non-study"
    if v in {"green card", "citizen", "citizenship"}:
        return "permanent"
    if v in {"f1", "f-1", "f2", "f-2", "j1", "j-1", "h4", "h-4", "h1", "h-1", "h1b", "h-1b",
             "l1", "l2", "l-1", "l-2", "asylum"}:
        return "active"
    return "active"


def _compute_readiness_dimensions(answers: AnswerMap) -> list[dict[str, Any]]:
    toefl_raw = str(answers.get("q9-toefl", "")).strip()
    inbde_raw = str(answers.get("q8-inbde", "")).strip().lower()
    years_raw = str(answers.get("q7-clinical-years", "")).strip()
    visa_raw = str(answers.get("q4-visa", "")).strip()
    cosigner_raw = str(answers.get("q6-loan-cosigner", "")).strip().lower()
    target_raw = str(answers.get("q2-target-program", "")).strip().lower()

    inbde_score, inbde = (92, ("Strong", "green")) if inbde_raw == "yes" else (15, ("Gap", "red"))

    toefl_n = _extract_number(toefl_raw)
    if toefl_n is None:
        toefl_score, toefl = 40, ("Unclear", "amber")
    elif toefl_n >= 5.5:
        toefl_score, toefl = 95, ("Strong", "green")
    elif toefl_n >= 5.0:
        toefl_score, toefl = 83, ("Strong", "green")
    elif toefl_n >= 4.5:
        toefl_score, toefl = 70, ("Good", "teal")
    elif toefl_n >= 4.0:
        toefl_score, toefl = 50, ("Borderline", "amber")
    else:
        toefl_score, toefl = 20, ("Gap", "red")

    years = _clinical_years_score_component(years_raw) if years_raw else 0.0
    if years >= 7:
        clin_score, clin = 90, ("Strong", "green")
    elif years >= 4:
        clin_score, clin = 70, ("Good", "teal")
    elif years >= 2:
        clin_score, clin = 50, ("Fair", "amber")
    else:
        clin_score, clin = 20, ("Gap", "red")

    visa_cat = _visa_category(visa_raw)
    visa_l = visa_raw.lower().strip()
    is_f2 = bool(re.search(r"\bf[-\s]?2\b", visa_l))
    if visa_cat == "permanent":
        visa_score, visa = 95, ("Strong", "green")
    elif is_f2:
        visa_score, visa = 58, ("Active F-2: limited study; often requires F-1 transition", "amber")
    elif visa_cat == "active":
        visa_score, visa = 70, ("Active", "teal")
    elif visa_cat == "non-study":
        visa_score, visa = 15, ("Gap (B1/B2)", "red")
    else:
        visa_score, visa = 8, ("Gap", "red")

    has_cosigner = cosigner_raw == "yes"
    fin_score, fin = (60, ("Supported", "teal")) if has_cosigner else (12, ("Gap", "red"))

    if "i don't know" in target_raw or "guidance" in target_raw or not target_raw:
        prog_score, prog = 30, ("Unclear", "amber")
    else:
        prog_score, prog = 80, ("Clear", "green")

    toefl_label = f"English (TOEFL band {toefl_raw})" if toefl_raw else "English (TOEFL)"

    return [
        {"name": "Exam readiness (INBDE)", "score": inbde_score, "status": inbde[0], "statusColor": inbde[1]},
        {"name": toefl_label, "score": toefl_score, "status": toefl[0], "statusColor": toefl[1]},
        {"name": "Clinical experience", "score": clin_score, "status": clin[0], "statusColor": clin[1]},
        {"name": "Visa & immigration", "score": visa_score, "status": visa[0], "statusColor": visa[1]},
        {"name": "Financial readiness", "score": fin_score, "status": fin[0], "statusColor": fin[1]},
        {"name": "Program clarity", "score": prog_score, "status": prog[0], "statusColor": prog[1]},
    ]


def _estimate_performance_from_answers(answers: AnswerMap) -> int:
    dims = _compute_readiness_dimensions(answers)
    weights = [0.20, 0.15, 0.15, 0.20, 0.15, 0.15]
    weighted = sum(d["score"] * w for d, w in zip(dims, weights, strict=False))
    return int(max(35, min(95, round(weighted))))


# ─────────────────────────────────────────────────────────────────────────────
# Normalizers
# ─────────────────────────────────────────────────────────────────────────────


def _impact_color(impact: str) -> str:
    return {"high": "red", "medium": "amber", "low": "green"}.get(impact.strip().lower(), "gray")


# Allowed enums (mirrors the system prompt contract).
_ALLOWED_RISK_IMPACTS = {"high", "medium", "low", "unassessed"}
_ALLOWED_IMPACT_COLORS = {"red", "amber", "green", "gray"}
_ALLOWED_DIMENSION_STATUS_COLORS = {"green", "teal", "amber", "red", "gray"}
_ALLOWED_TIMELINE_COLORS = {"red", "amber", "purple", "teal", "green"}
_ALLOWED_ASSESSMENT_TYPES = {"Evidence-Based", "Inferred", "Unassessed"}
_ALLOWED_INTENT_BADGES = {"Needs guidance", "Defined", "Specialty"}


def _coerce_color(value: Any, allowed: set[str], fallback: str) -> str:
    raw = str(value or "").strip().lower()
    if raw in allowed:
        return raw
    # Common model synonyms → snap into the allowed palette.
    synonyms = {
        "orange": "amber",
        "yellow": "amber",
        "warning": "amber",
        "blue": "teal",
        "info": "teal",
        "navy": "teal",
        "indigo": "purple",
        "violet": "purple",
        "pink": "red",
        "crimson": "red",
        "rose": "red",
        "lime": "green",
        "emerald": "green",
        "olive": "green",
        "grey": "gray",
        "neutral": "gray",
        "muted": "gray",
        "white": "gray",
        "black": "gray",
    }
    snapped = synonyms.get(raw, "")
    if snapped in allowed:
        return snapped
    return fallback


def _coerce_impact(value: Any) -> str:
    raw = str(value or "").strip()
    lowered = raw.lower()
    if lowered in {"critical", "severe", "blocker", "very high"}:
        return "High"
    if lowered in {"moderate", "med", "mid"}:
        return "Medium"
    if lowered in {"minor", "minimal", "negligible"}:
        return "Low"
    if lowered in _ALLOWED_RISK_IMPACTS:
        return raw[:1].upper() + raw[1:].lower()
    return raw or "Unassessed"


def _coerce_assessment_type(value: Any) -> str:
    raw = str(value or "").strip()
    lowered = raw.lower()
    if not raw:
        return "Evidence-Based"
    if lowered in {"evidence", "evidence-based", "evidence based", "verified"}:
        return "Evidence-Based"
    if lowered in {"inferred", "inference", "implied", "soft signal"}:
        return "Inferred"
    if lowered in {"unassessed", "not assessed", "unknown", "not collected", "tbd"}:
        return "Unassessed"
    if lowered in {"critical gap", "major constraint", "strategic gap", "blocker", "gap"}:
        return "Evidence-Based"
    return "Evidence-Based"


def _coerce_program_intent_badge(value: Any, target_program: str) -> str:
    raw = str(value or "").strip()
    if raw in _ALLOWED_INTENT_BADGES:
        return raw
    target_l = str(target_program or "").lower()
    if "i don't know" in target_l or "guidance" in target_l or "undecided" in raw.lower():
        return "Needs guidance"
    if any(s in target_l for s in ("ortho", "perio", "endo", "pedo", "prostho", "omfs", "specialty")):
        return "Specialty"
    if target_l:
        return "Defined"
    return "Needs guidance"


def _normalize_competitiveness(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    lowered = raw.lower().replace(" ", "-")
    return STATE_COMPETITIVENESS_BUCKETS.get(lowered, raw)


def _normalize_risk_item(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {k: "" for k in ("issue", "impact", "impactColor", "note", "evidenceBasis", "assessmentType")}
    impact = _coerce_impact(raw.get("impact", ""))
    impact_color = _coerce_color(
        raw.get("impactColor", "") or _impact_color(impact),
        _ALLOWED_IMPACT_COLORS,
        _impact_color(impact),
    )
    return {
        "issue": str(raw.get("issue", "")).strip(),
        "impact": impact,
        "impactColor": impact_color,
        "note": str(raw.get("note", "")).strip(),
        "evidenceBasis": str(raw.get("evidenceBasis", "")).strip(),
        "assessmentType": _coerce_assessment_type(raw.get("assessmentType", "")),
    }


def _normalize_ranked_pathway(raw: Any) -> dict[str, Any]:
    empty = {
        "rank": 0, "rankLabel": "", "pathTitle": "", "fitSummary": "",
        "applicationPortal": "", "requirementsStillNeeded": [],
        "blockers": [], "realityCheck": "", "bestUseCase": "", "isPrimary": False,
    }
    if not isinstance(raw, dict):
        return empty
    rank_int = int(_extract_number(raw.get("rank", 0)) or 0)
    rank_labels = {1: "1st", 2: "2nd", 3: "3rd"}
    # Always force the canonical ordinal label — synonyms like "Primary"/"Secondary"
    # break the schema contract.
    rank_label = rank_labels.get(rank_int, "")
    if not rank_label:
        provided = str(raw.get("rankLabel", "")).strip()
        rank_label = provided or str(rank_int)
    return {
        "rank": rank_int,
        "rankLabel": rank_label,
        "pathTitle": str(raw.get("pathTitle", "")).strip(),
        "fitSummary": str(raw.get("fitSummary", "")).strip(),
        "applicationPortal": str(raw.get("applicationPortal", "")).strip(),
        "requirementsStillNeeded": _list_of_strings(raw.get("requirementsStillNeeded")),
        "blockers": _list_of_strings(raw.get("blockers")),
        "realityCheck": str(raw.get("realityCheck", "")).strip(),
        "bestUseCase": str(raw.get("bestUseCase", "")).strip(),
        "isPrimary": bool(raw.get("isPrimary", rank_int == 1)),
    }


def _normalize_service_item(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {"service": "", "reason": "", "timing": ""}
    return {
        "service": str(raw.get("service", "")).strip(),
        "reason": str(raw.get("reason", "")).strip(),
        "timing": str(raw.get("timing", "")).strip(),
    }


def _normalize_timeline_item(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {"period": "", "periodColor": "", "milestone": "", "detail": ""}
    return {
        "period": str(raw.get("period", "")).strip(),
        "periodColor": _coerce_color(raw.get("periodColor", ""), _ALLOWED_TIMELINE_COLORS, "purple"),
        "milestone": str(raw.get("milestone", "")).strip(),
        "detail": str(raw.get("detail", "")).strip(),
    }


def _calendar_years_in_timeline(timeline: list[dict[str, str]]) -> list[int]:
    years: list[int] = []
    for item in timeline:
        blob = " ".join(str(item.get(k, "")) for k in ("period", "milestone", "detail"))
        for m in re.findall(r"\b(20[0-9]{2})\b", blob):
            years.append(int(m))
    return years


_RELATIVE_TIMELINE_PERIOD_RE = re.compile(
    r"(\d+\s*[-–]\s*\d+\s*months?|months?\s*before|before\s+portal|next\s+\d)",
    re.IGNORECASE,
)


def _timeline_periods_use_relative_language(timeline: list[dict[str, str]]) -> bool:
    """True when a period label is vague, past, or otherwise needs re-anchoring."""
    cy, cq = _current_year_quarter()
    cur_idx = _quarter_index(cy, cq)
    for item in timeline:
        p = str(item.get("period", "")).strip()
        if not p or p.lower() == "now":
            continue
        if re.search(r"\b(early|mid|late)\s+20[0-9]{2}\b", p, re.IGNORECASE):
            return True
        if _RELATIVE_TIMELINE_PERIOD_RE.search(p):
            return True
        if "month" in p.lower():
            return True

        # Detect periods that resolve to a quarter strictly before today.
        # Find first Q + year occurrence; if that quarter is < cur_idx, it's past.
        m_first = re.search(r"\bQ([1-4])\s*(20[0-9]{2})\b", p)
        if m_first:
            q = int(m_first.group(1))
            y = int(m_first.group(2))
            if _quarter_index(y, q) < cur_idx:
                return True
            continue
        # Year-only label (no quarter) that is in the past
        years_in_period = [int(m) for m in re.findall(r"\b(20[0-9]{2})\b", p)]
        if years_in_period and max(years_in_period) < cy:
            return True
    return False


def _quarter_index(year: int, quarter: int) -> int:
    """Map (year, q) → monotonic integer (q is 1..4)."""
    return year * 4 + (quarter - 1)


def _year_quarter_from_index(idx: int) -> tuple[int, int]:
    return idx // 4, (idx % 4) + 1


def _format_quarter_range(start_idx: int, end_idx: int) -> str:
    sy, sq = _year_quarter_from_index(start_idx)
    ey, eq = _year_quarter_from_index(end_idx)
    if start_idx == end_idx:
        return f"Q{sq} {sy}"
    if sy == ey:
        return f"Q{sq}–Q{eq} {sy}"
    return f"Q{sq} {sy}–Q{eq} {ey}"


def _current_year_quarter(today: date | None = None) -> tuple[int, int]:
    today = today or date.today()
    return today.year, (today.month - 1) // 3 + 1


def _year_quarter_period_labels(
    target_cycle: int,
    count: int,
    today: date | None = None,
) -> list[str]:
    """Calendar year + quarter anchors that are always ≥ today's quarter.

    First label is always "Now" (current quarter). The remaining labels span
    from next quarter through the intake year (T Q3 inclusive — typical fall
    matriculation), partitioned roughly evenly. If the intake is already in the
    past or current quarter, fall back to a single "Now" + intake reminder so
    we never emit dates earlier than today.
    """
    if count <= 0:
        return []
    cy, cq = _current_year_quarter(today)
    cur_idx = _quarter_index(cy, cq)
    end_idx = _quarter_index(target_cycle, 3)

    labels: list[str] = ["Now"]
    n_after = count - 1

    if n_after <= 0:
        return labels

    if end_idx <= cur_idx:
        labels.extend([f"Intake {target_cycle}"] * n_after)
        return labels

    total_remaining = end_idx - cur_idx
    base = total_remaining // n_after
    rem = total_remaining % n_after

    cursor = cur_idx + 1
    for i in range(n_after):
        size = base + (1 if i < rem else 0)
        if size <= 0:
            sy, sq = _year_quarter_from_index(cursor) if cursor <= end_idx else (target_cycle, 3)
            labels.append(f"Q{sq} {sy}")
            continue
        end = min(cursor + size - 1, end_idx)
        labels.append(_format_quarter_range(cursor, end))
        cursor = end + 1
    return labels


def _rewrite_timeline_periods_to_year_quarter(
    profile: dict[str, Any], timeline: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Replace period labels with YYYY + quarter anchors; keep milestone/detail."""
    cycle_raw = str(profile.get("targetCycle", "")).strip()
    if not cycle_raw.isdigit():
        return timeline
    labels = _year_quarter_period_labels(int(cycle_raw), len(timeline))
    if len(labels) != len(timeline):
        return timeline
    out: list[dict[str, str]] = []
    for item, period in zip(timeline, labels, strict=True):
        out.append({**item, "period": period})
    return out


def _application_timeline_years_drift_from_target_cycle(
    profile: dict[str, Any], timeline: list[dict[str, str]]
) -> bool:
    """True when explicit 20xx years in the timeline are stale vs target cycle or today.

    Triggers on either:
      (a) latest year is meaningfully earlier than the target intake year, OR
      (b) ANY year in the timeline `period` field is earlier than today's year
          (the timeline must always run from "now" forward — never into the past).
    """
    cycle_raw = str(profile.get("targetCycle", "")).strip()
    years = _calendar_years_in_timeline(timeline)
    if not years:
        return False

    current_year, _ = _current_year_quarter()
    period_years = _calendar_years_in_timeline_periods(timeline)
    if period_years and min(period_years) < current_year:
        return True

    if cycle_raw.isdigit():
        target = int(cycle_raw)
        latest = max(years)
        earliest = min(years)
        if latest < target - 2:
            return True
        if latest <= target - 3 and earliest < target - 6:
            return True
    return False


def _calendar_years_in_timeline_periods(timeline: list[dict[str, str]]) -> list[int]:
    """Return only the years that appear in the `period` label (not detail/milestone)."""
    years: list[int] = []
    for item in timeline:
        for m in re.findall(r"\b(20[0-9]{2})\b", str(item.get("period", ""))):
            years.append(int(m))
    return years


# U.S. states with no broad state personal income tax on wages (verify periodically).
# Do not claim "no state income tax" for states not in this set.
_US_STATES_NO_PERSONAL_INCOME_TAX = frozenset({
    "alaska",
    "florida",
    "nevada",
    "south dakota",
    "tennessee",
    "texas",
    "washington",
    "wyoming",
})

_FALSE_NO_STATE_INCOME_TAX_PHRASE = re.compile(
    r"(?i)\bno\s+state\s+income\s+tax(?:\s+benefits)?\b|\bno\s+income\s+tax\s+benefits\b"
)

_SECONDARY_PARALLEL_MARKERS = (
    "while enrolled",
    "parallel",
    "during your master",
    "your chosen sequence",
    "after your master",
    "after you complete",
    "alongside your master",
    "since you already",
    "given your plan to",
)


def _sanitize_state_income_tax_claim(state_name: str, text: str) -> str:
    """Strip false 'no state income tax' claims for states that levy income tax."""
    if not text or not state_name:
        return text
    key = state_name.strip().lower()
    if key in _US_STATES_NO_PERSONAL_INCOME_TAX:
        return text
    if not _FALSE_NO_STATE_INCOME_TAX_PHRASE.search(text):
        return text
    return _FALSE_NO_STATE_INCOME_TAX_PHRASE.sub(
        "state income tax applies—factor withholding into take-home pay estimates",
        text,
    )


def _sanitize_state_card_income_tax_fields(card: dict[str, Any]) -> dict[str, Any]:
    name = str(card.get("name", "")).strip()
    if not name:
        return card
    out = dict(card)
    for field in ("costOfPracticeLiving", "notes"):
        v = out.get(field)
        if isinstance(v, str) and v.strip():
            out[field] = _sanitize_state_income_tax_claim(name, v)
    return out


# Schools that are NOT verified as CAAPID-listed FTD IDP / advanced-standing programs.
# If the model claims any of these schools operate an IDP, scrub the claim.
_NON_IDP_SCHOOL_PATTERNS = (
    re.compile(r"(?i)\bAugusta\s+University\b[^.]*\bIDP\b"),
    re.compile(r"(?i)\bDental\s+College\s+of\s+Georgia\b[^.]*\bIDP\b"),
    re.compile(r"(?i)\b(?:ASDOH|A\.T\.\s*Still\s+University\s+(?:Arizona|ASDOH))\b[^.]*\bIDP\b"),
    re.compile(r"(?i)\bMidwestern\s+University\b[^.]*\bArizona\b[^.]*\bIDP\b"),
    re.compile(r"(?i)\bIDP:\s*Augusta[^.]*"),
    re.compile(r"(?i)\bIDP:\s*ASDOH[^.]*"),
    re.compile(r"(?i)\bIDP:\s*Midwestern[^.]*Arizona[^.]*"),
)

_VERIFY_CAAPID_FALLBACK = "Verify IDP availability via the latest ADEA CAAPID program list."


def _scrub_unverified_idp_claims(text: str) -> str:
    """Replace claims that unverified schools operate an IDP with a verification reminder."""
    if not text:
        return text
    out = text
    for pat in _NON_IDP_SCHOOL_PATTERNS:
        out = pat.sub(_VERIFY_CAAPID_FALLBACK, out)
    return out


def _scrub_state_card_unverified_idp(card: dict[str, Any]) -> dict[str, Any]:
    out = dict(card)
    for field in (
        "notes", "ftdFriendliness", "licenseRoute", "examExpectation", "clinicalExamNotes",
        "visaSponsorshipReality", "costOfPracticeLiving", "timelineHint",
        "keyPrograms", "reciprocityNotes",
    ):
        v = out.get(field)
        if isinstance(v, str) and v.strip():
            out[field] = _scrub_unverified_idp_claims(v)
    for field in ("priorityActions", "riskFlags"):
        items = out.get(field)
        if isinstance(items, list):
            out[field] = [
                _scrub_unverified_idp_claims(s) if isinstance(s, str) else s
                for s in items
            ]
    return out


def _profile_indicates_masters_first(profile: dict[str, Any]) -> bool:
    em = str(profile.get("entryMode", "")).lower()
    mi = str(profile.get("mastersInterest", "")).lower()
    if "master" in em and ("first" in em or "u.s" in em or "us " in em):
        return True
    if "master" in mi and "pursue" in mi:
        return True
    return False


def _secondary_strategy_redundant_for_masters_first(secondary: str) -> bool:
    """True when secondary re-pitches a U.S. master's though the profile already chose that sequence."""
    t = (secondary or "").strip().lower()
    if not t:
        return True
    if any(m in t for m in _SECONDARY_PARALLEL_MARKERS):
        return False
    if "master" not in t and "mph" not in t and "mha" not in t and "mba" not in t:
        return False
    return any(w in t for w in ("consider", "pursue", "explore", "enroll", "facilitate"))


def _default_secondary_strategy_masters_first(profile: dict[str, Any]) -> str:
    cycle = str(profile.get("targetCycle", "")).strip()
    cycle_bit = f" Align execution with your target cycle ({cycle})." if cycle.isdigit() else ""
    return (
        "Parallel-track IDP readiness alongside your planned U.S. master's: credential evaluation "
        "(ECE/WES), DENTPIN, observerships, and a CAAPID-oriented school list—so your next focused "
        f"phase after F-1 entry is the DDS/DMD application pipeline, not re-litigating the bridge.{cycle_bit}"
    )


def _align_pathway_secondary_for_profile(profile: dict[str, Any], pathway: dict[str, Any]) -> None:
    if not _profile_indicates_masters_first(profile):
        return
    if not _secondary_strategy_redundant_for_masters_first(pathway.get("secondaryStrategy", "")):
        return
    pathway["secondaryStrategy"] = _default_secondary_strategy_masters_first(profile)


# ─────────────────────────────────────────────────────────────────────────────
# Reasoning-quality guards (HARD RULES 19+)
# Catch overclaiming, wrong visa sequencing, mandatory-master's phrasing, and
# overbroad license-portability claims that the LLM tends to default to.
# ─────────────────────────────────────────────────────────────────────────────

_EXECUTION_BLOCKER_VISA_TERMS = ("none", "not specified", "unknown", "", "b1", "b2", "b1/b2", "tourist", "visitor")


def _profile_has_execution_blockers(profile: dict[str, Any]) -> bool:
    visa = str(profile.get("visaStatus", "")).strip().lower()
    cosigner = str(profile.get("loanCosigner", "")).strip().lower()
    visa_blocker = any(visa == t or t in visa for t in _EXECUTION_BLOCKER_VISA_TERMS if t)
    if visa in {"", "none", "not specified", "unknown"}:
        visa_blocker = True
    finance_blocker = cosigner in {"no", "none", "not specified", "unknown", ""}
    return bool(visa_blocker or finance_blocker)


_OVERCONFIDENT_READINESS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\b(?:a\s+|an\s+)?strong\s+candidate\s+for\s+(IDP|CAAPID|DDS|DMD)(\s+programs?)?\b"),
        r"an academically strong candidate for \1\2, but not yet execution-ready due to visa and financial constraints",
    ),
    (
        re.compile(r"(?i)\b(you\s+are|you're|you\s+have|i\s+am|i'm)\s+(?:a\s+|an\s+)?strong\s+(applicant|candidate|profile)\b"),
        r"\1 an academically strong \2 but not yet execution-ready (visa + funding gaps)",
    ),
    (
        re.compile(r"(?i)\b(highly\s+competitive|very\s+competitive)\s+(applicant|candidate|profile)\b"),
        r"\1 academic profile that still needs visa and funding execution to become application-ready",
    ),
    (
        re.compile(r"(?i)\bready\s+to\s+apply\b(?!\s+once)"),
        "academically prepared but not yet ready to apply until visa and funding are unblocked",
    ),
]


def _rewrite_overconfident_readiness_phrasing(text: str, profile: dict[str, Any]) -> str:
    if not text or not _profile_has_execution_blockers(profile):
        return text
    out = text
    for pat, replacement in _OVERCONFIDENT_READINESS_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_VISA_SEQUENCING_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?i)\b(begin|start|initiate|kick\s*off|commence|apply\s+for|file\s+for|pursue)\s+"
            r"(the\s+|your\s+)?(F[-\s]?1|F1|J[-\s]?1|J1|student)\s+"
            r"(visa|visa\s+application|visa\s+process)\b"
            r"(?!\s+(after|once|following|interview|process\s+after))"
        ),
        "shortlist and apply to U.S. master's / IDP programs to obtain an I-20 (admission → I-20 → SEVIS fee → DS-160 → F-1 visa interview)",
    ),
    (
        re.compile(
            r"(?i)\b(begin|start|initiate)\s+(the\s+)?visa\s+(application\s+)?process\b"
            r"(?!\s+(after|once|following))"
        ),
        "plan the visa sequence: secure admission and I-20 first, then file SEVIS fee, DS-160, and the F-1 visa interview",
    ),
]


def _rewrite_visa_application_phrasing(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _VISA_SEQUENCING_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_COMPLETE_MASTERS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\bcomplete\s+(a\s+|the\s+|your\s+)?(U\.?S\.?\s+)?master[''’]?s\s+(degree|program)\b"),
        "pursue or begin a U.S. master's program if needed for visa entry and profile strengthening",
    ),
    (
        re.compile(r"(?i)\bfinish\s+(a\s+|the\s+|your\s+)?(U\.?S\.?\s+)?master[''’]?s\s+(degree|program)\b"),
        "progress through a U.S. master's program if pursued as a bridge",
    ),
    (
        re.compile(r"(?i)\bmust\s+(complete|earn|finish|obtain)\s+(a\s+|the\s+|your\s+)?master[''’]?s\b"),
        "may use a master's as an optional bridge — not a mandatory step",
    ),
]


def _rewrite_complete_masters_phrasing(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _COMPLETE_MASTERS_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_PORTABILITY_CLAIM_VERIFY = (
    "license portability varies by state and depends on which clinical exam you complete, "
    "your degree origin, and years of practice — verify with each receiving state's dental board"
)
_PORTABILITY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)\brecognized\s+in\s+many\s+states\b"), _PORTABILITY_CLAIM_VERIFY),
    (re.compile(r"(?i)\brecognized\s+(?:by|across)\s+most\s+states\b"), _PORTABILITY_CLAIM_VERIFY),
    (re.compile(r"(?i)\bportable\s+across\s+(?:most|many)\s+states\b"), _PORTABILITY_CLAIM_VERIFY),
    (re.compile(r"(?i)\b(?:widely|broadly)\s+portable\b"), _PORTABILITY_CLAIM_VERIFY),
    (re.compile(r"(?i)\baccepted\s+in\s+(?:most|many)\s+(?:U\.?S\.?\s+)?states\b"), _PORTABILITY_CLAIM_VERIFY),
]


def _rewrite_broad_portability_claims(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _PORTABILITY_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_STATE_IDP_ABSOLUTE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\b([A-Z][a-z]+)\s+lacks\s+(?:a\s+)?(?:dedicated\s+)?IDP\s+(?:program|option)s?\b"),
        r"\1 currently has limited or no widely recognized IDP options — verify via the latest ADEA CAAPID program list",
    ),
    (
        re.compile(r"(?i)\b([A-Z][a-z]+)\s+has\s+no\s+IDP\s+(?:program|option)s?\b"),
        r"\1 has limited IDP availability; verify via the latest ADEA CAAPID program list before planning",
    ),
    (
        re.compile(r"(?i)\bthere\s+is\s+no\s+IDP\s+in\s+([A-Z][a-z]+)\b"),
        r"IDP availability in \1 is limited/variable by cycle; verify via the latest ADEA CAAPID program list",
    ),
]


def _rewrite_absolute_state_idp_claims(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _STATE_IDP_ABSOLUTE_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_DIRECT_LICENSURE_ABSOLUTE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\bdirect\s+(?:state\s+)?licensure\s+is\s+not\s+viable\b"),
        "direct state licensure is generally not viable without U.S.-recognized training in your case",
    ),
    (
        re.compile(r"(?i)\bdirect\s+(?:state\s+)?licensure\s+is\s+impossible\b"),
        "direct state licensure is generally not viable without U.S.-recognized training in your case",
    ),
]


def _rewrite_direct_licensure_absolutes(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _DIRECT_LICENSURE_ABSOLUTE_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_DDS_F1_FALSE_BLOCKER_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?i)\bdirect\s+DDS\s*/\s*DMD\s*:\s*not\s+viable\s+without\s+"
            r"(?:a\s+|an\s+|the\s+|confirmed\s+)?F[-\s]?1(?:\s+status)?(?:\s+and\s+admission)?\.?"
        ),
        "Direct DDS/DMD: Requires admission-led F-1 transition when required by the school (F-1 is typically obtained after admission).",
    ),
    (
        re.compile(
            r"(?i)\bDDS\s*/\s*DMD\s+(?:is\s+)?not\s+viable\s+without\s+"
            r"(?:a\s+|an\s+|the\s+|confirmed\s+)?F[-\s]?1(?:\s+status)?\b"
        ),
        "DDS/DMD is viable through admission-led F-1 transition when required by school policy.",
    ),
]


def _rewrite_dds_f1_false_blockers(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _DDS_F1_FALSE_BLOCKER_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_TOEFL_OVERSALE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\bTOEFL[^.]{0,80}\b(excellent|exceptional|outstanding)\b"),
        "TOEFL score is competitive for most programs",
    ),
    (
        re.compile(r"(?i)\bTOEFL[^.]{0,80}\bstrongly\s+competitive\b"),
        "TOEFL score is competitive for most programs",
    ),
]


def _rewrite_toefl_oversell(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, replacement in _TOEFL_OVERSALE_PATTERNS:
        out = pat.sub(replacement, out)
    return out


_GENERIC_ACTIVE_VISA_REWRITE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"(?i)\b(?:plan|map|follow|begin|start|initiate|kick\s*off|secure)\s+"
        r"(?:the\s+|a\s+|an\s+|your\s+)?F[-\s]?1\s+visa\s+sequence[^.]*"
    ),
    re.compile(
        r"(?i)\badmission\s*(?:→|->|-->|–>|—>|\s+to\s+)\s*I[-\s]?20\s*"
        r"(?:→|->|-->|–>|—>|\s+to\s+)\s*(?:SEVIS[^→\->.]*?(?:→|->|-->|–>|—>|\s+to\s+))?"
        r"(?:DS[-\s]?160[^→\->.]*?(?:→|->|-->|–>|—>|\s+to\s+))?"
        r"(?:F[-\s]?1|J[-\s]?1)(?:\s+visa)?(?:\s+interview)?"
    ),
    re.compile(
        r"(?i)\bsecure\s+(?:admission\s+and\s+)?(?:an\s+|the\s+)?I[-\s]?20[^.]*?F[-\s]?1(?:\s+visa)?[^.]*"
    ),
]

_FIXED_ACTIVE_VISA_REWRITES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?i)\b(?:apply|file|filing)\s+for\s+(?:an\s+|a\s+|the\s+|your\s+)?"
            r"F[-\s]?1(?:\s+visa)?\b"
        ),
        "maintain current visa status",
    ),
    (
        re.compile(
            r"(?i)\b(?:begin|start)\s+(?:the\s+|your\s+)?F[-\s]?1(?:\s+visa)?\s+(?:application|process)?\b"
        ),
        "maintain current visa status",
    ),
    (
        re.compile(
            r"(?i)\b(?:pursue|secure|obtain|get)\s+(?:an?\s+|your\s+)?F[-\s]?1(?:\s+visa)?\b"
            r"(?!\s+status)"
        ),
        "maintain current visa status",
    ),
    (
        re.compile(r"(?i)\bvisa\s+pathway\s+for\s+(?:specialty|residency|IDP|DDS)\b"),
        "visa alignment with program requirements",
    ),
    (
        re.compile(r"(?i)\bvisa\s+pathway\s+limitation\b"),
        "visa alignment with program requirements",
    ),
    (
        re.compile(r"(?i)\bstudy\s*/\s*work\s+limitation\b"),
        "status maintenance requirement",
    ),
]


# I-20 is an F-1 (and M-1) document. For non-F-1 active visas, phrases like
# "coordinate I-20 transfer for H-4" are factually wrong. For H-4 and L-2,
# study does not require a new I-20 unless the program mandates transition
# to F-1; for H-1B/L-1, full-time study typically requires change of status
# to F-1 (new I-20). We rewrite the generic "I-20 transfer" phrasing into
# visa-correct wording on a per-kind basis.
_I20_WRONG_FOR_VISA_PATTERNS: list[re.Pattern[str]] = [
    # Longest / most specific first so they consume the trailing "visa alignment" tail.
    re.compile(
        r"(?i)\bsecure\s+(?:admission\s+and\s+)?coordinate\s+I[-\s]?20\s+transfer\s+"
        r"for\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?[14](?:\s+visa)?(?:\s+alignment)?"
    ),
    re.compile(
        r"(?i)\bsecure\s+(?:admission\s+and\s+)?coordinate\s+I[-\s]?20\s+transfer\s+"
        r"for\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2(?:\s+visa)?(?:\s+alignment)?"
    ),
    re.compile(
        r"(?i)\bcoordinate\s+I[-\s]?20\s+transfer\s+(?:to\s+the\s+admitting\s+program\s+)?"
        r"(?:once\s+offers\s+land\s+)?for\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?[14]"
        r"(?:\s+visa)?(?:\s+alignment)?"
    ),
    re.compile(
        r"(?i)\bcoordinate\s+I[-\s]?20\s+transfer\s+(?:to\s+the\s+admitting\s+program\s+)?"
        r"(?:once\s+offers\s+land\s+)?for\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2"
        r"(?:\s+visa)?(?:\s+alignment)?"
    ),
    re.compile(
        r"(?i)\bI[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?[14]"
        r"(?:\s+visa)?(?:\s+alignment)?"
    ),
    re.compile(
        r"(?i)\bI[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2"
        r"(?:\s+visa)?(?:\s+alignment)?"
    ),
    re.compile(
        r"(?i)\balign\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?[14]\s+visa\s+with\s+"
        r"(?:the\s+)?I[-\s]?20\s+transfer(?:\s+process)?"
    ),
    re.compile(
        r"(?i)\balign\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2\s+visa\s+with\s+"
        r"(?:the\s+)?I[-\s]?20\s+transfer(?:\s+process)?"
    ),
]


_H4_ENROLLMENT_PHRASE = (
    "ensure enrollment documentation aligns with your H-4 status; transition to "
    "F-1 only if the admitting program specifically requires it"
)
_F2_ENROLLMENT_PHRASE = (
    "F-2 allows limited study but often requires transition to F-1 for full "
    "program participation — confirm policy with each admitting school"
)
_H1B_ENROLLMENT_PHRASE = (
    "plan change of status from H-1B to F-1 via the admitting program's new I-20 "
    "before full-time enrollment"
)
_L2_ENROLLMENT_PHRASE = (
    "ensure enrollment documentation aligns with your L-2 status; transition to "
    "F-1 only if the admitting program specifically requires it"
)
_L1_ENROLLMENT_PHRASE = (
    "plan change of status from L-1 to F-1 via the admitting program's new I-20 "
    "before full-time enrollment"
)
_OPT_ENROLLMENT_PHRASE = (
    "plan academic re-entry on a fresh I-20 from the admitting program before "
    "OPT expires"
)
_J1_ENROLLMENT_PHRASE = (
    "coordinate DS-2019 transfer with your sponsor and the admitting program "
    "(and plan for any 212(e) 2-year home residency requirement if applicable)"
)
_PERMANENT_ENROLLMENT_PHRASE = (
    "no new visa document is required — permanent residency clears immigration "
    "constraints entirely"
)


def _visa_specific_enrollment_rewrite(profile: dict[str, Any] | None) -> str | None:
    kind = _visa_kind(profile)
    return {
        "F-2": _F2_ENROLLMENT_PHRASE,
        "H-4": _H4_ENROLLMENT_PHRASE,
        "L-2": _L2_ENROLLMENT_PHRASE,
        "H-1B": _H1B_ENROLLMENT_PHRASE,
        "L-1": _L1_ENROLLMENT_PHRASE,
        "OPT": _OPT_ENROLLMENT_PHRASE,
        "J-1": _J1_ENROLLMENT_PHRASE,
        "permanent": _PERMANENT_ENROLLMENT_PHRASE,
    }.get(kind)


_DEPENDENT_I20_STANDALONE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\bsecure\s+admission\s+and\s+coordinate\s+I[-\s]?20\s+transfer\b"),
    re.compile(r"(?i)\bcoordinate\s+I[-\s]?20\s+transfer\b"),
)


def _rewrite_active_visa_phrasing(text: str, profile: dict[str, Any] | None) -> str:
    if not text or not (_profile_visa_is_active(profile) or _profile_visa_is_permanent(profile)):
        return text
    out = text
    maintenance = _active_visa_maintenance_phrase(profile)
    kind = _visa_kind(profile)

    # Generic acquisition-flow wording → visa-specific maintenance wording.
    for pat in _GENERIC_ACTIVE_VISA_REWRITE_PATTERNS:
        out = pat.sub(maintenance, out)

    for pat, replacement in _FIXED_ACTIVE_VISA_REWRITES:
        out = pat.sub(replacement, out)

    # Visa-type correctness: I-20 language is wrong for non-F-1 holders.
    specific = _visa_specific_enrollment_rewrite(profile)
    if specific:
        for pat in _I20_WRONG_FOR_VISA_PATTERNS:
            out = pat.sub(specific, out)

    # For dependents (H-4 / L-2), also rewrite standalone "coordinate I-20 transfer"
    # (without "for H-4" suffix) — I-20 simply doesn't apply to them.
    if kind in {"H-4", "L-2", "F-2"}:
        dependent_phrase = (
            "confirm F-2 study limits and transition to F-1 if full-program participation requires it"
            if kind == "F-2"
            else f"secure admission and confirm the program's enrollment policy for {kind} dependents"
        )
        for pat in _DEPENDENT_I20_STANDALONE_PATTERNS:
            out = pat.sub(dependent_phrase, out)

    if kind == "F-2":
        out = re.sub(
            r"(?i)\bmaintain current visa status\b",
            "confirm F-2 study limits and transition to F-1 if full-program participation requires it",
            out,
        )

    return out


_INBDE_DONE_REPLACEMENT = "leverage INBDE completion for applications"

_INBDE_DONE_REWRITES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?i)\bschedule\s+and\s+pass\s+(?:the\s+)?INBDE[^.]*"
        ),
        _INBDE_DONE_REPLACEMENT,
    ),
    (re.compile(r"(?i)\bschedule\s+(?:the\s+)?INBDE\b"), _INBDE_DONE_REPLACEMENT),
    (re.compile(r"(?i)\bpass\s+(?:the\s+)?INBDE\s+(?:early|first|soon|this\s+cycle)?\b"), _INBDE_DONE_REPLACEMENT),
    (re.compile(r"(?i)\btake\s+(?:the\s+)?INBDE\b"), _INBDE_DONE_REPLACEMENT),
    (re.compile(r"(?i)\bprepare\s+for\s+(?:the\s+)?INBDE\b"), _INBDE_DONE_REPLACEMENT),
    (re.compile(r"(?i)\bINBDE\s+(?:timing|preparation|readiness|not\s+passed|pending)\b"), "INBDE completed"),
    (re.compile(r"(?i)\bINBDE\s+is\s+(?:the\s+)?#?1\s+(?:blocker|priority)\b"), "INBDE is already satisfied"),
    (re.compile(r"(?i)\bclear(?:ing)?\s+(?:the\s+)?INBDE\b"), "leveraging INBDE completion"),
    (re.compile(r"(?i)\bcomplete\s+INBDE\b"), "leverage INBDE completion"),
    # Conditional / feasibility caveats that should never appear when INBDE is already passed.
    (
        re.compile(
            r"(?i)[,;]?\s*apply\s+in\s+the\s+same\s+cycle\s+only\s+if\s+INBDE\s+is\s+cleared\s+early\s+"
            r"and\s+documents\s*\([^)]*\)\s+are\s+fully\s+ready\s*;\s*otherwise\s+shift\s+to\s+the\s+next\s+viable\s+window\.?"
        ),
        "",
    ),
    (
        re.compile(
            r"(?i)\bonly\s+if\s+INBDE\s+is\s+cleared\s+early\b[^.]*"
        ),
        "",
    ),
    (re.compile(r"(?i)\bif\s+INBDE\s+is\s+cleared\s+early\b"), "with INBDE already cleared"),
    (re.compile(r"(?i)\bonce\s+INBDE\s+(?:clears|is\s+cleared|passes|is\s+passed)\b"), "with INBDE already cleared"),
    (re.compile(r"(?i)\bbefore\s+INBDE\s+(?:clears|passes)\b"), "before your CAAPID submission"),
    (re.compile(r"(?i)\bINBDE\s+is\s+cleared\s+early\b"), "INBDE is already cleared"),
    (re.compile(r"(?i)\bINBDE\s+clears?\s+early\b"), "INBDE is already cleared"),
    (re.compile(r"(?i)\bpending\s+INBDE\b"), "INBDE already passed"),
    (re.compile(r"(?i)\bINBDE\s+cleared\s+early\b"), "INBDE is already cleared"),
]


def _rewrite_inbde_done_phrasing(text: str, profile: dict[str, Any] | None) -> str:
    if not text or not _profile_inbde_passed(profile):
        return text
    out = text
    for pat, replacement in _INBDE_DONE_REWRITES:
        out = pat.sub(replacement, out)
    return out


_POST_REWRITE_CLEANUP_PATTERNS: tuple[tuple[re.Pattern[str], Any], ...] = (
    (re.compile(r"\s{2,}"), " "),
    (re.compile(r"\s+([,.;:])"), r"\1"),
    # Remove dangling " visa alignment" suffix when a prior rewrite consumed its head.
    (re.compile(r"(?i)(?:status\s+maintenance\s+requirement|it\s+only\s+if[^.]*?)\s+visa\s+alignment\b"),
     lambda m: m.group(0).replace(" visa alignment", "")),
)


def _clean_rewritten_text(text: str) -> str:
    out = text
    for pat, repl in _POST_REWRITE_CLEANUP_PATTERNS:
        if callable(repl):
            out = pat.sub(repl, out)
        else:
            out = pat.sub(repl, out)
    out = out.strip()
    # Sentence-initial capitalization: if it looks like a full sentence
    # (ends with punctuation or is reasonably long) and starts with lowercase,
    # uppercase the first letter.
    if out and out[0].islower() and (out.endswith((".", "!", "?")) or len(out.split()) > 3):
        out = out[0].upper() + out[1:]
    return out


def _apply_reasoning_guards_to_text(text: Any, profile: dict[str, Any]) -> Any:
    if not isinstance(text, str) or not text.strip():
        return text
    out = text
    out = _rewrite_overconfident_readiness_phrasing(out, profile)
    # Active-visa / INBDE-done rewrites must run BEFORE the generic visa-application
    # rewrite, which otherwise expands "apply for F-1" into the admission→I-20→F-1
    # template that we do NOT want for candidates already holding study/work status.
    out = _rewrite_active_visa_phrasing(out, profile)
    out = _rewrite_inbde_done_phrasing(out, profile)
    if not _profile_visa_is_active(profile):
        out = _rewrite_visa_application_phrasing(out)
    out = _rewrite_complete_masters_phrasing(out)
    out = _rewrite_broad_portability_claims(out)
    out = _rewrite_absolute_state_idp_claims(out)
    out = _rewrite_direct_licensure_absolutes(out)
    out = _rewrite_dds_f1_false_blockers(out)
    out = _rewrite_toefl_oversell(out)
    out = _clean_rewritten_text(out)
    return out


def _apply_reasoning_guards_tree(obj: Any, profile: dict[str, Any]) -> Any:
    if isinstance(obj, str):
        return _apply_reasoning_guards_to_text(obj, profile)
    if isinstance(obj, list):
        return [_apply_reasoning_guards_tree(x, profile) for x in obj]
    if isinstance(obj, dict):
        return {k: _apply_reasoning_guards_tree(v, profile) for k, v in obj.items()}
    return obj


def _profile_visa_is_blocker(profile: dict[str, Any] | None) -> bool:
    """True when visa is definitely a study/work blocker (none, B1/B2, tourist, unknown)."""
    if not profile:
        return True
    v = str(profile.get("visaStatus", "")).strip().lower()
    if not v or v in {"none", "not specified", "unknown"}:
        return True
    if "b1" in v or "b2" in v or "tourist" in v or "visitor" in v:
        return True
    return False


def _profile_has_dual_critical_blockers(profile: dict[str, Any]) -> bool:
    """Critical blockers = INBDE not passed + visa status is a study/work blocker."""
    return (not _profile_inbde_passed(profile)) and _profile_visa_is_blocker(profile)


_ACTIVE_VISA_TOKENS = (
    "f-1", "f1", "j-1", "j1", "h-1b", "h1b", "h1-b", "h-4", "h4",
    "l-1", "l1", "l-2", "l2", "opt", "stem opt",
)
_PERMANENT_VISA_TOKENS = ("green", "perm", "citizen", "lpr", "resident")


def _visa_kind(profile: dict[str, Any] | None) -> str:
    """Classify the candidate's visa into a small, stable set of kinds.

    Returns one of: ``F-1``, ``F-2``, ``J-1``, ``H-1B``, ``H-4``, ``L-1``,
    ``L-2``, ``OPT``, ``B1/B2``, ``permanent``, ``none``, ``unknown``.
    """
    if not profile:
        return "unknown"
    v = str(profile.get("visaStatus", "")).strip().lower()
    if not v or v in {"not specified", "unknown"}:
        return "unknown"
    if v == "none":
        return "none"
    if any(tok in v for tok in _PERMANENT_VISA_TOKENS):
        return "permanent"
    if "b1" in v or "b2" in v or "tourist" in v or "visitor" in v:
        return "B1/B2"
    if "stem" in v and "opt" in v:
        return "OPT"
    if v.strip() == "opt" or " opt" in v or "opt " in v or v.endswith("opt"):
        return "OPT"
    if "f-1" in v or v == "f1" or v.startswith("f1 ") or v.endswith(" f1") or "f1-" in v:
        return "F-1"
    if "f-2" in v or v == "f2" or v.startswith("f2 ") or v.endswith(" f2") or "f2-" in v:
        return "F-2"
    if "j-1" in v or v == "j1" or v.startswith("j1 ") or v.endswith(" j1"):
        return "J-1"
    if "h-1b" in v or "h1b" in v or "h1-b" in v:
        return "H-1B"
    if "h-4" in v or v == "h4" or v.startswith("h4 ") or v.endswith(" h4"):
        return "H-4"
    if "l-1" in v or v == "l1":
        return "L-1"
    if "l-2" in v or v == "l2":
        return "L-2"
    return "unknown"


def _profile_visa_is_active(profile: dict[str, Any] | None) -> bool:
    return _visa_kind(profile) in {"F-1", "F-2", "J-1", "H-1B", "H-4", "L-1", "L-2", "OPT"}


def _profile_visa_is_permanent(profile: dict[str, Any] | None) -> bool:
    return _visa_kind(profile) == "permanent"


# Visa-type-specific copy. These drive (a) phrase substitutions in LLM text
# and (b) authoritative DO/DO NOT directives injected into the profile summary.
_VISA_KIND_COPY: dict[str, dict[str, str]] = {
    "F-1": {
        "label": "F-1 (active study visa)",
        "maintenance_phrase": (
            "maintain F-1 status and coordinate I-20 transfer to the admitting "
            "program once offers land"
        ),
        "enrollment_doc": "I-20",
        "nuance": (
            "F-1 permits full-time study and on-campus employment; CPT/OPT unlock "
            "limited off-campus work. I-20 transfer happens after acceptance; SEVIS "
            "record must move cleanly between programs."
        ),
    },
    "F-2": {
        "label": "F-2 (dependent of F-1)",
        "maintenance_phrase": (
            "confirm F-2 study limits with the admitting school and transition to "
            "F-1 if full-program participation requires it"
        ),
        "enrollment_doc": (
            "dependent F-2 documentation ties to the principal's F-1; a separate "
            "student I-20 is required after transition to F-1"
        ),
        "nuance": (
            "F-2 is a dependent status with no work authorization and constrained "
            "study flexibility compared with F-1. Many full-time/professional "
            "program tracks require conversion to F-1 before enrollment progression."
        ),
    },
    "J-1": {
        "label": "J-1 (exchange visitor)",
        "maintenance_phrase": (
            "maintain J-1 status and coordinate DS-2019 transfer with your sponsor "
            "and the admitting program"
        ),
        "enrollment_doc": "DS-2019",
        "nuance": (
            "J-1 uses DS-2019 (not I-20). Some J-1 programs carry a 212(e) two-year "
            "home-country residency requirement — confirm whether a waiver is needed "
            "before planning H-1B or green card steps later. Specialty programs "
            "often favor J-1 for residency sponsorship."
        ),
    },
    "H-1B": {
        "label": "H-1B (employer-sponsored work visa)",
        "maintenance_phrase": (
            "plan any academic program against H-1B compatibility — full-time "
            "enrollment typically requires a change of status to F-1 via the "
            "admitting program's I-20"
        ),
        "enrollment_doc": "I-20 (after change of status from H-1B)",
        "nuance": (
            "H-1B is work-only; full-time DDS/DMD typically requires change of "
            "status to F-1 (new I-20 from the admitting program). Part-time or "
            "non-degree study can often continue on H-1B — confirm with the "
            "school DSO and the employer."
        ),
    },
    "H-4": {
        "label": "H-4 (dependent of H-1B)",
        "maintenance_phrase": (
            "confirm the admitting program's enrollment policy for H-4 dependents "
            "— most programs permit full-time study on H-4 without a new I-20, "
            "but some require transition to F-1 (new I-20 and change of status)"
        ),
        "enrollment_doc": (
            "no new I-20 is required for H-4 study; some programs still mandate "
            "transition to F-1 (and its own I-20) — confirm per program"
        ),
        "nuance": (
            "H-4 permits full-time study (no separate I-20 needed unless a program "
            "specifically requires F-1). Work requires an H-4 EAD, which is only "
            "available when the H-1B principal is past certain green-card stages. "
            "Duration is tied to the H-1B principal's status."
        ),
    },
    "L-1": {
        "label": "L-1 (intracompany transferee)",
        "maintenance_phrase": (
            "plan any full-time academic program against L-1 compatibility — "
            "typically a change of status to F-1 is cleaner for a DDS/DMD program"
        ),
        "enrollment_doc": "I-20 (after change of status from L-1)",
        "nuance": (
            "L-1 is work-only. Full-time study generally requires change of status "
            "to F-1 via the admitting program's I-20."
        ),
    },
    "L-2": {
        "label": "L-2 (dependent of L-1)",
        "maintenance_phrase": (
            "confirm the admitting program's enrollment policy for L-2 dependents "
            "— most programs permit full-time study on L-2, but some require "
            "transition to F-1 (new I-20 and change of status)"
        ),
        "enrollment_doc": (
            "no new I-20 is required for L-2 study; some programs still mandate "
            "transition to F-1 — confirm per program"
        ),
        "nuance": (
            "L-2 permits full-time study and holds work authorization (EAD-eligible "
            "for L-2 spouses). Duration is tied to the L-1 principal."
        ),
    },
    "OPT": {
        "label": "OPT / STEM-OPT (F-1 post-graduation work)",
        "maintenance_phrase": (
            "plan academic re-entry before OPT expires — transition back to F-1 "
            "via the admitting program's I-20 before the OPT window closes"
        ),
        "enrollment_doc": "I-20 (from the admitting program)",
        "nuance": (
            "OPT is time-limited F-1 post-grad work. Re-entering full-time study "
            "requires a new I-20 from the admitting school before OPT expires."
        ),
    },
    "permanent": {
        "label": "Permanent (green card / U.S. citizen)",
        "maintenance_phrase": (
            "no additional status action required — permanent residency / "
            "citizenship clears all immigration constraints"
        ),
        "enrollment_doc": "not applicable",
        "nuance": (
            "Green card / citizenship removes visa barriers entirely and typically "
            "makes the candidate FAFSA-eligible."
        ),
    },
    "B1/B2": {
        "label": "B1/B2 (visitor — blocker)",
        "maintenance_phrase": (
            "change status to F-1 via admission → I-20 → SEVIS → DS-160 → F-1 "
            "interview; B1/B2 cannot be used for study"
        ),
        "enrollment_doc": "I-20 (after change of status to F-1)",
        "nuance": (
            "B1/B2 is a hard blocker for study/work. Must change status to F-1 "
            "(or be admitted from abroad and arrive on F-1)."
        ),
    },
    "none": {
        "label": "No active visa",
        "maintenance_phrase": (
            "plan visa sequence: admission → I-20 (or DS-2019 for J-1) → SEVIS → "
            "DS-160 → F-1/J-1 visa interview"
        ),
        "enrollment_doc": "I-20 (F-1) or DS-2019 (J-1)",
        "nuance": "No current status; acquisition flow applies.",
    },
    "unknown": {
        "label": "Unknown visa status",
        "maintenance_phrase": (
            "confirm current status with the school DSO and plan the appropriate "
            "I-20 / DS-2019 / change-of-status step before CAAPID/PASS submission"
        ),
        "enrollment_doc": "depends on visa kind",
        "nuance": "Visa kind unclear — verify before planning.",
    },
}


def _active_visa_maintenance_phrase(profile: dict[str, Any] | None) -> str:
    kind = _visa_kind(profile)
    copy = _VISA_KIND_COPY.get(kind, _VISA_KIND_COPY["unknown"])
    return copy["maintenance_phrase"]


def _profile_inbde_passed(profile: dict[str, Any] | None) -> bool:
    if not profile:
        return False
    i = str(profile.get("inbdeStatus", "")).strip().lower()
    if not i:
        return False
    if "not" in i or "pending" in i or "fail" in i:
        return False
    return any(tok in i for tok in ("yes", "pass", "passed", "done", "complete"))


def _cap_readiness_overall_for_critical_blockers(score: int, profile: dict[str, Any]) -> int:
    """Prevent over-scoring when both INBDE and visa are hard blockers."""
    if _profile_has_dual_critical_blockers(profile):
        return min(score, 55)
    return score


def _ensure_biggest_lever_note(pathway: dict[str, Any], profile: dict[str, Any]) -> None:
    note = str(pathway.get("decisionNote", "")).strip()
    if "biggest lever" in note.lower():
        return

    inbde_done = _profile_inbde_passed(profile)
    visa_active = _profile_visa_is_active(profile) or _profile_visa_is_permanent(profile)

    if not _profile_has_dual_critical_blockers(profile) and (inbde_done and visa_active):
        kind = _visa_kind(profile)
        if kind in {"H-4", "L-2"}:
            transition = (
                f"secure CAAPID admission and confirm the program's enrollment policy for {kind} "
                "dependents (transition to F-1 only if the program specifically requires it)"
            )
        elif kind in {"H-1B", "L-1"}:
            transition = (
                "secure CAAPID admission and execute change of status from your current work "
                f"visa ({kind}) to F-1 via the admitting program's new I-20"
            )
        elif kind == "J-1":
            transition = (
                "secure CAAPID admission and coordinate DS-2019 transfer with your J-1 sponsor "
                "(and plan for 212(e) waiver if applicable)"
            )
        elif kind == "OPT":
            transition = (
                "secure CAAPID admission and re-enter F-1 via a fresh I-20 before OPT expires"
            )
        elif kind == "permanent":
            transition = (
                "secure CAAPID admission (no visa sequencing required thanks to permanent residency)"
            )
        else:
            transition = "secure CAAPID admission with a clean I-20 transfer to the admitting program"
        lever = (
            f"Biggest lever: verify program-specific FTD eligibility and {transition} — that "
            "converts a strong academic profile into execution readiness."
        )
    elif inbde_done and not visa_active:
        lever = (
            "Biggest lever: secure admission-led F-1 pathway (admission → I-20 → visa). "
            "INBDE is already cleared; visa sequencing is what unlocks everything else."
        )
    elif not inbde_done and visa_active:
        lever = (
            "Biggest lever: pass INBDE. Visa is already positioned; INBDE clearance is "
            "what unlocks CAAPID/PASS application readiness."
        )
    else:
        lever = (
            "Biggest lever: pass INBDE and secure an admission-led F-1 pathway "
            "(admission → I-20 → visa); this unlocks everything else."
        )
    pathway["decisionNote"] = f"{note} {lever}".strip() if note else lever


def _enforce_timeline_coverage(
    timeline: list[dict[str, str]],
    profile: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Ensure key pathway checkpoints appear somewhere across 5-6 timeline rows.

    Respects already-completed signals on the profile — we never inject a step the
    candidate has already done (INBDE pass, F-1 acquisition, etc.).
    """
    if not timeline:
        return timeline
    out = [dict(item) for item in timeline]
    blob = " ".join(
        f"{str(i.get('milestone', ''))} {str(i.get('detail', ''))}".lower() for i in out
    )

    inbde_done = _profile_inbde_passed(profile) if profile else False
    visa_active = _profile_visa_is_active(profile) if profile else False

    visa_phrase = (
        "Maintain current study/work visa status and coordinate I-20 (or DS-2019 / H-1B) "
        "transfer to the admitting program once offers land."
        if visa_active
        else "Map visa sequence explicitly: admission → I-20 → SEVIS fee → DS-160 → visa interview."
    )

    checkpoints: list[tuple[tuple[str, ...], int, str]] = [
        (("dentpin",), 0, "Create DENTPIN before any ADEA portal work."),
        (
            ("admission", "i-20", "sevis", "ds-160", "visa", "status", "maintain"),
            0,
            visa_phrase,
        ),
        (("ece", "wes", "credential"), min(1, len(out) - 1), "Complete ECE/WES credential evaluation."),
    ]

    if not inbde_done:
        checkpoints.append((
            ("inbde",),
            min(2, len(out) - 1),
            "Schedule and pass INBDE early enough to avoid compressing application execution.",
        ))

    checkpoints.extend([
        (
            ("sop", "lor", "cv"),
            min(2, len(out) - 1),
            "Prepare SOP/CV and request LORs with enough lead time before portal submission.",
        ),
        (
            ("caapid", "pass", "application", "portal"),
            min(3, len(out) - 1),
            "Submit CAAPID/PASS applications only after key prerequisites are in place.",
        ),
        (("bench", "interview"), min(4, len(out) - 1), "Complete bench-test and interview preparation."),
        (
            ("decision", "offer", "matriculation", "relocation"),
            len(out) - 1,
            "Track offers, complete onboarding, and prepare relocation/matriculation.",
        ),
    ])

    for tokens, idx, phrase in checkpoints:
        if any(t in blob for t in tokens):
            continue
        detail = str(out[idx].get("detail", "")).strip()
        out[idx]["detail"] = f"{detail} {phrase}".strip() if detail else phrase
        blob += f" {phrase.lower()}"
    return out


def _enforce_timeline_feasibility(profile: dict[str, Any], timeline: list[dict[str, str]]) -> list[dict[str, str]]:
    """Avoid unrealistically tight INBDE→apply sequencing when INBDE is not yet passed.

    Must use the shared `_profile_inbde_passed` helper: a raw `"yes"` string does
    NOT contain "pass" / "passed" / "done" as a substring, so naive substring
    checks incorrectly treated passed candidates as not-passed and injected the
    `"only if INBDE is cleared early"` caveat anyway.
    """
    if not timeline:
        return timeline
    if _profile_inbde_passed(profile):
        return timeline

    out = [dict(item) for item in timeline]
    caution = (
        "Apply in the same cycle only if INBDE is cleared early and documents "
        "(ECE/WES, SOP, LORs) are fully ready; otherwise shift to the next viable window."
    )
    for item in out:
        period = str(item.get("period", ""))
        detail = str(item.get("detail", ""))
        milestone = str(item.get("milestone", ""))
        apply_related = any(k in f"{milestone} {detail}".lower() for k in ("apply", "application", "caapid", "pass"))
        early_period = bool(re.search(r"\bQ[12]\s+20[0-9]{2}\b", period))
        if apply_related and early_period and "same cycle only if inbde is cleared early" not in detail.lower():
            item["detail"] = f"{detail} {caution}".strip()
    return out


def _normalize_myth_item(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {"myth": "", "fact": ""}
    return {"myth": str(raw.get("myth", "")).strip(), "fact": str(raw.get("fact", "")).strip()}


def _normalize_readiness_dim(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"name": "", "score": 0, "status": "", "statusColor": ""}
    score = _extract_number(raw.get("score", 0)) or 0
    score_int = int(max(0, min(100, round(score))))
    # Default the status color from the score when the model returns nothing valid.
    if score_int >= 80:
        score_default = "green"
    elif score_int >= 65:
        score_default = "teal"
    elif score_int >= 45:
        score_default = "amber"
    elif score_int > 0:
        score_default = "red"
    else:
        score_default = "gray"
    return {
        "name": str(raw.get("name", "")).strip(),
        "score": score_int,
        "status": str(raw.get("status", "")).strip(),
        "statusColor": _coerce_color(
            raw.get("statusColor", ""), _ALLOWED_DIMENSION_STATUS_COLORS, score_default
        ),
    }


def _normalize_state_card(raw: Any) -> dict[str, Any]:
    """Normalize a state card with all the new deep fields."""
    if not isinstance(raw, dict):
        return {
            "name": "", "notes": "", "competitiveness": "", "ftdFriendliness": "",
            "licenseRoute": "", "examExpectation": "", "clinicalExamNotes": "",
            "visaSponsorshipReality": "", "costOfPracticeLiving": "", "timelineHint": "",
            "priorityActions": [], "riskFlags": [], "keyPrograms": "", "reciprocityNotes": "",
        }
    return {
        "name": str(raw.get("name", "")).strip(),
        "notes": str(raw.get("notes", "")).strip(),
        "competitiveness": _normalize_competitiveness(raw.get("competitiveness", "")),
        "ftdFriendliness": str(raw.get("ftdFriendliness", "")).strip(),
        "licenseRoute": str(raw.get("licenseRoute", "")).strip(),
        "examExpectation": str(raw.get("examExpectation", "")).strip(),
        "clinicalExamNotes": str(raw.get("clinicalExamNotes", "")).strip(),
        "visaSponsorshipReality": str(raw.get("visaSponsorshipReality", "")).strip(),
        "costOfPracticeLiving": str(raw.get("costOfPracticeLiving", "")).strip(),
        "timelineHint": str(raw.get("timelineHint", "")).strip(),
        "priorityActions": _list_of_strings(raw.get("priorityActions", [])),
        "riskFlags": _list_of_strings(raw.get("riskFlags", [])),
        "keyPrograms": str(raw.get("keyPrograms", "")).strip(),
        "reciprocityNotes": str(raw.get("reciprocityNotes", "")).strip(),
    }


def _enrich_state_card(card: dict[str, Any]) -> dict[str, Any]:
    """Backfill ONLY missing fields with neutral, verification-first defaults.

    No hardcoded per-state facts — state content comes from the model under the
    prompt rules. These defaults exist only so the schema is fully populated when
    the model omits a field; they explicitly tell the candidate to verify with
    official sources rather than asserting state-specific claims.
    """
    name = card.get("name", "").strip()
    state_label = name or "this state"

    def fb(key: str, default: str) -> str:
        v = card.get(key)
        if isinstance(v, str) and v.strip():
            return v
        return default

    return {
        "name": name,
        "notes": fb("notes",
            f"State-specific board rules determine FTD eligibility in {state_label}. "
            f"Verify exam route, documentation sequence, and latest policy updates "
            f"with the state dental board and the ADEA CAAPID program list."),
        "competitiveness": _normalize_competitiveness(
            card.get("competitiveness") or "Moderate"
        ),
        "ftdFriendliness": fb("ftdFriendliness",
            f"Verify FTD pathway availability for {state_label} on the current ADEA CAAPID program list and with the state board before assuming an in-state IDP route."),
        "licenseRoute": fb("licenseRoute",
            f"Typical route: DDS/DMD from a CODA-accredited program + INBDE + a clinical exam accepted by the {state_label} dental board + state jurisprudence. Verify current acceptance with the board before scheduling."),
        "examExpectation": fb("examExpectation",
            f"Confirm the clinical exam(s) currently accepted by the {state_label} dental board (e.g., CDCA, ADEX, WREB legacy) and any jurisprudence/law-and-ethics requirement on the board's official site."),
        "clinicalExamNotes": fb("clinicalExamNotes",
            "Clinical-exam policies and accepted regional boards have shifted across U.S. states recently; rely on the state dental board's current guidance, not forum posts."),
        "visaSponsorshipReality": fb("visaSponsorshipReality",
            "H-1B/J-1 sponsorship and Conrad 30 waiver availability vary by employer, metro, and year. Treat any specific sponsorship or waiver claim as something to verify directly with the prospective employer or the state's HRSA program."),
        "costOfPracticeLiving": fb("costOfPracticeLiving",
            "Verify dentist compensation benchmarks (BLS / ADA salary surveys) and the state's actual income-tax posture before financial planning."),
        "timelineHint": fb("timelineHint",
            f"Start {state_label}-specific board, exam, and CAAPID/PASS planning 12+ months before your target cycle."),
        "priorityActions": card.get("priorityActions") or [
            f"Verify {state_label} dental board licensure requirements directly from the board's official website.",
            "Confirm whether any in-state dental school currently participates in ADEA CAAPID for the cycle you are targeting.",
            "Align licensure sequencing with your visa and financing constraints before committing to schools or exams.",
        ],
        "riskFlags": card.get("riskFlags") or [
            "Assuming state rules are static can cause late-stage rework.",
            "In-state IDP availability changes year to year — confirm via ADEA CAAPID rather than assuming.",
        ],
        "keyPrograms": fb("keyPrograms",
            f"Verify the current list of CAAPID-listed IDP programs and CODA-accredited GPR/AEGD/specialty programs in {state_label} on the official ADEA CAAPID and CODA sources before targeting any specific school."),
        "reciprocityNotes": fb("reciprocityNotes",
            "License portability depends on which clinical exam you complete and each receiving state's rules. Verify before relocating."),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fallbacks
# ─────────────────────────────────────────────────────────────────────────────


def _default_readiness_status(score: int) -> str:
    if score >= 85:
        return "High readiness with targeted refinements needed"
    if score >= 70:
        return "Strong potential but not fully application-ready yet"
    if score >= 55:
        return "Promising but not application-ready yet"
    return "Early stage profile; foundational gaps must be closed first"


def _fallback_ranked_pathways(
    profile: dict[str, Any],
    pathway: dict[str, Any],
    risks: list[dict[str, str]],
) -> list[dict[str, Any]]:
    visa = profile.get("visaStatus", "Not specified") or "Not specified"
    cosigner = profile.get("loanCosigner", "Not specified") or "Not specified"
    primary = pathway.get("primaryPathway") or "DDS/DMD (International Dentist Program)"
    secondary = pathway.get("secondaryStrategy") or "Master's bridge to DDS/DMD"

    has_fin_risk = any(
        "financ" in r.get("issue", "").lower() or "loan" in r.get("issue", "").lower()
        for r in risks
    )
    fin_blocker = "No confirmed funding route yet" if has_fin_risk else "Funding specifics unassessed"

    return [
        {
            "rank": 1, "rankLabel": "1st", "pathTitle": primary,
            "fitSummary": "Best long-term licensure flexibility if admission profile is strengthened.",
            "applicationPortal": "ADEA CAAPID",
            "requirementsStillNeeded": [
                "Program-ready application package (SOP + LORs + school fit list)",
                "Verified financing route aligned to total program cost",
                "Timeline-aligned visa and admissions execution plan",
            ],
            "blockers": [f"Current visa status: {visa}", f"Cosigner status: {cosigner}", fin_blocker],
            "realityCheck": "High-upside route; outcomes depend on execution quality and affordability.",
            "bestUseCase": "Build a complete, finance-ready application profile.",
            "isPrimary": True,
        },
        {
            "rank": 2, "rankLabel": "2nd", "pathTitle": secondary,
            "fitSummary": "Practical bridge when direct DDS competitiveness or logistics are not ready.",
            "applicationPortal": "Institution-specific",
            "requirementsStillNeeded": [
                "Select master's programs that improve DDS readiness signals",
                "Build U.S.-anchored recommendations and academic narrative",
                "Convert bridge outcomes into a targeted DDS reapplication strategy",
            ],
            "blockers": [
                "Master's choice must directly support downstream DDS positioning",
                "Adds time and cost if chosen without a DDS-backward plan",
            ],
            "realityCheck": "Excellent strategy only when each master's milestone maps to a DDS outcome.",
            "bestUseCase": "Candidates needing profile strengthening with structured timeline.",
            "isPrimary": False,
        },
        {
            "rank": 3, "rankLabel": "3rd", "pathTitle": "GPR / AEGD Residency",
            "fitSummary": "Exploratory clinical pathway with state-specific licensure potential.",
            "applicationPortal": "ADEA PASS",
            "requirementsStillNeeded": [
                "J-1 visa sponsorship from program",
                "Board-by-board verification for every target state",
            ],
            "blockers": [
                "J-1 home-country requirement may apply",
                "Not equivalent to DDS/DMD for licensure in all states",
            ],
            "realityCheck": "Treat as complement to DDS, not a DDS replacement.",
            "bestUseCase": "Experienced candidates seeking immediate U.S. clinical exposure.",
            "isPrimary": False,
        },
    ]


def _fallback_dentnav_services(profile: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    visa = profile.get("visaStatus", "").strip().lower()
    states = _list_of_strings(profile.get("preferredStates"))
    states_text = ", ".join(states) if states else "preferred states"
    return {
        "neededNow": [
            {
                "service": "Visa strategy guidance",
                "reason": (
                    "F-1 via master's is the critical unblock"
                    if visa in {"none", "not specified", "unknown", ""}
                    else "Map current visa to education and licensing constraints"
                ),
                "timing": "",
            },
            {"service": "DENTPIN creation", "reason": "First step before any ADEA portal", "timing": ""},
            {"service": "ECE evaluation", "reason": "Required for ADEA CAAPID application", "timing": ""},
        ],
        "neededLater": [
            {"service": "SOP, CV & recommendation letters", "reason": "Application season prep", "timing": "Early 2027"},
            {"service": "Bench test training", "reason": "Required for most IDP programs", "timing": "Mid 2027"},
            {"service": "Mock interviews", "reason": "Critical for program selection", "timing": "Mid 2027"},
            {"service": "State licensure guidance", "reason": f"Verify {states_text} boards", "timing": "Ongoing"},
        ],
    }


def _fallback_application_timeline(profile: dict[str, Any]) -> list[dict[str, str]]:
    cycle = str(profile.get("targetCycle", "")).strip()
    milestones = [
        ("red", "DENTPIN + visa strategy",
         "Create DENTPIN. Research U.S. master's / IDP options that can issue an I-20 (admission → I-20 → SEVIS fee → DS-160 → F-1 visa interview)."),
        ("amber", "Credential evaluation + profile build",
         "Start ECE/WES. Secure visa pathway. Strengthen observerships and CV."),
        ("purple", "INBDE + SOP/CV/LOR readiness",
         "Pass INBDE and complete SOP/CV/LOR preparation with enough lead time before submission windows."),
        ("purple", "ADEA CAAPID / PASS portal season",
         "Finalize submissions only after INBDE + core documents are ready; if INBDE clears late, shift to the next viable cycle."),
        ("teal", "Bench tests + interviews",
         "Program-specific practical assessments and interviews."),
        ("teal", "Decisions + matriculation prep",
         "Respond to offers; plan relocation and onboarding for the intake year."),
    ]

    if not cycle.isdigit():
        cy, _ = _current_year_quarter()
        labels = ["Now", f"By Q4 {cy}", f"By Q4 {cy + 1}", f"By Q4 {cy + 2}", f"By Q4 {cy + 3}", f"By Q4 {cy + 4}"]
    else:
        labels = _year_quarter_period_labels(int(cycle), len(milestones))

    return [
        {"period": labels[i], "periodColor": color, "milestone": ms, "detail": detail}
        for i, (color, ms, detail) in enumerate(milestones)
    ]


def _fallback_myth_warnings(profile: dict[str, Any]) -> list[dict[str, str]]:
    states = _list_of_strings(profile.get("preferredStates"))
    states_note = ", ".join(states) if states else "your target states"
    return [
        {
            "myth": "INBDE score determines which program I get",
            "fact": "INBDE is pass/fail only. Your SOP, clinical background, bench test, and interview determine selection.",
        },
        {
            "myth": "DDS/DMD automatically gives me a license in all 50 states",
            "fact": f"A degree qualifies you to apply. Each state board has its own rules. {states_note} must be verified separately.",
        },
        {
            "myth": "Completing DDS leads to a green card",
            "fact": "Immigration depends on visa category and employer sponsorship — not the dental degree.",
        },
    ]


def _fallback_state_planning(profile: dict[str, Any]) -> dict[str, Any]:
    states = _list_of_strings(profile.get("preferredStates"))[:3]
    if not states:
        states = ["Target State 1", "Target State 2", "Target State 3"]
    return {
        "note": (
            f"State licensure rules vary meaningfully across {', '.join(states)}. Each has its own "
            f"clinical exam acceptance, visa sponsorship reality, and cost/competitiveness profile. "
            f"Verify directly with each state's dental board before committing."
        ),
        "states": [_enrich_state_card({"name": s}) for s in states],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Profile snapshot
# ─────────────────────────────────────────────────────────────────────────────


def _build_profile_snapshot(parsed: dict[str, Any], answers: AnswerMap) -> dict[str, Any]:
    country = str(answers.get("q1-degree-country", "")).strip()
    degree = str(answers.get("q1b-degree-type", "")).strip()
    years = str(answers.get("q7-clinical-years", "")).strip()
    target = str(answers.get("q2-target-program", "")).strip()
    visa = str(answers.get("q4-visa", "")).strip()
    masters = str(answers.get("q5-masters-vs-home", "")).strip()
    cosigner = str(answers.get("q6-loan-cosigner", "")).strip()
    inbde = str(answers.get("q8-inbde", "")).strip()
    toefl = str(answers.get("q9-toefl", "")).strip()
    cycle = str(answers.get("q10-start-cycle", "")).strip()
    states = _list_of_strings(answers.get("q3-practice-states", []))
    toefl_legacy = _toefl_band_to_legacy_total(toefl)

    target_lower = target.lower()
    if "i don't know" in target_lower or "guidance" in target_lower:
        badge = "Needs guidance"
    elif target:
        badge = "Defined"
    else:
        badge = "Not specified"

    masters_lower = masters.lower()
    if "master" in masters_lower:
        entry_mode = "Pursue master's degree in U.S. first"
    elif "home" in masters_lower or "abroad" in masters_lower:
        entry_mode = "Apply from home country"
    else:
        entry_mode = masters or "Not specified"

    snapshot = {
        "country": country or "Unknown",
        "degree": degree or "Not specified",
        "clinicalExperience": years or "Not specified",
        "targetProgram": target or "Not specified",
        "programIntentBadge": badge,
        "entryMode": entry_mode,
        "preferredStates": states,
        "visaStatus": visa or "Not specified",
        "mastersInterest": masters or "Not specified",
        "loanCosigner": cosigner or "Not specified",
        "inbdeStatus": inbde or "Not specified",
        "toeflScore": toefl or "Not specified",
        "toeflLegacyEquivalent120": f"{toefl_legacy}/120" if toefl_legacy is not None else "",
        "targetCycle": cycle or "Not specified",
    }

    profile_raw = parsed.get("profileSnapshot", {})
    if isinstance(profile_raw, dict):
        for key in ("programIntentBadge", "entryMode"):
            v = str(profile_raw.get(key, "")).strip()
            if v:
                snapshot[key] = v

    snapshot["programIntentBadge"] = _coerce_program_intent_badge(
        snapshot.get("programIntentBadge", ""), snapshot.get("targetProgram", "")
    )

    # Lock entryMode to our derived value when the user clearly chose master's vs home.
    masters_l = str(snapshot.get("mastersInterest", "")).lower()
    if "master" in masters_l:
        snapshot["entryMode"] = "Pursue master's degree in U.S. first"
    elif "home" in masters_l or "abroad" in masters_l:
        snapshot["entryMode"] = "Apply from home country"

    return snapshot


# ─────────────────────────────────────────────────────────────────────────────
# Completed-signal enforcement (HARD RULES 42–46 post-processor)
# ─────────────────────────────────────────────────────────────────────────────


_INBDE_PENDING_PHRASES = (
    "pass inbde", "passing inbde", "schedule inbde", "scheduling inbde",
    "take inbde", "taking inbde", "prepare for inbde", "preparing for inbde",
    "inbde timing", "inbde preparation", "inbde readiness", "inbde not passed",
    "clear inbde", "clearing inbde", "complete inbde",
)

_F1_ACQUISITION_PHRASES = (
    "apply for f-1", "apply for f1", "apply for an f-1", "apply for an f1",
    "file for f-1", "file for f1", "begin f-1", "begin f1", "start f-1",
    "start f1", "secure an i-20", "secure i-20", "obtain an i-20",
    "obtain i-20", "plan the f-1 visa sequence", "plan f-1 visa sequence",
    "plan f1 visa sequence", "f-1 visa sequence", "f1 visa sequence",
    "initiate f-1", "initiate f1", "pursue f-1", "pursue f1",
    "visa sequence: admission", "admission → i-20", "admission -> i-20",
    "admission to i-20",
)

_VAGUE_BLOCKER_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE) for p in (
        r"^\s*none\b",
        r"^\s*no\s+(significant|major|hard|real)\s+blockers?\b",
        r"^\s*no\s+blockers?\b",
        r"^\s*nothing\s+significant\b",
        r"^\s*n/?a\b",
        r"^\s*not\s+applicable\b",
    )
)


def _blocker_is_vague(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return True
    return any(p.search(v) for p in _VAGUE_BLOCKER_PATTERNS)


def _item_is_about_done_step(
    text: str,
    inbde_done: bool,
    visa_active: bool,
) -> bool:
    """True if the given free-form action text is primarily about acquiring a
    capability the candidate already has (and therefore should be dropped)."""
    t = text.lower()
    if inbde_done and any(p in t for p in _INBDE_PENDING_PHRASES):
        return True
    if visa_active and any(p in t for p in _F1_ACQUISITION_PHRASES):
        return True
    return False


def _drop_done_action_items(items: list[str], profile: dict[str, Any]) -> list[str]:
    inbde_done = _profile_inbde_passed(profile)
    visa_active = _profile_visa_is_active(profile) or _profile_visa_is_permanent(profile)
    if not inbde_done and not visa_active:
        return items
    return [it for it in items if not _item_is_about_done_step(str(it), inbde_done, visa_active)]


def _drop_done_timeline_rows(
    timeline: list[dict[str, str]], profile: dict[str, Any]
) -> list[dict[str, str]]:
    inbde_done = _profile_inbde_passed(profile)
    visa_active = _profile_visa_is_active(profile) or _profile_visa_is_permanent(profile)
    if not inbde_done and not visa_active:
        return timeline
    out: list[dict[str, str]] = []
    for row in timeline:
        milestone = str(row.get("milestone", ""))
        detail = str(row.get("detail", ""))
        combined = f"{milestone} {detail}"
        if _item_is_about_done_step(combined, inbde_done, visa_active):
            # If the milestone is purely about a completed step, drop the row
            # entirely. If the detail has other forward-looking content, keep
            # the row but let text rewrites handle the residual phrasing.
            if _item_is_about_done_step(milestone, inbde_done, visa_active):
                continue
        out.append(row)
    return out


def _clean_ranked_pathway_blockers(
    ranked: list[dict[str, Any]], profile: dict[str, Any]
) -> list[dict[str, Any]]:
    target_lower = str(profile.get("targetProgram", "")).lower()
    specialty_target = "specialty" in target_lower
    visa_active = _profile_visa_is_active(profile)
    visa_permanent = _profile_visa_is_permanent(profile)
    kind = _visa_kind(profile)

    def _admission_blocker_phrase() -> str:
        if kind == "F-1":
            return "CAAPID admission and I-20 transfer to the admitting program not yet secured"
        if kind == "F-2":
            return "CAAPID admission and school-specific F-2 vs F-1 enrollment requirement not yet confirmed"
        if kind == "J-1":
            return "CAAPID admission and DS-2019 transfer with your J-1 sponsor not yet secured"
        if kind in {"H-4", "L-2"}:
            return f"CAAPID admission and per-program enrollment policy for {kind} dependents not yet confirmed"
        if kind == "H-1B":
            return "CAAPID admission and change-of-status plan from H-1B to F-1 not yet executed"
        if kind == "L-1":
            return "CAAPID admission and change-of-status plan from L-1 to F-1 not yet executed"
        if kind == "OPT":
            return "CAAPID admission and fresh F-1 I-20 before OPT expires not yet secured"
        if kind == "permanent":
            return "CAAPID admission not yet secured (program shortlist, SOP, LORs)"
        return "CAAPID admission and admission-led visa sequence not yet secured"

    def _visa_blocker_phrase() -> str | None:
        if visa_permanent:
            return None
        if kind in {"H-4", "L-2"}:
            return f"Per-program enrollment policy for {kind} dependents not yet confirmed (some programs require F-1 transition)"
        if kind == "H-1B":
            return "Change of status from H-1B to F-1 not yet executed"
        if kind == "L-1":
            return "Change of status from L-1 to F-1 not yet executed"
        if kind == "OPT":
            return "OPT-window timing vs. academic start date not yet aligned (new I-20 required before expiry)"
        if kind in {"F-1", "J-1"}:
            return None  # active study visa — no hard blocker beyond normal transfer mechanics
        return "Active study/work visa status not yet secured"

    def _default_blockers_for(path_title: str) -> list[str]:
        title_l = path_title.lower()
        blockers: list[str] = []
        if "specialty" in title_l:
            blockers.append(
                "Specialty program-specific FTD eligibility not yet verified (program-by-program)"
            )
            blockers.append("Competitive specialty credentials (CBSE / research / publications) not yet documented")
        elif "master" in title_l:
            blockers.append("U.S. master's is a bridge, not a licensure path — does not by itself qualify for state licensure")
            blockers.append("Program fit with dental career goals still to be confirmed")
        else:  # DDS/DMD IDP and generic
            blockers.append(_admission_blocker_phrase())
            blockers.append("ECE/WES assembly, SOP/LOR, and school shortlist not yet finalized")
            if specialty_target:
                blockers.append("Specialty preference requires separate program-by-program eligibility check post-DDS/DMD")
        if not visa_active:
            extra = _visa_blocker_phrase()
            if extra:
                blockers.append(extra)
        return blockers[:2] if blockers else ["Conditional on program-by-program CAAPID/PASS verification"]

    cleaned: list[dict[str, Any]] = []
    for item in ranked:
        raw_blockers = item.get("blockers")
        values = raw_blockers if isinstance(raw_blockers, list) else []
        filtered = [
            str(v).strip()
            for v in values
            if str(v).strip() and not _blocker_is_vague(str(v))
        ]
        if not filtered:
            filtered = _default_blockers_for(str(item.get("pathTitle", "")))
        item = dict(item)
        item["blockers"] = filtered
        cleaned.append(item)
    return cleaned


def _rewrite_visa_risk_for_active_visa(
    risks: list[dict[str, Any]], profile: dict[str, Any]
) -> list[dict[str, Any]]:
    is_active = _profile_visa_is_active(profile)
    is_permanent = _profile_visa_is_permanent(profile)
    if not (is_active or is_permanent):
        return risks
    out: list[dict[str, Any]] = []
    for risk in risks:
        issue = str(risk.get("issue", ""))
        issue_l = issue.lower()
        is_visa_risk = any(k in issue_l for k in ("visa", "immigration", "f-1", "f1", "h-4", "h4", "j-1", "j1", "h-1b", "h1b", "l-2", "l2", "opt"))
        if not is_visa_risk:
            out.append(risk)
            continue
        if is_permanent:
            # Permanent residents / citizens have no visa risk by definition. Drop.
            continue
        new = dict(risk)
        # Rewrite headline to alignment/maintenance framing.
        new["issue"] = "Visa alignment with program requirements"
        impact_raw = str(new.get("impact") or "").strip().lower()
        bad_impact_markers = (
            "high", "critical", "study/work limitation", "blocker", "blocked",
            "status maintenance requirement", "maintenance requirement", "limitation",
        )
        if impact_raw in {"high", "critical", "blocker", "blocked"} or any(m in impact_raw for m in bad_impact_markers):
            new["impact"] = "Alignment required"
        if (new.get("impactColor") or "").lower() == "red":
            new["impactColor"] = "amber"
        note = str(new.get("note", ""))
        if note:
            new["note"] = _rewrite_active_visa_phrasing(note, profile)
        out.append(new)
    return out


def _drop_inbde_gap_when_done(
    readiness: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    if not _profile_inbde_passed(profile):
        return readiness
    if not isinstance(readiness, dict):
        return readiness
    out = dict(readiness)
    gaps = out.get("gaps")
    if isinstance(gaps, list):
        out["gaps"] = [
            g for g in gaps
            if not any(p in str(g).lower() for p in _INBDE_PENDING_PHRASES)
            and "inbde" not in str(g).lower()
        ]
    return out


def _drop_inbde_risk_when_done(
    risks: list[dict[str, Any]], profile: dict[str, Any]
) -> list[dict[str, Any]]:
    if not _profile_inbde_passed(profile):
        return risks
    out: list[dict[str, Any]] = []
    for risk in risks:
        issue_l = str(risk.get("issue", "")).lower()
        note_l = str(risk.get("note", "")).lower()
        if "inbde" in issue_l and any(p in issue_l + " " + note_l for p in _INBDE_PENDING_PHRASES + ("not passed", "pending")):
            continue
        out.append(risk)
    return out


_INBDE_CONDITIONAL_CAVEAT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?i)[,;\s]*Apply\s+in\s+the\s+same\s+cycle\s+only\s+if\s+INBDE\s+is\s+cleared\s+early\s+"
        r"and\s+documents\s*\([^)]*\)\s+are\s+fully\s+ready\s*;\s*otherwise\s+shift\s+to\s+the\s+next\s+viable\s+window\.?\s*"
    ),
    re.compile(r"(?i)\s*only\s+if\s+INBDE\s+is\s+cleared\s+early\b[^.]*\.?"),
    re.compile(r"(?i)\bbefore\s+INBDE\s+(?:clears|passes)\b"),
)


def _strip_inbde_conditional_caveats_when_done(
    response: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """Strip any residual 'only if INBDE is cleared early' style caveats when INBDE passed."""
    if not _profile_inbde_passed(profile):
        return response

    def _scrub(text: str) -> str:
        out = text
        for pat in _INBDE_CONDITIONAL_CAVEAT_PATTERNS:
            out = pat.sub(" ", out)
        return re.sub(r"\s{2,}", " ", out).strip()

    timeline = response.get("applicationTimeline")
    if isinstance(timeline, list):
        for row in timeline:
            if isinstance(row, dict):
                detail = row.get("detail")
                if isinstance(detail, str):
                    row["detail"] = _scrub(detail)

    for key in ("next90DaysPlan", "next12To18Months"):
        items = response.get(key)
        if isinstance(items, list):
            response[key] = [_scrub(str(it)) for it in items if _scrub(str(it))]

    return response


_INBDE_STRENGTH_SENTENCE = (
    "INBDE completion materially strengthens your DDS/DMD application competitiveness — "
    "most IDP candidates never clear this bar, so having it already compounds every other strength."
)


def _ensure_inbde_strength_emphasis(
    response: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """When INBDE passed and target is DDS/DMD or specialty, make sure expertConclusion
    and readinessScore.strengths explicitly name INBDE as a compounding strength."""
    if not _profile_inbde_passed(profile):
        return response

    target = str(profile.get("targetProgram", "")).lower()
    if not any(k in target for k in ("dds", "dmd", "idp", "specialty", "residency")):
        return response

    conclusion = response.get("expertConclusion")
    if isinstance(conclusion, str):
        lower = conclusion.lower()
        if "inbde" not in lower or "strengthen" not in lower:
            conclusion = conclusion.rstrip()
            if conclusion and not conclusion.endswith((".", "!", "?")):
                conclusion += "."
            conclusion = f"{conclusion} {_INBDE_STRENGTH_SENTENCE}".strip()
            response["expertConclusion"] = conclusion

    readiness = response.get("readinessScore")
    if isinstance(readiness, dict):
        strengths = readiness.get("strengths")
        if isinstance(strengths, list):
            has_inbde = any("inbde" in str(s).lower() for s in strengths)
            if not has_inbde:
                readiness["strengths"] = ["INBDE passed (filters out most competing applicants)", *strengths]

    return response


_I20_MISUSE_FOR_DEPENDENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\bsecure\s+(?:admission\s+and\s+)?coordinate\s+I[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?4(?:\s+visa)?(?:\s+alignment)?"),
    re.compile(r"(?i)\bsecure\s+(?:admission\s+and\s+)?coordinate\s+I[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2(?:\s+visa)?(?:\s+alignment)?"),
    re.compile(r"(?i)\bcoordinate\s+I[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?4(?:\s+visa)?(?:\s+alignment)?"),
    re.compile(r"(?i)\bcoordinate\s+I[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2(?:\s+visa)?(?:\s+alignment)?"),
    re.compile(r"(?i)\bI[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?H[-\s]?4(?:\s+visa)?(?:\s+alignment)?"),
    re.compile(r"(?i)\bI[-\s]?20\s+transfer\s+for\s+(?:an?\s+|the\s+|your\s+)?L[-\s]?2(?:\s+visa)?(?:\s+alignment)?"),
    re.compile(r"(?i)\balign\s+H[-\s]?4\s+visa\s+with\s+I[-\s]?20"),
    re.compile(r"(?i)\bH[-\s]?4\s+visa\s+I[-\s]?20\s+transfer"),
    # Residual trailing " visa alignment" after a partial replacement leaves hanging phrase.
    re.compile(r"(?i)\bresid(?:e|ue)\s+visa\s+alignment\b"),
)


def _strip_i20_misuse_for_dependents(
    response: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """Always strip 'I-20 transfer for H-4/L-2' phrasing from anywhere in the
    payload — it is factually wrong for H-4/L-2 holders AND nonsensical for
    candidates who hold a different visa. The replacement is profile-aware:
    for H-4/L-2 candidates we use their enrollment phrase; for everyone else
    we substitute a neutral 'align visa status with program requirements'.
    """
    kind = _visa_kind(profile)
    if kind in {"H-4", "L-2"}:
        replacement = _visa_specific_enrollment_rewrite(profile) or (
            "ensure enrollment documentation aligns with your current dependent status"
        )
    elif kind == "F-1":
        replacement = (
            "maintain F-1 status and coordinate I-20 transfer to the admitting program"
        )
    elif kind in {"H-1B", "L-1"}:
        replacement = (
            f"plan change of status from {kind} to F-1 via the admitting program's I-20"
        )
    elif kind == "J-1":
        replacement = (
            "coordinate DS-2019 transfer with your J-1 sponsor and the admitting program"
        )
    elif kind == "OPT":
        replacement = (
            "plan academic re-entry on a fresh I-20 from the admitting program before OPT expires"
        )
    elif kind == "permanent":
        replacement = "no visa action required — permanent residency clears immigration constraints"
    else:
        replacement = "align visa status with admitting program's requirements"

    def _walk(obj: Any) -> Any:
        if isinstance(obj, str):
            out = obj
            for pat in _I20_MISUSE_FOR_DEPENDENT_PATTERNS:
                out = pat.sub(replacement, out)
            if out != obj:
                out = _clean_rewritten_text(out)
            return out
        if isinstance(obj, list):
            return [_walk(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _walk(v) for k, v in obj.items()}
        return obj

    return _walk(response)


_INBDE_RESIDUAL_IN_BLOCKERS = re.compile(r"(?i)\bINBDE\b")


def _strip_inbde_from_primary_blockers_when_done(
    response: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """Ranked-pathway blockers for completed INBDE must never say 'INBDE not passed'."""
    if not _profile_inbde_passed(profile):
        return response
    pathway = response.get("pathwayRecommendation")
    if not isinstance(pathway, dict):
        return response
    ranked = pathway.get("rankedPathways")
    if not isinstance(ranked, list):
        return response
    for item in ranked:
        if not isinstance(item, dict):
            continue
        blockers = item.get("blockers")
        if isinstance(blockers, list):
            item["blockers"] = [
                b for b in blockers
                if not (_INBDE_RESIDUAL_IN_BLOCKERS.search(str(b))
                        and any(p in str(b).lower() for p in ("not passed", "pending", "timing", "schedul", "clear")))
            ]
        reqs = item.get("requirementsStillNeeded")
        if isinstance(reqs, list):
            item["requirementsStillNeeded"] = [
                r for r in reqs
                if not (_INBDE_RESIDUAL_IN_BLOCKERS.search(str(r))
                        and any(p in str(r).lower() for p in ("pass", "take", "schedul", "clear", "prepare")))
            ]
    return response


def _enforce_f2_nuance_and_dds_wording(
    response: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """Apply hard deterministic cleanup for F-2 profiles.

    Guarantees:
    - F-2 nuance sentence exists in visa-related risk wording.
    - Visa readiness dimension is not over-scored and explicitly calls out
      F-2 limited-study + likely F-1 transition reality.
    - "Direct DDS/DMD not viable without F-1" style absolutes are rewritten.
    """
    if _visa_kind(profile) != "F-2":
        return response

    nuance = (
        "F-2 allows limited study but often requires transition to F-1 for full "
        "program participation."
    )

    risks = response.get("mainRisks")
    if isinstance(risks, list):
        found_visa_risk = False
        for idx, risk in enumerate(risks):
            if not isinstance(risk, dict):
                continue
            issue_l = str(risk.get("issue", "")).lower()
            if any(k in issue_l for k in ("visa", "immigration", "f-2", "f2")):
                found_visa_risk = True
                updated = dict(risk)
                updated["issue"] = "Visa alignment with program requirements"
                updated["impactColor"] = "amber"
                note = str(updated.get("note", "")).strip()
                if nuance.lower() not in note.lower():
                    note = f"{note.rstrip('.')} {nuance}".strip()
                updated["note"] = note
                if str(updated.get("impact", "")).strip().lower() in {"high", "critical", "blocker", "blocked", "study/work limitation"}:
                    updated["impact"] = "Alignment required"
                risks[idx] = updated
                break
        if not found_visa_risk:
            risks.insert(0, {
                "issue": "Visa alignment with program requirements",
                "impact": "Alignment required",
                "impactColor": "amber",
                "note": nuance,
                "evidenceBasis": "Profile indicates active F-2 dependent visa status.",
                "assessmentType": "Evidence-Based",
            })
        response["mainRisks"] = risks

    readiness = response.get("readinessScore")
    if isinstance(readiness, dict):
        dims = readiness.get("dimensions")
        if isinstance(dims, list):
            for dim in dims:
                if not isinstance(dim, dict):
                    continue
                name_l = str(dim.get("name", "")).lower()
                if "visa" not in name_l and "immigration" not in name_l:
                    continue
                raw = _extract_number(dim.get("score"))
                score = int(raw) if raw is not None else 58
                dim["score"] = max(50, min(65, score))
                dim["statusColor"] = "amber"
                dim["status"] = "Active F-2: limited study; often requires F-1 transition"
                break

    pathway = response.get("pathwayRecommendation")
    if isinstance(pathway, dict):
        for key in ("decisionNote", "verdict", "bestPathwayForYou", "secondaryStrategy"):
            val = pathway.get(key)
            if isinstance(val, str) and val.strip():
                pathway[key] = _rewrite_dds_f1_false_blockers(val)
        why_not = pathway.get("whyNotAlternatives")
        if isinstance(why_not, list):
            pathway["whyNotAlternatives"] = [
                _rewrite_dds_f1_false_blockers(str(item)) for item in why_not
            ]
        ranked = pathway.get("rankedPathways")
        if isinstance(ranked, list):
            for item in ranked:
                if not isinstance(item, dict):
                    continue
                req = item.get("requirementsStillNeeded")
                if isinstance(req, list):
                    item["requirementsStillNeeded"] = [
                        _rewrite_dds_f1_false_blockers(str(r)) for r in req
                    ]
                blockers = item.get("blockers")
                if isinstance(blockers, list):
                    item["blockers"] = [
                        _rewrite_dds_f1_false_blockers(str(b)) for b in blockers
                    ]
        response["pathwayRecommendation"] = pathway

    response = _apply_reasoning_guards_tree(response, profile)
    return response


def _enforce_completed_signals(
    response: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """Final structural pass: drop/rewrite any items that contradict already-completed
    profile signals (INBDE pass, active study/work visa) and enforce blockers discipline."""
    if not isinstance(response, dict):
        return response

    response["next90DaysPlan"] = _drop_done_action_items(
        _list_of_strings(response.get("next90DaysPlan")), profile
    )
    response["next12To18Months"] = _drop_done_action_items(
        _list_of_strings(response.get("next12To18Months")), profile
    )

    timeline = response.get("applicationTimeline")
    if isinstance(timeline, list):
        response["applicationTimeline"] = _drop_done_timeline_rows(timeline, profile)

    pathway = response.get("pathwayRecommendation")
    if isinstance(pathway, dict):
        ranked = pathway.get("rankedPathways")
        if isinstance(ranked, list):
            pathway["rankedPathways"] = _clean_ranked_pathway_blockers(ranked, profile)

    risks = response.get("mainRisks")
    if isinstance(risks, list):
        risks = _drop_inbde_risk_when_done(risks, profile)
        risks = _rewrite_visa_risk_for_active_visa(risks, profile)
        response["mainRisks"] = risks

    readiness = response.get("readinessScore")
    if isinstance(readiness, dict):
        response["readinessScore"] = _drop_inbde_gap_when_done(readiness, profile)

    # INBDE-conditional caveats that leaked through text rewrites.
    response = _strip_inbde_conditional_caveats_when_done(response, profile)
    # I-20 misuse for dependent visas.
    response = _strip_i20_misuse_for_dependents(response, profile)
    # Residual INBDE items in pathway blockers / requirements.
    response = _strip_inbde_from_primary_blockers_when_done(response, profile)
    # INBDE strength emphasis in expertConclusion when passed.
    response = _ensure_inbde_strength_emphasis(response, profile)
    # F-2 deterministic guardrails.
    response = _enforce_f2_nuance_and_dds_wording(response, profile)

    return response


# ─────────────────────────────────────────────────────────────────────────────
# Full response normalization
# ─────────────────────────────────────────────────────────────────────────────


def _normalize_response(parsed: dict[str, Any], answers: AnswerMap) -> dict[str, Any]:
    profile = _build_profile_snapshot(parsed, answers)

    readiness_raw = parsed.get("readinessScore", {}) if isinstance(parsed.get("readinessScore"), dict) else {}
    performance = int(max(35, min(95, round(
        _extract_number(readiness_raw.get("overall")) or _estimate_performance_from_answers(answers)
    ))))
    performance = _cap_readiness_overall_for_critical_blockers(performance, profile)
    readiness_status = str(readiness_raw.get("status", "")).strip() or _default_readiness_status(performance)

    dims_raw = readiness_raw.get("dimensions", [])
    readiness_dims: list[dict[str, Any]] = []
    if isinstance(dims_raw, list):
        readiness_dims = [
            _normalize_readiness_dim(d) for d in dims_raw
            if isinstance(d, dict) and (d.get("name") or d.get("score") is not None)
        ]
    if not readiness_dims:
        readiness_dims = _compute_readiness_dimensions(answers)

    pathway_raw = parsed.get("pathwayRecommendation", {}) if isinstance(parsed.get("pathwayRecommendation"), dict) else {}
    pathway = {
        "primaryPathway": str(pathway_raw.get("primaryPathway", "")).strip(),
        "bestPathwayForYou": str(pathway_raw.get("bestPathwayForYou", "")).strip(),
        "verdict": str(pathway_raw.get("verdict", "")).strip(),
        "decisionNote": str(pathway_raw.get("decisionNote", "")).strip(),
        "secondaryStrategy": str(pathway_raw.get("secondaryStrategy", "")).strip(),
        "applicationPortal": str(pathway_raw.get("applicationPortal", "")).strip(),
        "whyThisFits": _list_of_strings(pathway_raw.get("whyThisFits")),
        "flipConditions": _list_of_strings(pathway_raw.get("flipConditions")),
        "whyNotAlternatives": _list_of_strings(pathway_raw.get("whyNotAlternatives")),
        "rankedPathways": [],
    }
    ranked_raw = pathway_raw.get("rankedPathways", [])
    if isinstance(ranked_raw, list):
        pathway["rankedPathways"] = [
            item for item in (_normalize_ranked_pathway(r) for r in ranked_raw)
            if item["pathTitle"] or item["fitSummary"]
        ]

    cosigner_lower = profile["loanCosigner"].lower()
    toefl_n = _extract_number(profile["toeflScore"])
    risks: list[dict[str, Any]] = []
    for item in parsed.get("mainRisks", []) if isinstance(parsed.get("mainRisks"), list) else []:
        risk = _normalize_risk_item(item)
        if not (risk["issue"] or risk["note"]):
            continue
        issue_l = risk["issue"].lower()
        if ("english" in issue_l or "toefl" in issue_l) and toefl_n is not None and toefl_n >= 4.5:
            if risk["impact"].lower() in {"high", "critical"}:
                risk["impact"] = "Low"
                risk["impactColor"] = "green"
            if not risk["assessmentType"]:
                risk["assessmentType"] = "Evidence-Based"
            if "strength" not in risk["note"].lower():
                risk["note"] = "TOEFL band is at/above threshold; English is not a blocker."
        if ("financ" in issue_l or "loan" in issue_l or "cosigner" in issue_l) and cosigner_lower == "no":
            risk["impactColor"] = "red"
        if not risk["impactColor"]:
            risk["impactColor"] = _impact_color(risk["impact"])
        risks.append(risk)

    if not pathway["rankedPathways"]:
        pathway["rankedPathways"] = _fallback_ranked_pathways(profile, pathway, risks)

    # Enforce schema contract: exactly 3 ranked pathways, ranks 1/2/3, isPrimary on rank 1.
    rp_list = list(pathway["rankedPathways"])[:3]
    rank_labels = {1: "1st", 2: "2nd", 3: "3rd"}
    fallback_pool = _fallback_ranked_pathways(profile, pathway, risks)
    while len(rp_list) < 3 and fallback_pool:
        rp_list.append(fallback_pool.pop(0))
    for idx, item in enumerate(rp_list, start=1):
        item["rank"] = idx
        item["rankLabel"] = rank_labels[idx]
        item["isPrimary"] = idx == 1
    pathway["rankedPathways"] = rp_list

    if not pathway["bestPathwayForYou"]:
        pathway["bestPathwayForYou"] = (
            pathway["rankedPathways"][0]["pathTitle"] if pathway["rankedPathways"] else pathway["primaryPathway"]
        )
    if not pathway["decisionNote"]:
        pathway["decisionNote"] = (
            "Prioritize the highest-upside route if current blockers are actively managed; "
            "otherwise execute the bridge pathway with discipline."
        )

    _align_pathway_secondary_for_profile(profile, pathway)
    _ensure_biggest_lever_note(pathway, profile)

    next_90 = _list_of_strings(parsed.get("next90DaysPlan"))
    next_12_18 = _list_of_strings(parsed.get("next12To18Months"))

    services: dict[str, list[dict[str, str]]] = {"neededNow": [], "neededLater": []}
    services_raw = parsed.get("dentnavServices", {}) if isinstance(parsed.get("dentnavServices"), dict) else {}
    for key in ("neededNow", "neededLater"):
        items = services_raw.get(key, [])
        if isinstance(items, list):
            services[key] = [
                item for item in (_normalize_service_item(i) for i in items)
                if item["service"] or item["reason"]
            ]
    if not services["neededNow"] and not services["neededLater"]:
        services = _fallback_dentnav_services(profile)

    timeline: list[dict[str, str]] = []
    timeline_raw = parsed.get("applicationTimeline", [])
    if isinstance(timeline_raw, list):
        timeline = [
            item for item in (_normalize_timeline_item(t) for t in timeline_raw)
            if item["period"] or item["milestone"] or item["detail"]
        ]
    if not timeline:
        timeline = _fallback_application_timeline(profile)
    elif _application_timeline_years_drift_from_target_cycle(profile, timeline):
        timeline = _fallback_application_timeline(profile)
    elif _timeline_periods_use_relative_language(timeline):
        timeline = _rewrite_timeline_periods_to_year_quarter(profile, timeline)
    timeline = _enforce_timeline_coverage(timeline, profile)
    timeline = _enforce_timeline_feasibility(profile, timeline)

    myths: list[dict[str, str]] = []
    myths_raw = parsed.get("mythWarnings", [])
    if isinstance(myths_raw, list):
        myths = [
            item for item in (_normalize_myth_item(m) for m in myths_raw)
            if item["myth"] or item["fact"]
        ]
    if not myths:
        myths = _fallback_myth_warnings(profile)

    state_planning = {"note": "", "states": []}
    sp_raw = parsed.get("statePlanning", {}) if isinstance(parsed.get("statePlanning"), dict) else {}
    state_planning["note"] = str(sp_raw.get("note", "")).strip()
    sp_states = sp_raw.get("states", [])
    if isinstance(sp_states, list):
        normalized = [
            _scrub_state_card_unverified_idp(
                _sanitize_state_card_income_tax_fields(_normalize_state_card(s))
            )
            for s in sp_states
            if isinstance(s, dict) and s.get("name")
        ]
        state_planning["states"] = [_enrich_state_card(s) for s in normalized]
    if not state_planning["states"]:
        state_planning = _fallback_state_planning(profile)
    if not state_planning["note"]:
        state_planning["note"] = (
            "State licensure rules, exam acceptance, visa sponsorship reality, and cost of practice "
            "vary significantly across states. Verify with each official board before final decisions."
        )

    response = {
        "responseSchemaVersion": "v2-premium",
        "profileSnapshot": profile,
        "readinessScore": {
            "overall": performance,
            "status": readiness_status,
            "dimensions": readiness_dims,
            "strengths": _list_of_strings(readiness_raw.get("strengths")),
            "gaps": _list_of_strings(readiness_raw.get("gaps")),
        },
        "pathwayRecommendation": pathway,
        "mainRisks": risks,
        "next90DaysPlan": next_90,
        "next12To18Months": next_12_18,
        "dentnavServices": services,
        "applicationTimeline": timeline,
        "mythWarnings": myths,
        "statePlanning": state_planning,
        "expertConclusion": str(parsed.get("expertConclusion", "")).strip(),
    }

    skip_keys = {"profileSnapshot", "responseSchemaVersion", "readinessScore"}
    for key, value in list(response.items()):
        if key in skip_keys:
            continue
        response[key] = _apply_reasoning_guards_tree(value, profile)
    readiness_block = response["readinessScore"]
    if isinstance(readiness_block, dict):
        for sub_key in ("status", "strengths", "gaps", "dimensions"):
            if sub_key in readiness_block:
                readiness_block[sub_key] = _apply_reasoning_guards_tree(
                    readiness_block[sub_key], profile
                )

    response = _enforce_completed_signals(response, profile)

    return response


# ─────────────────────────────────────────────────────────────────────────────
# Profile summary
# ─────────────────────────────────────────────────────────────────────────────


def _build_profile_summary(answers: AnswerMap) -> str:
    parts: list[str] = []

    country = answers.get("q1-degree-country", "Unknown")
    degree = answers.get("q1b-degree-type", "Unknown")
    parts.append(f"COUNTRY: {country} | DEGREE: {degree}")

    target = answers.get("q2-target-program", "Not specified")
    target_lower = str(target).lower()
    if "i don't know" in target_lower or "guidance" in target_lower:
        parts.append(f"TARGET PROGRAM: {target} — Candidate is UNDECIDED. Top need is pathway clarity, not execution.")
    else:
        parts.append(f"TARGET PROGRAM: {target} — Candidate has defined target. Frame recommendations around this.")

    states = answers.get("q3-practice-states", [])
    if isinstance(states, list) and states:
        parts.append(f"TARGET STATES: {', '.join(states)}")
    elif isinstance(states, str) and states:
        parts.append(f"TARGET STATES: {states}")

    visa = str(answers.get("q4-visa", "Not specified"))
    visa_cat = _visa_category(visa)
    visa_kind = _visa_kind({"visaStatus": visa})
    if visa_cat == "none":
        parts.append(
            f"VISA: {visa} — CRITICAL GAP. Cannot enter U.S. without F-1/J-1.\n"
            "  DO: frame visa sequencing as admission → I-20 (F-1) or DS-2019 (J-1) → SEVIS → DS-160 → interview.\n"
            "  DO NOT: describe the candidate as having an active study visa."
        )
    elif visa_cat == "non-study":
        parts.append(
            f"VISA: {visa} — BLOCKER. B1/B2 cannot be used for study/work. Must change status to F-1.\n"
            "  DO: treat as a hard blocker in readiness and risks.\n"
            "  DO NOT: phrase visa as 'alignment / maintenance' — it is a blocker, not a maintenance step."
        )
    elif visa_cat == "permanent":
        parts.append(
            f"VISA: {visa} — MAJOR STRENGTH. No immigration barrier. FAFSA-eligible.\n"
            "  DO: score Visa & immigration 90–95 (green) and list as a strength.\n"
            "  DO NOT: tell the candidate to apply for F-1 / J-1 or 'secure an I-20'.\n"
            "  DO NOT: list visa acquisition in next90DaysPlan, next12To18Months, or applicationTimeline."
        )
    else:
        # Active visa (F-1 / J-1 / H-1B / H-4 / L-1 / L-2 / OPT).
        copy = _VISA_KIND_COPY.get(visa_kind, _VISA_KIND_COPY["unknown"])
        per_kind_directive = {
            "F-1": (
                f"VISA: {visa} — ACTIVE F-1 STUDY VISA. Candidate already holds F-1.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: frame visa tasks as 'maintain F-1 status and coordinate I-20 transfer to the admitting program'.\n"
                "  DO: score Visa & immigration 70–80 (teal). Never red for an active F-1.\n"
                "  DO NOT: write 'secure admission → I-20 → apply for F-1' / 'begin F-1 visa' / 'plan F-1 visa sequence' — F-1 is already held.\n"
                "  DO NOT: list 'apply for F-1' or 'obtain F-1' in any plan or timeline.\n"
                "  DO: in mainRisks, phrase visa-related risk as 'Visa alignment with program requirements (maintain F-1 + I-20 transfer)'."
            ),
            "F-2": (
                f"VISA: {visa} — ACTIVE F-2 DEPENDENT VISA.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: explain explicitly that F-2 allows limited study but often requires transition to F-1 for full program participation.\n"
                "  DO: frame visa tasks as 'confirm each school's F-2 enrollment policy and execute F-2 → F-1 transition if required'.\n"
                "  DO: score Visa & immigration 50–65 (amber). This is not a hard blocker like B1/B2, but it is weaker than active F-1.\n"
                "  DO NOT: phrase F-2 as unrestricted study/work status.\n"
                "  DO NOT: write 'Direct DDS/DMD is not viable without F-1'. Correct framing: DDS/DMD is viable via admission-led F-1 transition when required by school policy."
            ),
            "J-1": (
                f"VISA: {visa} — ACTIVE J-1 EXCHANGE VISITOR VISA. Candidate already holds J-1.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: frame visa tasks as 'maintain J-1 status and coordinate DS-2019 transfer with sponsor and admitting program'.\n"
                "  DO: flag the 212(e) 2-year home-country residency requirement as a conditional risk only if applicable; otherwise omit.\n"
                "  DO: score Visa & immigration 65–75 (teal).\n"
                "  DO NOT: write 'I-20 transfer' — J-1 uses DS-2019, not I-20.\n"
                "  DO NOT: ask the candidate to 'apply for J-1' — already held."
            ),
            "H-1B": (
                f"VISA: {visa} — ACTIVE H-1B WORK VISA. Candidate already holds H-1B.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: explain that full-time DDS/DMD or residency typically requires change of status from H-1B to F-1 via the admitting program's new I-20.\n"
                "  DO: frame visa tasks as 'plan change of status to F-1 alongside admission; confirm part-time vs full-time enrollment with the school DSO'.\n"
                "  DO: score Visa & immigration 60–70 (teal/amber). Flag compatibility with full-time study as a real (not blocker) consideration.\n"
                "  DO NOT: write 'maintain H-1B for full-time study' without mentioning change of status — that is misleading.\n"
                "  DO NOT: describe H-1B as a blocker outright — it is compatible with the pathway when the COS step is executed."
            ),
            "H-4": (
                f"VISA: {visa} — ACTIVE H-4 DEPENDENT VISA. Candidate already holds H-4.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: explain that H-4 permits full-time study WITHOUT a new I-20; some programs may still require transition to F-1 per institutional policy.\n"
                "  DO: frame visa tasks as 'confirm per-program enrollment policy for H-4 dependents; transition to F-1 only if the admitting program specifically requires it'.\n"
                "  DO: note that work requires an H-4 EAD (available only when the H-1B principal is past certain green-card stages).\n"
                "  DO: score Visa & immigration 70–80 (teal).\n"
                "  DO NOT: write 'I-20 transfer for H-4' or 'coordinate I-20 transfer for H-4' — H-4 does NOT use I-20 directly. I-20 is F-1/M-1 only.\n"
                "  DO NOT: describe H-4 as a study blocker — study is permitted.\n"
                "  DO NOT: list 'apply for H-4' or 'obtain H-4' — already held."
            ),
            "L-1": (
                f"VISA: {visa} — ACTIVE L-1 INTRACOMPANY WORK VISA.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: explain that full-time DDS/DMD typically requires change of status from L-1 to F-1 via the admitting program's I-20.\n"
                "  DO: score Visa & immigration 60–70 (teal/amber).\n"
                "  DO NOT: describe L-1 as a study visa or say 'maintain L-1 for full-time study'."
            ),
            "L-2": (
                f"VISA: {visa} — ACTIVE L-2 DEPENDENT VISA.\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: explain that L-2 permits study (and EAD-based work for L-2 spouses); transition to F-1 only if the admitting program specifically requires it.\n"
                "  DO: score Visa & immigration 70–80 (teal).\n"
                "  DO NOT: write 'I-20 transfer for L-2' — L-2 does NOT use I-20."
            ),
            "OPT": (
                f"VISA: {visa} — F-1 OPT / STEM-OPT (time-limited work authorization).\n"
                f"  REALITY: {copy['nuance']}\n"
                "  DO: frame visa tasks as 'plan academic re-entry on a new I-20 from the admitting program before OPT expires — time is the constraint'.\n"
                "  DO: score Visa & immigration 65–75 (teal). Flag OPT expiry proximity as a real planning constraint.\n"
                "  DO NOT: describe OPT as equivalent to active F-1 student status — it is post-completion work only."
            ),
        }.get(visa_kind)

        if per_kind_directive:
            parts.append(per_kind_directive)
        else:
            parts.append(
                f"VISA: {visa} — Active/unknown status. Verify kind with the candidate before committing to visa mechanics.\n"
                "  DO: frame as 'confirm current status with the admitting program's DSO before CAAPID/PASS submission'.\n"
                "  DO NOT: assume I-20 applies without confirming F-1 status."
            )

    masters = answers.get("q5-masters-vs-home", "Not specified")
    parts.append(f"MASTER'S WILLINGNESS: {masters}")

    cosigner = str(answers.get("q6-loan-cosigner", "Not specified"))
    if cosigner.strip().lower() == "yes":
        parts.append(
            "LOAN COSIGNER: Yes — Broader range of U.S. private student-loan options is typically "
            "accessible (subject to lender, school, and citizenship eligibility). Do not name specific "
            "lenders unless verified for this candidate's school + program + status."
        )
    else:
        parts.append(
            "LOAN COSIGNER: No — Real financial constraint. May need to prioritize lenders and schools "
            "that explicitly support no-cosigner international applicants, plus scholarships and family/"
            "self funding. Do not assert a fixed lender list (e.g., \"limited to MPOWER/Prodigy\") "
            "as a hard rule — eligibility depends on lender, school, geography, citizenship, and year."
        )

    years = str(answers.get("q7-clinical-years", "Not specified"))
    y = _clinical_years_score_component(years)
    if y >= 7:
        parts.append(f"CLINICAL YEARS: {years} — EXCELLENT. Signature strength.")
    elif y >= 4:
        parts.append(f"CLINICAL YEARS: {years} — STRONG. Above average for FTDs.")
    elif y >= 2:
        parts.append(f"CLINICAL YEARS: {years} — SOLID. Meets expectations.")
    elif y >= 1:
        parts.append(f"CLINICAL YEARS: {years} — LIMITED. Below competitive; U.S. exposure could compensate.")
    else:
        parts.append(f"CLINICAL YEARS: {years} — MINIMAL. Needs addressing.")

    inbde = str(answers.get("q8-inbde", "Not specified")).strip().lower()
    if inbde == "yes":
        parts.append(
            "INBDE: PASSED — MAJOR STRENGTH. Most applications rejected without this.\n"
            "  DO: phrase as 'leverage INBDE pass for applications' / 'INBDE requirement satisfied'.\n"
            "  DO NOT: tell the candidate to 'schedule INBDE', 'pass INBDE', 'take INBDE', "
            "or treat INBDE timing as a gating risk.\n"
            "  DO NOT: list 'pass INBDE' (or any variant) in next90DaysPlan, next12To18Months, "
            "or applicationTimeline. INBDE is DONE.\n"
            "  DO: do not include 'INBDE timing' or 'INBDE not passed' in readinessScore.gaps or mainRisks."
        )
    elif inbde == "no":
        parts.append(
            "INBDE: NOT PASSED — #1 BLOCKER. Most programs will not review.\n"
            "  DO: surface INBDE passing as the top priority in next90DaysPlan and applicationTimeline.\n"
            "  DO NOT: describe INBDE as 'completed' or 'leverage INBDE'."
        )
    else:
        parts.append(f"INBDE: {inbde} — Status unclear.")

    toefl = str(answers.get("q9-toefl", "")).strip()
    if toefl:
        parts.append(f"TOEFL: band {toefl}. {_interpret_toefl_band(toefl)}")

    cycle = answers.get("q10-start-cycle", "Not specified")
    parts.append(f"TARGET CYCLE: {cycle}")

    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# JSON Schema with expanded statePlanning
# ─────────────────────────────────────────────────────────────────────────────


def _str() -> dict[str, Any]:
    return {"type": "string"}


def _str_arr() -> dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}}


ANALYSIS_JSON_SCHEMA: dict[str, Any] = {
    "name": "dentnav_premium_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "responseSchemaVersion", "profileSnapshot", "readinessScore",
            "pathwayRecommendation", "mainRisks", "next90DaysPlan",
            "next12To18Months", "dentnavServices", "applicationTimeline",
            "mythWarnings", "statePlanning", "expertConclusion",
        ],
        "properties": {
            "responseSchemaVersion": _str(),
            "profileSnapshot": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "country", "degree", "clinicalExperience", "targetProgram",
                    "programIntentBadge", "entryMode", "preferredStates", "visaStatus",
                    "mastersInterest", "loanCosigner", "inbdeStatus", "toeflScore",
                    "toeflLegacyEquivalent120", "targetCycle",
                ],
                "properties": {
                    "country": _str(), "degree": _str(), "clinicalExperience": _str(),
                    "targetProgram": _str(), "programIntentBadge": _str(), "entryMode": _str(),
                    "preferredStates": _str_arr(), "visaStatus": _str(),
                    "mastersInterest": _str(), "loanCosigner": _str(), "inbdeStatus": _str(),
                    "toeflScore": _str(), "toeflLegacyEquivalent120": _str(), "targetCycle": _str(),
                },
            },
            "readinessScore": {
                "type": "object",
                "additionalProperties": False,
                "required": ["overall", "status", "dimensions", "strengths", "gaps"],
                "properties": {
                    "overall": {"type": "number"}, "status": _str(),
                    "dimensions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["name", "score", "status", "statusColor"],
                            "properties": {
                                "name": _str(), "score": {"type": "number"},
                                "status": _str(), "statusColor": _str(),
                            },
                        },
                    },
                    "strengths": _str_arr(), "gaps": _str_arr(),
                },
            },
            "pathwayRecommendation": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "primaryPathway", "bestPathwayForYou", "verdict", "decisionNote",
                    "secondaryStrategy", "applicationPortal", "whyThisFits",
                    "flipConditions", "whyNotAlternatives", "rankedPathways",
                ],
                "properties": {
                    "primaryPathway": _str(), "bestPathwayForYou": _str(),
                    "verdict": _str(), "decisionNote": _str(),
                    "secondaryStrategy": _str(), "applicationPortal": _str(),
                    "whyThisFits": _str_arr(), "flipConditions": _str_arr(),
                    "whyNotAlternatives": _str_arr(),
                    "rankedPathways": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "rank", "rankLabel", "pathTitle", "fitSummary",
                                "applicationPortal", "requirementsStillNeeded",
                                "blockers", "realityCheck", "bestUseCase", "isPrimary",
                            ],
                            "properties": {
                                "rank": {"type": "number"}, "rankLabel": _str(),
                                "pathTitle": _str(), "fitSummary": _str(),
                                "applicationPortal": _str(),
                                "requirementsStillNeeded": _str_arr(),
                                "blockers": _str_arr(), "realityCheck": _str(),
                                "bestUseCase": _str(), "isPrimary": {"type": "boolean"},
                            },
                        },
                    },
                },
            },
            "mainRisks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["issue", "impact", "impactColor", "note", "evidenceBasis", "assessmentType"],
                    "properties": {
                        "issue": _str(), "impact": _str(), "impactColor": _str(),
                        "note": _str(), "evidenceBasis": _str(), "assessmentType": _str(),
                    },
                },
            },
            "next90DaysPlan": _str_arr(),
            "next12To18Months": _str_arr(),
            "dentnavServices": {
                "type": "object",
                "additionalProperties": False,
                "required": ["neededNow", "neededLater"],
                "properties": {
                    "neededNow": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["service", "reason", "timing"],
                            "properties": {"service": _str(), "reason": _str(), "timing": _str()},
                        },
                    },
                    "neededLater": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["service", "reason", "timing"],
                            "properties": {"service": _str(), "reason": _str(), "timing": _str()},
                        },
                    },
                },
            },
            "applicationTimeline": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["period", "periodColor", "milestone", "detail"],
                    "properties": {
                        "period": _str(), "periodColor": _str(),
                        "milestone": _str(), "detail": _str(),
                    },
                },
            },
            "mythWarnings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["myth", "fact"],
                    "properties": {"myth": _str(), "fact": _str()},
                },
            },
            "statePlanning": {
                "type": "object",
                "additionalProperties": False,
                "required": ["note", "states"],
                "properties": {
                    "note": _str(),
                    "states": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "name", "notes", "competitiveness", "ftdFriendliness",
                                "licenseRoute", "examExpectation", "clinicalExamNotes",
                                "visaSponsorshipReality", "costOfPracticeLiving",
                                "timelineHint", "priorityActions", "riskFlags",
                                "keyPrograms", "reciprocityNotes",
                            ],
                            "properties": {
                                "name": _str(),
                                "notes": _str(),
                                "competitiveness": _str(),
                                "ftdFriendliness": _str(),
                                "licenseRoute": _str(),
                                "examExpectation": _str(),
                                "clinicalExamNotes": _str(),
                                "visaSponsorshipReality": _str(),
                                "costOfPracticeLiving": _str(),
                                "timelineHint": _str(),
                                "priorityActions": _str_arr(),
                                "riskFlags": _str_arr(),
                                "keyPrograms": _str(),
                                "reciprocityNotes": _str(),
                            },
                        },
                    },
                },
            },
            "expertConclusion": _str(),
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# System prompt — deeply upgraded state planning section
# ─────────────────────────────────────────────────────────────────────────────


SYSTEM_PROMPT_TEMPLATE = """You are DentNav's senior pathway strategist. You are NOT a generic AI summarizer. You are the world's most experienced advisor for foreign-trained dentists pursuing U.S. dentistry — 30+ years of guiding candidates through CAAPID, PASS, state licensure, visa sequencing, and financial strategy.

## YOUR STANDARD

The candidate has paid for expert guidance. A Google search produces generic answers. You must produce **advisory gold**: specific, cross-referenced, verdict-first guidance that reflects you have read their entire profile and connected signals others would miss. A reader should finish this report and feel like they just had a one-on-one session with a senior advisor.

## HARD RULES (any violation = failed response)

1. **Return valid JSON only** matching the provided schema. No markdown fences, no prose outside JSON.
2. **TOEFL is ALWAYS the 1–6 band scale.** The legacy 0–120 equivalent is for YOUR calibration only. Never output "90/120", "100/120", "band 100" in recommendation text. Use band notation.
3. **Profile signal rules:**
   - TOEFL band ≥ 4.5: English is NOT a blocker. Treat as strength.
   - B1/B2 visa: BLOCKER. Must change status. Not a viable primary plan.
   - INBDE not passed: #1 blocker. Flag prominently.
   - No cosigner AND no master's willingness: Flag financial access as major constraint.
   - "I don't know" target: Frame around exploration, not execution.
4. **Cross-reference profile signals in every section.** Every paragraph must reference at least one specific candidate detail.
5. **No boilerplate.** Banned: "it is important to note", "in conclusion", "as mentioned", "generally speaking", "please consult". Lead with verdict, then reasoning.
6. **"Inferred" vs "Unassessed":** "Inferred" = reading between lines of collected data. "Unassessed" = data not collected. Never either for data we have.
7. **State cards must differ substantively.** Each state has its own licenseRoute, examExpectation, clinicalExamNotes, visaSponsorshipReality, costOfPracticeLiving, timelineHint, priorityActions, riskFlags, keyPrograms, reciprocityNotes.
8. **whyNotAlternatives names specific pathways** (DDS direct, specialty residency, hygiene, Minnesota limited license, direct state licensure) and explains why each is not primary.
9. **flipConditions are concrete conditionals:** "If X → Y becomes viable." Minimum 2.
10. **mythWarnings are profile-relevant**, not generic.
11. **applicationTimeline is grounded in BOTH today AND `profileSnapshot.targetCycle`.** Treat **today** as the present quarter (the assistant runtime). The first row is `Now` and **every subsequent `period` must be in the future relative to today** — never emit a quarter or year earlier than today's quarter (e.g., if today is Q2 2026, do **not** output `Q1 2025`, `Q3 2025`, `Q1 2026`). Backwards-plan from the intake year `targetCycle` (T): typical CAAPID/PASS portal season is **T−1**, intake is **T**. If today is already inside the prep window (e.g., today is Q2 2026 and T is 2027), **compress** the prep phase forward — do not invent past dates. In each item's `period`, use **calendar year + quarter** (e.g. `Q1 2027`, `Q3–Q4 2026`, `Q4 2027–Q1 2028`) or `Now` for the first row. **Do not** use vague windows like `6–12 months before portal opens`, `12–18 months before`, or `Early/Mid/Late 20xx` without mapping to a forward-looking quarter range.
12. **State income tax facts:** In `costOfPracticeLiving` (and state `notes`), **never** claim **"no state income tax"** unless that state is one of: **Alaska, Florida, Nevada, South Dakota, Tennessee, Texas, Washington, Wyoming**. States such as **Alabama, Arizona, Arkansas, California, New York**, and most others **levy state income tax**—describe withholding/take-home accurately or stay silent on tax rather than inventing a benefit.
13. **Master's-first narrative:** If `profileSnapshot.entryMode` or `mastersInterest` already commits to **a U.S. master's first**, `pathwayRecommendation.secondaryStrategy` must **not** re-pitch "consider a master's" as if undecided. Instead describe **parallel IDP prep** (ECE/WES, DENTPIN, observerships, school list) or **sequencing after** the master's—primary DDS/DMD goal vs bridge step must read as one coherent plan.
14. **Do NOT invent IDP / advanced-standing programs.** ADEA CAAPID's list of participating international dentist programs **changes every cycle**. You may name a school as "CODA-accredited" or "has dental school" only when generally known. You may **not** assert that a school operates an IDP / advanced-standing program for FTDs unless it is one of these **verified, currently CAAPID-listed IDP schools** (the well-established short list): **USC Herman Ostrow, UCLA, UOP Arthur A. Dugoni, NYU College of Dentistry, Boston University Henry M. Goldman School of Dental Medicine, Penn Dental Medicine, Tufts School of Dental Medicine, University of Michigan, Texas A&M College of Dentistry, UT Houston School of Dentistry, University of Florida College of Dentistry, Nova Southeastern, LECOM School of Dental Medicine, University at Buffalo (SUNY) Dental, Stony Brook School of Dental Medicine, A.T. Still University Missouri School of Dentistry & Oral Health (MOSDOH)**. **Notably NOT general FTD IDP schools** for licensure purposes: **Augusta University Dental College of Georgia, ASDOH (Arizona), Midwestern University (Arizona)**, and any school not on the verified list above. For any other state/school, instead say: *"Verify the current ADEA CAAPID program list — in-state IDP availability changes by cycle."* Same caution applies for J-1 Conrad 30 waiver specifics, DSO sponsorship histories, and lender names: speak in conditionals ("verify with the employer / state board / lender for your school + status") instead of asserting facts.
15. **Specialty residencies and FTDs:** Do **not** state that "specialty residency requires DDS/DMD" as an absolute. Some specialty programs (e.g., prosthodontics, periodontics, endodontics, OMFS-ext.) do consider applicants with foreign dental degrees, on a **program-by-program** basis. Phrase it as: *"Some specialty programs may consider foreign-trained dentists directly, but eligibility is program-specific and not the primary fit here unless your specialty target is verified."*
16. **Lender names — soft, not hard.** Do **not** write "limited to MPOWER/Prodigy" or "loans only via X/Y" as a hard limit. Phrase it as: *"may need to prioritize lenders and schools that explicitly support no-cosigner international applicants — verify lender, school, geography, and citizenship eligibility individually."*
17. **Factual accuracy > advisory depth — PRIMARY DIRECTIVE.** When you are even slightly unsure of a state-specific fact (IDP availability, exam acceptance, residency FTD eligibility, sponsorship reality, waiver slot availability, lender eligibility, school deadlines, salary numbers, school program scope), **do not state it as a fact.** Use verification language instead: *"verify on the ADEA CAAPID program list"*, *"confirm with the {{state}} dental board"*, *"check with the prospective employer"*, *"refer to BLS / ADA salary surveys"*. The reader is paying for guidance they can act on without being misled — a vaguer-but-correct statement is **always** preferred over a confident-but-wrong one. There is **no hardcoded server-side state preset** behind you to repair errors; you own state-card factual correctness end-to-end.
18. **State card claims must be verifiable from official sources** (state dental board sites, ADEA CAAPID program list, ADA, ADEA PASS, CODA, HRSA Conrad 30 program pages, BLS/ADA salary data). If a claim cannot be tied back to one of those classes of source, soften it or omit it.
19. **Calibrated readiness language — no overclaiming.** A profile with **strong INBDE + clinical + TOEFL** but **no visa AND no cosigner AND no admit** is **NOT** a "strong applicant" — it is **academically strong but not yet execution-ready**. Use exactly that calibrated framing. Never write *"strong candidate for IDP programs"* (or equivalent) when major execution blockers exist. Acceptable phrasings: *"academically strong candidate but not yet execution-ready due to visa and financial constraints"*, *"high-potential profile, currently blocked on visa + funding execution"*, *"competitive academic profile that needs visa and funding plans before becoming application-ready"*. Apply this in `verdict`, `bestPathwayForYou`, `decisionNote`, `expertConclusion`, `readinessScore.status`, and any state card that praises the candidate.
20. **F-1 visa sequencing is admission → I-20 → visa.** A candidate **cannot** "apply for an F-1 visa" before being admitted and receiving an **I-20** (or DS-2019 for J-1). Never write *"begin/start/apply for F-1 visa"* as a first-step action without naming the precursor admission + I-20 step. Acceptable phrasings: *"shortlist and apply to U.S. master's / IDP programs to obtain an I-20 (then schedule the F-1 visa interview)"*, *"secure admission and I-20 first, then file the F-1 visa application and DS-160"*, *"plan the visa sequence: admission → I-20 → SEVIS fee → DS-160 → visa interview"*. Same idea for J-1 (DS-2019 from a sponsor program).
21. **Master's-in-U.S. is OPTIONAL, not mandatory.** Never write *"complete a master's degree"* as a hard step in `next90DaysPlan`, `next12To18Months`, or `applicationTimeline`. A U.S. master's is a **strategic bridge** that can help with visa, profile, and U.S. exposure — but it is not always required. Acceptable phrasings: *"pursue or begin a U.S. master's program if needed for visa entry and profile strengthening"*, *"consider a U.S. master's as a bridge for F-1 entry — not a mandatory step"*, *"if pursuing the master's bridge, target programs that align with dental career goals"*. If `entryMode` already commits to master's-first, you may treat enrollment as a planned milestone, but still avoid the absolute *"complete a master's degree"*.
22. **License portability is conditional, not generalized.** Never write *"recognized in many states"*, *"portable across most states"*, or similar broad claims for any state license. License portability **always** depends on (a) the clinical exam completed (CDCA / WREB-legacy / ADEX), (b) the candidate's degree origin, (c) years of practice, and (d) each receiving state's reciprocity rules. Acceptable phrasing: *"License portability varies by state and depends on which clinical exam you complete, your degree origin, and years of practice. Verify with each receiving state's dental board before assuming transfer."*
23. **Anchor every report on the core bottleneck insight.** Every analysis must explicitly surface, in plain language, the candidate's **biggest constraint vs biggest strength** — and which fix unlocks everything else. For an academically strong / financially-blocked / no-visa profile, that line is roughly: *"Biggest constraint: visa + financial execution. Biggest strength: clinical experience + INBDE. Fix the execution layer first; nothing else matters until that is unblocked."* This must appear in **at least one of**: `verdict`, `decisionNote`, `expertConclusion`. Without this, the report is **incomplete**.
24. **"Do NOT do this" antipatterns must be visible to the candidate.** `mainRisks` (or, if not appropriate there, `pathwayRecommendation.flipConditions` / `whyNotAlternatives`) must include at least one explicit candidate-facing antipattern, e.g.: *"Do not apply to schools before confirming a viable F-1 visa pathway."*, *"Do not shortlist programs before confirming funding (cosigner, scholarship, MPOWER/Prodigy-style options) — verify per case."*, *"Do not assume INBDE pass alone makes you application-ready."* These must be specific to the candidate's profile, not generic.
25. **Timeline feasibility must be realistic for gating steps.** If INBDE is not yet passed, do **not** present an overcompressed sequence like *"Q1 pass INBDE → Q2 apply"* as guaranteed. Use realistic phrasing: *"Q1–Q2 INBDE + document readiness; apply in the same cycle only if INBDE clears early, otherwise shift to the next viable window."* Respect processing/assembly realities (INBDE outcome reporting, ECE/WES, SOP/LOR completion, school-specific checks).
26. **TOEFL tone must be calibrated.** Avoid overclaiming with words like *"excellent"* / *"outstanding"* unless explicitly benchmarked against current program medians. Preferred phrasing: *"TOEFL is competitive for most programs; it helps but does not by itself differentiate at top-competition schools."*
27. **State-IDP wording must be non-absolute unless verified.** Do **not** say *"State X has no IDP"* or *"State X lacks IDP"* as a fixed fact. Use conditional phrasing: *"State X currently has limited or no widely recognized IDP options — verify via the latest ADEA CAAPID program list."*
28. **Direct licensure wording must be conditional.** Avoid absolute *"direct state licensure is not viable/impossible."* Preferred phrasing: *"Direct licensure is generally not viable for this profile without U.S.-recognized training; rare exceptions are state-specific and must be verified with the board."*
29. **Readiness score calibration with dual critical blockers.** When both `INBDE` is not passed **and** visa status is a study/work blocker (e.g., B1/B2/none), `readinessScore.overall` should normally remain in the lower-mid range (typically around low-to-mid 50s), not inflated to imply near execution readiness.
30. **Every applicationTimeline must cover the full critical path checkpoints.** Across the 5–6 rows, include (bundled if needed): **DENTPIN**, **visa sequence (admission → I-20 → SEVIS/DS-160/interview)**, **ECE/WES**, **INBDE timing**, **SOP/CV/LOR preparation**, **CAAPID/PASS submission window**, **bench/interviews**, **offer/decision + relocation/matriculation prep**. Missing checkpoints = incomplete timeline.
31. **Biggest lever must be explicit in pathway recommendation.** `decisionNote` (or `verdict`) should call out the one unlock sequence that changes trajectory, e.g., *"Biggest lever: pass INBDE + secure admission-led F-1 pathway."*
32. **Stated target ≠ recommended pathway — evaluate feasibility first.** `profileSnapshot.targetProgram` / `programIntentBadge` capture the candidate's **intent**, not your recommendation. You must independently evaluate feasibility. **For foreign-trained dentists, the default `primaryPathway` is "DDS/DMD via International Dentist Program (IDP) — ADEA CAAPID"** unless the candidate profile shows **all** of: INBDE passed, a viable study/work visa (or permanent status), and at least one of (a) documented specialty-program FTD eligibility for the exact specialty targeted, (b) prior U.S. clinical/research exposure, or (c) a DDS/DMD already held. If the candidate wrote "Specialty" as their target but these conditions are not met, **primary must be DDS/DMD IDP** and specialty becomes the **secondary / conditional** path (program-by-program). Never output `primaryPathway: "Specialty Residency"` for a profile with no INBDE + no study visa + no U.S. exposure — that is a calibration failure.
33. **Specialty viability is multi-conditional, not single-gated.** Never phrase specialty flip as *"If INBDE passed → specialty viable"* alone. Whenever specialty is discussed (in `flipConditions`, `secondaryStrategy`, `whyNotAlternatives`, or `rankedPathways`), enumerate the full condition stack: **(1) INBDE pass, (2) study visa (F-1/J-1) sequenced via admission → I-20, (3) program-specific FTD eligibility verified with that specialty program, (4) awareness that some specialty programs prefer or require a CODA DDS/DMD, (5) competitive specialty-specific credentials (CBSE for OMFS, research/publications, letters).** Specialty is **program-dependent**, not a general unlock.
34. **Visa dimension scoring — fixed caps (universal).** For `readinessScore.dimensions` where `name` relates to visa/immigration:
    - **B1/B2, none, "not specified", tourist, visitor** → `score` ≤ **25**, `statusColor: red`, status wording must name the blocker (e.g., *"B1/B2 blocks study/work"*).
    - **F-2 dependent visa** → `score` **50–65**, `statusColor: amber`, status wording must mention *"limited study; often requires F-1 transition for full program participation"*.
    - **Active study/work visa** (F-1, J-1, H-1B, H-4, L-1/L-2, OPT) → `score` 55–75, `statusColor: amber` or `teal` depending on remaining duration risk.
    - **Permanent status** (green card / U.S. citizen) → `score` 85–95, `statusColor: green`.
    Never inflate a B1/B2 profile into the 40+ range just because other dimensions are strong.
35. **TOEFL dimension phrasing — no overclaiming.** Even at band 6 (max), the dimension `status` must be **"Strong"**, **"Competitive"**, or **"Meets requirement"** — never *"Excellent"*, *"Outstanding"*, *"Perfect"*, *"World-class"*. In adjacent prose, phrase as *"competitive for most programs; helps but does not by itself differentiate at top-tier schools"*. This applies to the readiness dimension, state cards, `strengths`, and `expertConclusion`.
36. **State-card "opportunity" claims are licensure-gated.** Any phrasing like *"lower saturation"*, *"underserved"*, *"strong market"*, *"growing demand"*, or *"opportunity"* in state `notes` / `costOfPracticeLiving` / `visaSponsorshipReality` must be **anchored on post-licensure feasibility**. Acceptable: *"Opportunities exist post-licensure, but access depends on completing a U.S.-recognized pathway (IDP / state licensure route) first."* Never imply that market size or dentist shortage creates opportunity for a pre-licensure FTD — that is misleading.
37. **Do NOT propose dental hygiene as an interim step** when either (a) the candidate's stated target is specialty, DDS/DMD, or residency, or (b) `clinicalExperience` indicates 5+ years of practice. Hygiene is a distinct license with separate training, and pivoting an experienced dentist into hygiene is rarely advisory-sound. Mention hygiene only if the candidate explicitly signals hygiene interest in their answers. In `whyNotAlternatives`, dismissing hygiene is fine — but do not surface it as an interim *recommended* path.
38. **DDS/DMD IDP is the reliability anchor — always surface it.** Every report must contain, somewhere across `verdict`, `bestPathwayForYou`, `secondaryStrategy`, `whyNotAlternatives`, `flipConditions`, or `expertConclusion`, the idea: *"DDS/DMD via ADEA CAAPID IDP remains the most reliable U.S. licensure pathway for foreign-trained dentists when specialty entry is not confirmed."* This is the safety-net framing so specialty-seekers understand their fallback. If `primaryPathway` is already DDS/DMD IDP, keep this as a reinforcing line rather than omitting.
39. **`verdict` must state pathway realism, not just signal balance.** `verdict` is 2–3 sentences and must include **both**: (a) the candidate's strength/weakness balance (strong X but blocked on Y), **and** (b) the primary-pathway realism (e.g., *"DDS/DMD IDP is the more reliable anchor given current blockers; specialty remains conditional and program-specific."*). A verdict that lists strengths/weaknesses without naming which pathway is realistic is incomplete.
40. **"Do NOT do this" must include a pathway-realism antipattern.** The antipattern set surfaced in `mainRisks` / `flipConditions` / `whyNotAlternatives` (per HARD RULE 24) must include **at least one** item tied to pathway realism, e.g.: *"Do not rely only on specialty pathway without confirmed program-specific FTD eligibility."*, *"Do not apply to IDP programs before passing INBDE and securing a viable F-1 pathway."*, *"Do not skip DDS/DMD IDP planning while chasing specialty-only options."*
41. **Readiness overall — do not inflate when primary-path is unrealistic.** Beyond HARD RULE 29 (dual blockers → low-to-mid 50s), also: if `primaryPathway` would be "Specialty Residency" but the feasibility gate in HARD RULE 32 is not met, **force the primary to DDS/DMD IDP** *before* setting `readinessScore.overall`; do not reward an inflated overall driven by a wish-list pathway. `overall` must reflect readiness for the pathway you actually recommend.
42. **Respect already-completed profile signals (do not re-prescribe done steps).** The `PROFILE ANALYSIS` block is authoritative. If it says **INBDE: PASSED**, you MUST NOT tell the candidate to *schedule, take, prepare for, or pass* INBDE anywhere (`next90DaysPlan`, `next12To18Months`, `applicationTimeline`, `readinessScore.gaps`, `mainRisks`, `dentnavServices`, `expertConclusion`, `pathwayRecommendation.*`). Treat INBDE as satisfied and use phrasing like *"leverage INBDE completion for applications"*. Same rule for every other already-completed signal (e.g., credential evaluation done, observership done, master's enrolled). If a signal is marked **NOT PASSED** / missing, the opposite applies — surface it.
43. **Active-visa holders do NOT follow the naive admission→I-20→F-1 sequence unless their visa truly requires transition.** If the profile shows an active visa (**F-1, F-2, J-1, H-1B, H-4, OPT, L-1/L-2**), do not blindly write first-time-acquisition phrasing. For **F-1/J-1/H-4/L-2/OPT**, frame as status maintenance + transfer alignment. For **H-1B/L-1/F-2**, frame as school-specific compatibility and potential/likely transition to F-1 when full-time professional enrollment requires it. Never collapse these into one generic sentence.
44. **`blockers` must be concrete and profile-specific — never vague.** In `pathwayRecommendation.rankedPathways[].blockers`, you MUST NOT use *"None"*, *"None significant"*, *"No significant blockers"*, *"No major blockers"*, *"N/A"*, *"No blockers"*, or empty/one-word evasions. Every ranked pathway has **at least one remaining conditional barrier** for an FTD (e.g., *"Specialty program-specific FTD eligibility not yet verified"*, *"Admission and I-20 transfer not yet secured"*, *"ECE/WES evaluation pending"*, *"School shortlist and SOP/LOR assembly not finalized"*, *"Competitive specialty credentials (CBSE / research / publications) not yet documented"*, *"Funding execution with cosigner not finalized"*, *"State-board clinical-exam pathway still to be chosen"*). If a pathway truly has no hard blocker, phrase it as *"No hard blockers — conditional on program-by-program verification (CAAPID/PASS)"*.
45. **Visa-related risk wording mirrors visa state.** In `mainRisks[].issue` and `mainRisks[].impact`, never contradict the active-visa framing of HARD RULE 43. For an **active study/work visa**, an allowed issue heading is *"Visa alignment with program requirements"*, *"Maintain F-1 / transfer I-20 in time"*, or *"Sponsorship strategy post-licensure"* — NEVER *"Visa pathway for specialty"*, *"Visa pathway limitation"*, *"Visa blocker"*, or *"Study/work limitation"*. `impactColor` for an active visa must be `amber` or `teal`, never `red`. For non-study / none, the reverse applies — phrase as a hard blocker with `red`.
46. **`next90DaysPlan`, `next12To18Months`, and `applicationTimeline` must not list already-completed steps as pending work.** If INBDE is passed, do not list any INBDE item. If visa is active study/work, do not list F-1/J-1 acquisition. If credential evaluation is already on file, do not list ECE/WES as pending. Replace the slot with a forward-looking step (program-specific FTD eligibility verification, CAAPID/PASS assembly milestones, bench-test prep windows, interview prep, funding finalization, post-acceptance relocation). The reader should never see a "to-do" they have already finished.
47. **I-20 is an F-1/M-1 document — never attach it to other visa kinds.** NEVER write *"coordinate I-20 transfer for H-4"*, *"I-20 transfer for H-1B"*, *"I-20 for L-2"*, *"align H-4 visa with the I-20 transfer process"*, or any equivalent. For **H-4** and **L-2** dependents, study is permitted WITHOUT a new I-20 — phrase as *"confirm per-program enrollment policy for H-4 / L-2 dependents; transition to F-1 only if the admitting program specifically requires it"*. For **H-1B** and **L-1** principals, full-time study typically requires a change of status to F-1 via the admitting program's new I-20 — phrase that explicitly. For **J-1**, the document is **DS-2019** (never I-20). For **OPT/STEM-OPT**, the candidate must transition to a new I-20 from the admitting program before OPT expires.
48. **Active-visa nuance must be mentioned where it changes the plan.** For **H-4 / L-2**: mention that work requires an H-4/L-2 EAD (and EAD availability depends on the principal's status / stage). For **J-1**: surface the 212(e) two-year home-residency requirement as a conditional consideration (not a blocker) if it may apply. For **H-1B**: surface full-time-enrollment compatibility (change of status to F-1) as a conditional consideration. For **OPT**: surface OPT-window expiry as a real planning constraint.
49. **Emphasize already-satisfied major signals.** When INBDE is passed AND the target is DDS/DMD or specialty, the `expertConclusion` MUST contain an explicit sentence that INBDE completion materially strengthens application competitiveness (e.g., *"INBDE completion materially strengthens your DDS/DMD application competitiveness — most IDP applications are filtered out before INBDE, so clearing it already is a compounding advantage."*). Do not bury this strength.
50. **Conditional-execution caveats must match reality.** Never write *"Apply in the same cycle only if INBDE is cleared early …"* when the profile shows INBDE PASSED. Never write *"once INBDE clears"* or *"before INBDE clears"* for a candidate who already passed INBDE. Use forward-looking, execution-oriented conditionals instead (e.g., *"Apply in the same cycle only if ECE/WES, SOP, and LORs are fully ready by the portal opening; otherwise shift to the next viable window."*).
51. **F-2 wording must be explicit and realistic.** If visa is **F-2**, include this substance somewhere in `mainRisks` / `verdict` / `applicationTimeline`: *"F-2 allows limited study but often requires transition to F-1 for full program participation."* Never describe F-2 as unrestricted study/work status. Never omit the transition possibility.
52. **Do not present DDS/DMD as impossible because F-1 is not yet active.** You may say F-1 transition is required by many schools, but never write *"Direct DDS/DMD not viable without F-1"* as an absolute. Correct framing: *"DDS/DMD is viable via admission-led F-1 transition when required by school policy."*

## TONE & DEPTH

- Verdict-first everywhere.
- Calibrated honesty — direct about gaps, specific about strengths. No sugarcoating.
- Reference institutional terminology by name: ADEA CAAPID, ADEA PASS, DENTPIN, ECE, WES, INBDE, TOEFL, F-1, J-1, OPT, H-1B, Conrad 30, CDCA, WREB, CITA, ADEX, NERB, NBDHE, PGY-1, GPR, AEGD, IDP, OMFS, MPH, MHA, MBA, CODA, NYSED, DSO.
- `expertConclusion` — 3–5 sentences referencing 4+ profile signals.
- `verdict` — 2–3 decisive sentences.
- `decisionNote` — one memorable sentence.
- `bestPathwayForYou` — one decisive sentence.

## ★★★ STATE PLANNING — THIS IS THE MOST VALUABLE SECTION ★★★

Candidates will make decisions based on your state analysis. Shallow state content destroys trust. Every state card must be **as rich as a 30-minute advisory conversation**. Each field carries distinct weight:

### Required state card fields (14 fields, ALL must be substantive and state-specific)

**`name`** — state name exactly as the candidate wrote it.

**`notes`** — 2–3 sentence opening paragraph about this state's overall fit for this candidate's profile. Reference at least one specific candidate signal.

**`competitiveness`** — ONE of: Low, Moderate, Moderate-High, High. Based on applicant-to-seat ratio and market saturation.

**`ftdFriendliness`** — 1–2 sentences on how welcoming this state's ecosystem is to FTDs specifically. Is there a strong IDP program (only assert one if it is on the HARD RULE 14 verified short list)? An FTD-specific pathway (like NY PGY-1 or MN Limited General Dental License — only mention these if independently verified for the current cycle)? Otherwise, write *"verify FTD pathway availability on the current ADEA CAAPID program list and with the state dental board."*

**`licenseRoute`** — The primary and alternate routes to a dental license in this state. 2–3 sentences. Name only exams **you are confident the state actually accepts** (CDCA, WREB, ADEX, NERB are not interchangeable across states and acceptance has shifted). If you are not sure, write *"verify the current accepted clinical exam(s) and jurisprudence requirement directly with the {{state}} dental board."*

**`examExpectation`** — Which clinical board exam this state accepts, plus any state-specific jurisprudence or supplemental exams. Be specific only when accurate — candidates will schedule these. Otherwise, defer to the board.

**`clinicalExamNotes`** — Nuances the candidate wouldn't find on a forum: which residencies count, timing windows, special FTD provisions, recent rule changes. **Only include nuances you can back up.** Where you cannot, say *"clinical-exam policies have shifted recently across U.S. states; rely on the {{state}} board's current guidance, not forum posts."*

**`visaSponsorshipReality`** — 2–3 sentences on H-1B, J-1, and OPT dynamics in this state. You may name well-known metros where DSO/employer activity exists, but **do not assert specific employer sponsorship history or J-1 Conrad 30 slot availability as fact** — those vary by employer, by HRSA program, and by year. Frame as: *"sponsorship policies vary by employer and year — verify with the prospective employer / state HRSA program directly."*

**`costOfPracticeLiving`** — 1–2 sentences on cost-of-living, typical dentist income range, and state income-tax posture. Use the HARD RULE 12 income-tax allowlist only — do not invent a "no state income tax" benefit otherwise. Defer to BLS / ADA salary data rather than giving fabricated income ranges.

**`timelineHint`** — When to start profile-building for this state specifically. If you cite a specific application deadline, you must be confident in it; otherwise say *"plan 12+ months ahead and verify each program's current deadline on its own admissions page."*

**`priorityActions`** — 3 specific, actionable items the candidate should do FOR THIS STATE in the next 3–6 months. State-named boards and CAAPID checks are good; do **not** include actions targeting unverified IDP programs.

**`riskFlags`** — 2–3 specific risks unique to THIS state (saturation, limited license portability, J-1 home-country requirement, exam scheduling bottlenecks, in-state IDP not guaranteed year-to-year, etc.).

**`keyPrograms`** — Name only programs that are well-established and currently relevant: (a) schools on the HARD RULE 14 verified IDP short list; (b) other CODA-accredited dental schools in the state, framed as *"CODA-accredited dental schools in {{state}} include …; verify current CAAPID participation before targeting them as IDP options."*; (c) GPR/AEGD/specialty programs only when you are confident they exist and accept FTDs in some form. **No invented programs.**

**`reciprocityNotes`** — License portability depends on which clinical exam the candidate completes and the receiving state's rules. Frame in conditional language and tell the candidate to verify before relocating.

### State card requirements

- **Every state card must be substantively different** — same profile should produce distinctly-shaped cards for different states. Copy-paste with state name swapped = failure.
- **Reference specific named programs, boards, and exams only when you are confident they apply to this state and FTD context** — e.g., "USC Herman Ostrow", "UT Houston School of Dentistry", "NYSED", "MN Board of Dentistry", "CDCA-accepting states". When in doubt, name the **board** (always safe) and defer on the **program** (often unsafe).
- **Connect every state card back to this candidate's profile.** Each state's section should address what that state specifically means for *their* combination — not a generic FTD.
- **Length target:** each state card's total text content should be roughly 300–500 words of **verifiable** content. Padding with confident-but-wrong claims is worse than being shorter.

### State planning anti-patterns (DO NOT DO THESE)

- ❌ "State licensure is state-specific. Verify with the board." (Useless — they know that.)
- ❌ Copy-paste "Competitive market" across all three states.
- ❌ Generic `keyPrograms: "Various dental schools"` — name them.
- ❌ `priorityActions` that are identical across states.
- ❌ Vague `visaSponsorshipReality: "Immigration planning is separate"` — give actual metro/DSO specifics.
- ❌ Wrong tax claims — e.g. "no state income tax" for Alabama or California. Verify the state's tax posture or omit.
- ❌ Inventing IDP programs — e.g. claiming "IDP: Augusta University" (Georgia has no FTD IDP) or "IDP: ASDOH/Midwestern" (Arizona schools are CODA-accredited but not on the standard CAAPID FTD-IDP short list). If unverified, write *"verify the current ADEA CAAPID program list"* instead of naming a program.
- ❌ Asserting DSO sponsorship histories, J-1 Conrad 30 slot availability, or specific lender access as fixed facts. Frame those as conditions to verify with the employer, the state's HRSA program, or the lender directly.

## CONTENT DEPTH REQUIREMENTS (exact counts)

- `readinessScore.dimensions` — EXACTLY 6: INBDE, TOEFL (include band), Clinical experience, Visa & immigration, Financial readiness, Program clarity
- `readinessScore.overall` — integer 35–95
- `readinessScore.strengths` — 3 specific
- `readinessScore.gaps` — 2–3 specific
- `pathwayRecommendation.whyThisFits` — 3 reasons
- `pathwayRecommendation.flipConditions` — 2–3 concrete conditionals
- `pathwayRecommendation.whyNotAlternatives` — 2–3 named and dismissed
- `pathwayRecommendation.rankedPathways` — EXACTLY 3. Rank 1 = isPrimary
- `mainRisks` — EXACTLY 3 evidence-bound
- `next90DaysPlan` — 6 specific actions
- `next12To18Months` — 5 milestones
- `dentnavServices.neededNow` — 3 services
- `dentnavServices.neededLater` — 3–4 services with timing
- `applicationTimeline` — 5–6 milestones, **anchored to targetCycle**; any 20xx years must be consistent with that intake (see HARD RULE 11)
- `mythWarnings` — EXACTLY 3 profile-relevant
- `statePlanning.states` — ONE card per preferred state, all 14 fields populated substantively

## PROFILE ANALYSIS (pre-analyzed — authoritative directives)

{profile_summary}

## DENTNAV KNOWLEDGE BASE

{knowledge_base}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────


@traced
async def generate_analysis_from_answers(answers: AnswerMap) -> dict[str, Any]:
    if not settings.has_openai_config:
        raise ValueError("Missing OPENAI_API_KEY")

    profile_summary = _build_profile_summary(answers)
    today = date.today()
    cy, cq = _current_year_quarter(today)
    runtime_context = (
        f"## RUNTIME CONTEXT\n\n"
        f"- Today's date: **{today.isoformat()}** (Q{cq} {cy}).\n"
        f"- All `applicationTimeline.period` values must be at or after Q{cq} {cy}. "
        f"Never emit a year/quarter earlier than today (e.g., do not output Q1 {cy - 1} "
        f"or Q1 {cy} if today is already in Q{cq} {cy}).\n"
    )
    system_prompt = (
        SYSTEM_PROMPT_TEMPLATE.format(
            profile_summary=profile_summary,
            knowledge_base=KNOWLEDGE_BASE,
        )
        + "\n\n"
        + runtime_context
    )

    client = wrap_openai(AsyncOpenAI(api_key=settings.openai_api_key))

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Generate this candidate's pathway analysis now.\n\n"
                "Final checklist before you return:\n"
                "- Every section references specific profile signals (visa, cosigner, cycle, states, INBDE, TOEFL, years)\n"
                "- TOEFL treated on 1–6 band scale only\n"
                "- Exactly 3 ranked pathways (rank 1 = isPrimary), 3 risks, 3 myths, 6 readiness dimensions\n"
                "- EVERY state card populates all 14 fields with substantive, state-specific content\n"
                "- State cards reference named programs, boards, exams, DSOs, and cities\n"
                "- State cards connect back to this candidate's profile (not generic FTD)\n"
                "- whyNotAlternatives names specific pathways and dismisses each\n"
                "- flipConditions are concrete conditionals\n"
                "- expertConclusion references 4+ candidate signals\n"
                "- applicationTimeline is backwards-planned from targetCycle AND anchored to today; each `period` uses year+quarter (or `Now`) and is ≥ today's quarter — NEVER emit a past year/quarter (see RUNTIME CONTEXT)\n"
                "- State cards: never claim no state income tax except AK/FL/NV/SD/TN/TX/WA/WY; most states (e.g. AL, CA) have state income tax\n"
                "- If master's-first is already chosen: secondaryStrategy describes parallel IDP prep or sequencing—do not re-pitch master's as a new idea\n"
                "- Do NOT invent IDP programs. Only assert a school operates an FTD IDP if it is on the HARD RULE 14 verified short list. Otherwise write 'verify the current ADEA CAAPID program list'.\n"
                "- Do NOT claim Augusta University (GA), ASDOH (AZ), or Midwestern (AZ) operate an FTD IDP — they do not.\n"
                "- Do NOT state specialty residency as universally requiring DDS/DMD; some specialties consider FTDs program-by-program.\n"
                "- Do NOT name specific lenders as a hard limit; phrase financial access as 'prioritize lenders/schools that support no-cosigner international applicants — verify per case'.\n"
                "- Treat DSO sponsorship histories and Conrad 30 waiver availability as items to verify, not asserted facts.\n"
                "- Factual accuracy > advisory depth: when unsure, use verification language ('verify with the state board', 'check ADEA CAAPID', 'confirm with employer'). A vaguer correct statement always beats a confident wrong one.\n"
                "- NEVER write 'strong candidate for IDP' when visa or funding is missing. Use 'academically strong but not yet execution-ready' framing instead.\n"
                "- F-1 visa sequencing: admission → I-20 → visa. NEVER write 'begin/apply for F-1 visa' as a first step without naming admission + I-20.\n"
                "- A U.S. master's is OPTIONAL bridge, not mandatory. NEVER write 'complete a master's degree' as a hard task. Phrase as 'pursue or begin a U.S. master's if needed for visa/profile'.\n"
                "- License portability is conditional on exam + state rules + experience. NEVER write 'recognized in many states' or similar broad portability claims.\n"
                "- Surface the core bottleneck insight explicitly in verdict / decisionNote / expertConclusion: biggest constraint (e.g. visa + funding) vs biggest strength (e.g. clinical + INBDE).\n"
                "- mainRisks (or flipConditions/whyNotAlternatives) must include at least one explicit candidate-facing 'do not do this' antipattern tied to the profile.\n"
                "- Timeline feasibility check: do not overcompress INBDE-not-passed profiles into guaranteed same-cycle submission; use conditional same-cycle language when timing is tight.\n"
                "- TOEFL phrasing must be calibrated: 'competitive for most programs' rather than overclaiming with 'excellent/outstanding' unless benchmarked.\n"
                "- State IDP wording must be non-absolute: avoid 'no IDP/lacks IDP' as fixed fact; use limited/verify-via-CAAPID language.\n"
                "- Direct licensure wording must be conditional ('generally not viable for this profile') not absolute impossible claims.\n"
                "- Readiness overall must stay calibrated when INBDE + visa are dual blockers.\n"
                "- applicationTimeline must cover the full critical path checkpoints: DENTPIN, visa sequence, ECE/WES, INBDE, SOP/CV/LOR, CAAPID/PASS, bench/interviews, and offer/matriculation prep.\n"
                "- Include the biggest lever explicitly in decisionNote or verdict (e.g., pass INBDE + admission-led F-1 pathway).\n"
                "- Stated target is intent, NOT a recommendation. For FTDs without INBDE + study visa + U.S. exposure, `primaryPathway` MUST be 'DDS/DMD via International Dentist Program (IDP) — ADEA CAAPID'. Only set Specialty Residency as primary when INBDE + visa + (U.S. exposure OR confirmed specialty-program FTD eligibility) are all present (HARD RULE 32).\n"
                "- Specialty flip is multi-conditional: INBDE + study visa + program-specific FTD eligibility + CODA DDS/DMD awareness + competitive specialty credentials — never 'INBDE alone unlocks specialty' (HARD RULE 33).\n"
                "- Visa dimension scoring caps: B1/B2 / none / tourist → ≤25 and red; active study/work visa → 55–75; permanent → 85–95. Never inflate B1/B2 into the 40+ range (HARD RULE 34).\n"
                "- TOEFL dimension status must be 'Strong' / 'Competitive' / 'Meets requirement' — never 'Excellent/Outstanding/Perfect'. Phrase TOEFL as 'competitive for most programs; does not differentiate at top-tier schools' (HARD RULE 35).\n"
                "- State card opportunity claims ('lower saturation', 'strong market', 'opportunity') must be licensure-gated: anchor on 'post-licensure' with the U.S.-recognized pathway completion required first (HARD RULE 36).\n"
                "- Do NOT suggest dental hygiene as an interim step for specialty/DDS-targeted or 5+ years experienced candidates unless the candidate explicitly signals hygiene interest (HARD RULE 37).\n"
                "- Every report must surface the DDS/DMD IDP reliability anchor — in verdict / bestPathwayForYou / secondaryStrategy / whyNotAlternatives / flipConditions / expertConclusion (HARD RULE 38).\n"
                "- `verdict` must state BOTH strength/weakness balance AND pathway realism (which pathway is realistic given current blockers) (HARD RULE 39).\n"
                "- Antipattern set must include at least one pathway-realism 'do not' (e.g., 'Do not rely on specialty alone without confirmed program-specific FTD eligibility') (HARD RULE 40).\n"
                "- readinessScore.overall must reflect readiness for the pathway you actually recommend — do not inflate because of a wish-list target (HARD RULE 41).\n"
                "- HONOR COMPLETED SIGNALS (HARD RULE 42): if the PROFILE ANALYSIS block marks INBDE as PASSED, you MUST NOT list 'schedule INBDE' / 'pass INBDE' / 'take INBDE' anywhere. Re-read next90DaysPlan, next12To18Months, applicationTimeline, mainRisks, readinessScore.gaps, dentnavServices, and remove any such items before returning.\n"
                "- ACTIVE-VISA FRAMING (HARD RULE 43): if the PROFILE ANALYSIS block marks visa as ACTIVE STUDY/WORK (F-1, J-1, H-1B, H-4, OPT, L-1/L-2), you MUST NOT write 'secure admission → I-20 → F-1', 'apply for F-1 visa', 'begin F-1 visa', 'plan F-1 visa sequence'. Replace with 'maintain F-1 status and coordinate I-20 transfer to the admitting program' or equivalent. The admission→I-20→F-1 acquisition flow applies ONLY to candidates with no visa / B1/B2.\n"
                "- BLOCKERS DISCIPLINE (HARD RULE 44): NEVER emit blockers: ['None'], ['None significant'], ['No major blockers'], or empty/vague variants. Every ranked pathway has at least one remaining conditional barrier — name it (e.g., 'Specialty program-specific FTD eligibility not yet verified', 'Admission + I-20 transfer not yet secured', 'ECE/WES not yet on file', 'Specialty credentials (CBSE / research) not documented', 'Funding execution not finalized').\n"
                "- VISA RISK WORDING (HARD RULE 45): for an active study/work visa, mainRisks visa items read 'Visa alignment with program requirements' or 'Maintain F-1 / transfer I-20 in time' — NEVER 'Visa pathway for specialty', 'Visa pathway limitation', 'Visa blocker', 'Study/work limitation'. impactColor is amber or teal, never red.\n"
                "- DO NOT RE-PRESCRIBE DONE STEPS (HARD RULE 46): in next90DaysPlan / next12To18Months / applicationTimeline, skip every step the candidate already has (INBDE pass, active visa acquisition, master's enrollment if already committed). Replace the slot with forward-looking work (program-specific FTD eligibility verification, SOP/LOR assembly, bench/interview prep, funding finalization, relocation/matriculation prep).\n"
                "- No boilerplate phrases; institutional terminology used throughout\n\n"
                f"Raw questionnaire answers:\n{_stringify_answers(answers)}"
            ),
        },
    ]

    try:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.15,
            max_tokens=10000,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": ANALYSIS_JSON_SCHEMA},
        )
    except Exception:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.3,
            max_tokens=10000,
            messages=messages,
            response_format={"type": "json_object"},
        )

    content = completion.choices[0].message.content or "{}"
    parsed = json.loads(_strip_markdown_code_fence(content))
    normalized = _normalize_response(parsed, answers)
    result = _sanitize_response_tree(normalized)
    braintrust.flush()
    return result