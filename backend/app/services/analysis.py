import json
import re
from datetime import date
from typing import Any

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
    if v in {"f1", "f-1", "j1", "j-1", "h4", "h-4", "h1", "h-1", "h1b", "h-1b",
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
    if visa_cat == "permanent":
        visa_score, visa = 95, ("Strong", "green")
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
    weighted = sum(d["score"] * w for d, w in zip(dims, weights))
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

_VERIFY_CAAPID_FALLBACK = "verify the current ADEA CAAPID program list — this school's IDP/advanced-standing status is not confirmed"


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
# Reasoning-quality guards (HARD RULES 19–24)
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


def _apply_reasoning_guards_to_text(text: Any, profile: dict[str, Any]) -> Any:
    if not isinstance(text, str) or not text.strip():
        return text
    out = text
    out = _rewrite_overconfident_readiness_phrasing(out, profile)
    out = _rewrite_visa_application_phrasing(out)
    out = _rewrite_complete_masters_phrasing(out)
    out = _rewrite_broad_portability_claims(out)
    return out


def _apply_reasoning_guards_tree(obj: Any, profile: dict[str, Any]) -> Any:
    if isinstance(obj, str):
        return _apply_reasoning_guards_to_text(obj, profile)
    if isinstance(obj, list):
        return [_apply_reasoning_guards_tree(x, profile) for x in obj]
    if isinstance(obj, dict):
        return {k: _apply_reasoning_guards_tree(v, profile) for k, v in obj.items()}
    return obj


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
        ("purple", "SOP, CV & LORs",
         "Draft personal statement; request LORs well before the portal season."),
        ("purple", "ADEA CAAPID / PASS portal season",
         "Finalize applications; track program-specific requirements and deadlines."),
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
# Full response normalization
# ─────────────────────────────────────────────────────────────────────────────


def _normalize_response(parsed: dict[str, Any], answers: AnswerMap) -> dict[str, Any]:
    profile = _build_profile_snapshot(parsed, answers)

    readiness_raw = parsed.get("readinessScore", {}) if isinstance(parsed.get("readinessScore"), dict) else {}
    performance = int(max(35, min(95, round(
        _extract_number(readiness_raw.get("overall")) or _estimate_performance_from_answers(answers)
    ))))
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
    if visa_cat == "none":
        parts.append(f"VISA: {visa} — CRITICAL GAP. Cannot enter U.S. without F-1/J-1.")
    elif visa_cat == "non-study":
        parts.append(f"VISA: {visa} — BLOCKER. B1/B2 cannot be used for study/work. Must change status.")
    elif visa_cat == "permanent":
        parts.append(f"VISA: {visa} — MAJOR STRENGTH. No immigration barrier. FAFSA-eligible.")
    else:
        parts.append(f"VISA: {visa} — Active visa. Map to education and employment pathway constraints.")

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
        parts.append("INBDE: PASSED — MAJOR STRENGTH. Most applications rejected without this.")
    elif inbde == "no":
        parts.append("INBDE: NOT PASSED — #1 BLOCKER. Most programs will not review.")
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

    client = AsyncOpenAI(api_key=settings.openai_api_key)

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
    return _sanitize_response_tree(normalized)