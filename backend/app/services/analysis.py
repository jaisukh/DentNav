import json
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.services.answers_validate import AnswerMap

KNOWLEDGE_BASE = """
# DENTNAV KNOWLEDGE BASE — U.S. PATHWAYS FOR FOREIGN-TRAINED DENTISTS (FTDs)

## PLATFORM PURPOSE
DentNav is a guidance platform for foreign-trained dentists pursuing U.S. dentistry.
Most FTDs do not fail because they lack talent — they struggle because they do not know
which pathway fits them, when the application cycle starts, how licensing differs by state,
or how to build a competitive profile before they apply.

## 1. CORE PATHWAY OVERVIEW

### 1A. DDS / DMD (INTERNATIONAL DENTIST PROGRAM — IDP)
- ~15 U.S. dental schools offer 2–3 year advanced-standing DDS/DMD tracks for FTDs.
- Application: ADEA CAAPID (opens June, deadline varies Oct–Feb by school).
  Schools weigh INBDE pass, TOEFL/IELTS, credential evaluation, clinical experience,
  personal statement narrative, 3+ LORs (at least one clinical supervisor), bench test,
  and interview.
- Holistic review: committees look for clinical maturity, cultural adaptability,
  and a clear "why U.S. dentistry" narrative — not just scores.
- DDS and DMD are academically equivalent; the naming depends on the school.
- Tuition: $150K–$350K total; limited institutional aid for internationals;
  most rely on private loans requiring a U.S. cosigner (citizen/green-card holder).
- Visa: most schools sponsor F-1; some accept H-4 EAD or green-card holders.
  F-1 OPT (12 months post-graduation) allows initial practice; long-term requires
  employer-sponsored H-1B or green-card pathway.
- Competitive edge: candidates with 3+ years of clinical practice, INBDE passed,
  TOEFL band ≥4.5, and strong narrative consistently outperform those missing any one pillar.
- IMPORTANT: Applicants often focus only on exams and forget bench test preparation
  and interview/communication skills — these are critical differentiators.

### 1B. DENTAL RESIDENCY (GPR / AEGD / SPECIALTY)
- GPR (General Practice Residency): 1–2 year hospital-based programs.
- AEGD (Advanced Education in General Dentistry): 1–2 year university-based programs.
- Application: ADEA PASS (opens mid-year, matches via MATCH in December).
- Purpose: broaden clinical exposure (medically complex patients, OR sedation,
  implants). Can serve as pathway to licensure in some states.
- Some states accept GPR/AEGD completion as a pathway to licensure without a separate
  clinical board exam — critical for states like New York (PGY-1 based pathway).
- Stipend: $55K–$75K/year; no tuition in many programs.
- Visa: J-1 most common; some offer H-1B. J-1 has 2-year home-country requirement
  unless waiver obtained (Conrad 30 / HHS underserved area).

### 1C. SPECIALTY PROGRAMS (ORTHO, OMFS, PERIO, ENDO, PEDO, PROSTHO, etc.)
- Some specialty residency programs accept foreign-trained dentists directly —
  eligibility varies by specialty AND by individual program. Do not assume DDS/DMD
  is always required first.
- Prior specialty training (e.g., MDS) from home country can significantly strengthen
  candidacy by demonstrating advanced training, thesis experience, procedural familiarity,
  and academic seriousness.
- Application: ADEA PASS; highly competitive. Research publications, U.S. clinical
  externships, and strong faculty LORs are near-essential.
- OMFS (Oral & Maxillofacial Surgery): usually requires U.S. DDS/DMD first, then
  separate OMFS application. One of the most complex pathways.

### 1D. DENTAL HYGIENE PATHWAY
- Separate licensure; state-specific. Many states require CODA-linked formal hygiene
  education and NBDHE/ADEX exams.
- Florida has a distinct route that may not require additional hygiene school for FTDs,
  but applicants still must satisfy the state's examination and licensing requirements.
- Useful for income and U.S. clinical exposure while pursuing DDS path.
- Does NOT count toward DDS/DMD admissions directly but demonstrates commitment.

### 1E. DENTAL ASSISTANT / RELATED ROLES
- State-specific requirements. Some states allow FTDs to work as assistants without
  formal certification; others require DANB certification or state registration.
- Helpful for building U.S. experience, networking, and familiarity with clinical systems.
- Other pre-licensure roles: research positions, public health, healthcare administration,
  marketing/product specialist, data-related healthcare roles, patient coordination,
  simulation lab educators, or faculty/instructor roles at dental schools (institution-
  and state-specific rules apply).

## 2. STRATEGIC APPLICATION PRINCIPLES

### 2A. DUAL-TRACK STRATEGY
- Applicants CAN apply for both DDS/DMD (via CAAPID) and residency (via PASS)
  simultaneously. Many successful FTDs do this.
- Key: each application must match the candidate's profile, specialty background,
  finances, and long-term plan. Avoid applying blindly to maximize volume.

### 2B. CHOOSING BETWEEN DDS/DMD AND RESIDENCY
- The right choice depends on profile fit, not online popularity.
- DDS/DMD: attractive for those seeking a broad U.S. degree pathway and access to
  traditional general practice routes. Wider recognition.
- Residency: especially attractive for applicants who already have specialty training,
  significant clinical experience, or a clear specialist identity they want to preserve.
- Specialization can offer stronger identity, defined scope, advanced procedural authority,
  and often higher long-term earning potential.
- General dentistry remains excellent; many applicants prefer the broader path.

### 2C. BUILDING COMPETITIVENESS BEFORE APPLYING
- U.S. graduate programs (MPH, MHA, MBA) build academic credentials, F-1 status,
  and networking with dental school faculty.
- Research roles, observerships, assistant roles, public health training, or healthcare
  administration pathways build U.S. exposure.
- Profile-building should be strategic, not just resume-padding.

## 3. EXAMS & CREDENTIALS

### 3A. INBDE (INTEGRATED NATIONAL BOARD DENTAL EXAMINATION)
- Pass/fail (no numeric score reported to schools). INBDE is generally pass/fail;
  selection depends on the entire application, not a numeric INBDE score.
- Required across multiple pathways, not only DDS/DMD.
- Tests foundational + clinical sciences, patient management, biomedical.
- Eligibility: FTDs can apply through ADA with credential evaluation.
- Preparation: 3–6 months typical; Bootcamp, Mental Dental, Booster, First Aid for
  INBDE are popular resources. Passing on first attempt matters — multiple attempts
  raise flags.
- Available year-round at Prometric centers.

### 3B. CREDENTIAL EVALUATION
- ECE (Educational Credential Evaluators) is commonly requested by programs to convert
  academic credentials into U.S.-readable format. WES also accepted.
- Course-by-course evaluation recommended (not just degree equivalency).
- Processing: 4–8 weeks standard; plan early relative to CAAPID deadline.

### 3C. ENGLISH PROFICIENCY
- IMPORTANT (as of January 2026): TOEFL iBT now uses a 1–6 band scale in 0.5-point
  increments (replacing the old 0–120 scale). Each section (Reading, Listening, Speaking,
  Writing) is scored 1–6; the total score is the average of four sections, rounded
  to nearest 0.5. This aligns with CEFR standards.
- Competitive threshold for most dental programs: TOEFL band ≥ 4.5. Top programs
  prefer band 5.0+.
- Band interpretation: 6 = expert, 5-5.5 = very strong, 4-4.5 = adequate for most
  programs, 3-3.5 = below threshold (most programs will flag this), 2-2.5 = significant
  barrier requiring intensive preparation.
- IELTS ≥7.0 remains an alternative accepted by most programs.
- Some schools accept Duolingo (≥120) or PTE (≥68).
- Scores valid for 2 years; time expiry relative to application cycle matters.
- A competitive English score significantly affects eligibility AND interview strength.
- The questionnaire captures TOEFL as a band score (2, 2.5, 3, ... 6). Always interpret
  the user's q9-toefl answer as a band score on the new 1–6 scale, NOT the old 0–120 scale.

## 4. VISA REALITIES
- F-1: student visa for DDS/DMD or master's programs; need I-20 from school + proof
  of funding. Student/scholar routes are favored for many applicants because they allow
  entry, academic progression, and later transition into employment-based options.
- H-4: spouse of H-1B; H-4 holders can study in the U.S. Those with EAD have additional
  flexibility. Schools/programs may prefer applicants who don't require visa sponsorship.
  EAD renewal uncertainty is a risk factor.
- Green Card / Citizen: no visa barrier; eligible for federal loans (FAFSA).
- J-1: for residency (GPR/AEGD/specialty); 2-year home-country requirement unless waived
  (Conrad 30 / HHS underserved area).
- B1/B2: cannot study or work; must change status (risky, not recommended as primary plan).
- No visa: cannot enter the U.S.; must apply from home country for F-1/J-1.
- IMPORTANT: Completing a DDS/DMD does NOT automatically lead to a green card.
  Immigration outcomes depend on visa category, employer sponsorship, and separate
  immigration processes — not on the dental degree alone.

## 5. FINANCING
- With cosigner (citizen/GC): private loans (Sallie Mae, Discover, Prodigy Finance for
  select schools) can cover most tuition.
- Without cosigner: very limited options; Prodigy Finance (select schools only),
  MPOWER Financing, or school-specific international scholarships.
- Cost varies dramatically by program, school, length, and whether the program charges
  tuition or offers a stipend. Residency is NOT always cheaper than DDS.
- Master's pathway (MPH, MHA, MBA): 1–2 years, $30K–$80K. Creates F-1 bridge, U.S.
  credentials, networking, and CPT/OPT opportunities.

## 6. STATE LICENSURE
- Licensure is state-by-state; earning a DDS/DMD does NOT automatically grant a license
  in any state. A degree helps qualify you, but you apply separately for a state license.
- No pathway gives automatic licensure everywhere.
- Most states require: DDS/DMD from CODA-accredited school + INBDE pass +
  regional clinical exam (CDCA/WREB/CITA) or state-specific exam.
- New York: PGY-1 (GPR/AEGD) based pathway may satisfy clinical exam requirement.
  Always verify current regulation with NY State authority.
- Minnesota: has a limited general dental license — a state-specific supervised pathway
  that may allow some FTDs to practice under supervision. Confirm with MN Board of Dentistry.
- Florida: distinct hygiene pathway that may not require additional hygiene school for FTDs.
  Still requires state exams and licensing.
- California, Florida, Texas: high FTD population; competitive but accessible pathways.
- Some states have residency requirements for licensure.
- Students should ALWAYS verify directly with the relevant state dental board.

## 7. TIMELINE REALITIES
- Fastest to practice: ~3 years (2-year DDS + licensure exam).
- With master's first: ~4–5 years total.
- GPR/AEGD → licensure (in accepting states): ~2 years.
- Planning should start 12–18 months before target application cycle.
- Many students underestimate timing. For a target intake year, preparation often starts
  many months earlier with INBDE, TOEFL, credentials, and documents ready BEFORE the
  portal opens.

## 8. RECOMMENDED STEP-BY-STEP ROADMAP
1. Clarify goal: general practice, specialty training, hygiene, assisting, teaching,
   research, or state-specific limited pathway.
2. Study the application cycle early — preparation starts months before portals open.
3. Complete credential evaluation (ECE) so schools can interpret transcripts.
4. Prepare for and pass INBDE — needed across most pathways.
5. Prepare TOEFL or equivalent — competitive score affects eligibility AND interviews.
6. Build profile: clinical experience, specialty background, research, publications,
   U.S. dental exposure, observerships, assistant roles, community work, or U.S.
   graduate study.
7. Choose programs strategically based on actual strengths, not scattershot.
8. Secure evaluations and LOR requests early — do not wait until deadline.
9. Prepare for bench tests AND interviews — often overlooked.
10. Research licensure state by state — degree/residency does not auto-grant license.

## 9. MYTHS VS FACTS
- MYTH: You cannot do residency without a DDS/DMD.
  FACT: Some residency programs accept FTDs directly; eligibility varies by specialty.
- MYTH: DDS/DMD automatically gives license in all 50 states.
  FACT: You must apply separately for state licensure; a degree helps qualify you.
- MYTH: INBDE score determines which residency you get.
  FACT: INBDE is pass/fail. Selection depends on the entire application.
- MYTH: Residency is always cheaper than DDS.
  FACT: Cost varies dramatically by program, school, length, and tuition vs stipend.
- MYTH: Residency is always two years.
  FACT: Program length varies — some are one year, others longer.
- MYTH: DDS is more valuable than DMD.
  FACT: DDS and DMD are academically equivalent.
- MYTH: Completing DDS automatically leads to a green card.
  FACT: Immigration depends on visa category, employer sponsorship, and immigration
  processes — not the dental degree alone.

## 10. COMMON MISTAKES FTDs MAKE
- Applying without INBDE passed → most schools won't review.
- Generic personal statement → committees can tell; must be specific to each school.
- Ignoring credential evaluation timeline → missed deadlines.
- Scattershot applications to 15+ schools → better to target 6–8 with tailored narratives.
- Underestimating U.S. clinical exposure value → externships/observerships differentiate.
- Not understanding visa implications of each pathway before committing.
- Focusing only on exams and forgetting bench test and interview preparation.
- Not knowing their own strengths or choosing programs that don't match their profile.
- Underestimating the overall timeline — the process involves multiple sequential steps.
- Confusing TOEFL score scales → the old 0–120 scale was retired Jan 2026;
  only the 1–6 band scale is current. Never reference "TOEFL 90" or "TOEFL 100" —
  use band scores (e.g., "TOEFL band 4.5" or "TOEFL band 5.0").

## 11. CAREER & COMPENSATION
- Income depends on procedures performed, efficiency, case mix, patient flow, and
  practice model. Many dentists are compensated on production-based models.
- Specialists may earn more than general dentists, but it depends on the specialty,
  region, and practice structure.
- Specialization can provide stronger professional identity, advanced scope, greater
  procedural confidence, and often higher long-term leverage — but is not automatically
  the best choice for every applicant.

## DISCLAIMERS (ALWAYS HONOR)
- No guarantees of admission, visa outcomes, or licensure.
- Dental licensure, visa sponsorship, residency eligibility, and state board rules
  can change. Always verify with official sources (school websites, state dental boards,
  ADEA portals, immigration/legal counsel).
- DentNav provides strategic guidance, not legal or immigration advice.
""".strip()


def load_analysis_mock() -> dict[str, Any]:
    return json.loads(settings.analysis_mock_path.read_text(encoding="utf-8"))


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


def _sanitize_legacy_toefl_scale_text(text: str) -> str:
    """Remove/replace obsolete TOEFL 0–120 total-score language models often hallucinate."""
    if not text or not text.strip():
        return text
    s = text
    # Scale name / denominator
    s = re.sub(r"(?i)\b0\s*[–-]\s*120\b", "1–6 band", s)
    s = re.sub(r"(?i)\bout of\s*120\b", "on the 1–6 band scale", s)
    s = re.sub(r"(?i)\b/\s*120\b", " (1–6 band scale)", s)
    s = re.sub(r"(?i)\b(?:maximum|max|total)\s*(?:score\s*)?(?:of\s*)?120\b", "maximum band 6", s)
    s = re.sub(r"(?i)\b120[- ]point\b", "6-point band", s)
    # Legacy "competitive total" ranges → band language
    s = re.sub(
        r"(?i)\b(?:scores?\s+)?(?:in\s+)?(?:the\s+)?(?:range\s+of\s+)?(?:90|9[0-9])\s*[–-]\s*(?:100|11[0-9]|120)\b",
        "competitive TOEFL bands (about 4.5–6.0 on the 1–6 scale)",
        s,
    )
    s = re.sub(
        r"(?i)\b(?:90|9[0-9]|100|10[0-9]|11[0-9]|120)\s+to\s+(?:100|11[0-9]|120)\b",
        "4.5 to 6.0 bands",
        s,
    )
    # "TOEFL ... 100" style legacy totals (only when clearly a single total score, not band decimals)
    s = re.sub(
        r"(?i)\b(TOEFL(?:\s+iBT)?)\s+(?:total\s+)?(?:score\s+)?(?:of\s+)?(8[0-9]|9[0-9]|100|10[0-9]|11[0-9]|120)\b",
        r"\1 band score (1–6 scale only)",
        s,
    )
    s = re.sub(
        r"(?i)\b(?:a\s+)?(8[0-9]|9[0-9]|100|10[0-9]|11[0-9]|120)\s+(?:on|out of)\s+(?:the\s+)?(?:TOEFL|TOEFL\s+iBT)\b",
        "a TOEFL band on the 1–6 scale",
        s,
    )
    # Lingering "iBT ... 120" phrasing
    s = re.sub(r"(?i)\biBT\s*\(?\s*0\s*[–-]\s*120\s*\)?", "iBT (1–6 band scale)", s)
    return s


def _sanitize_response_legacy_toefl(obj: Any) -> Any:
    """Apply legacy TOEFL sanitizer to every string in the response tree."""
    if isinstance(obj, str):
        return _sanitize_legacy_toefl_scale_text(obj)
    if isinstance(obj, list):
        return [_sanitize_response_legacy_toefl(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize_response_legacy_toefl(v) for k, v in obj.items()}
    return obj


def _stringify_answers(answers: AnswerMap) -> str:
    raw = {k: (v if isinstance(v, list) else v) for k, v in answers.items()}
    return json.dumps(raw, ensure_ascii=False, indent=2, sort_keys=True)


def _normalize_body(value: Any) -> list[str]:
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


def _clinical_years_score_component(answer: str) -> float:
    s = answer.strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", s)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2.0
    n = _extract_number(s)
    return n if n is not None else 0.0


def _estimate_performance_from_answers(answers: AnswerMap) -> int:
    score = 58.0

    inbde_raw = answers.get("q8-inbde", "")
    inbde = inbde_raw.strip().lower() if isinstance(inbde_raw, str) else ""
    if inbde == "yes":
        score += 12
    elif inbde == "no":
        score -= 5

    years_raw = answers.get("q7-clinical-years", "")
    if isinstance(years_raw, str):
        years = _clinical_years_score_component(years_raw)
        if years >= 8:
            score += 10
        elif years >= 4:
            score += 7
        elif years >= 2:
            score += 4
        elif years < 1:
            score -= 3

    toefl_raw = answers.get("q9-toefl", "")
    toefl_band = _extract_number(toefl_raw) if isinstance(toefl_raw, str) else None
    if toefl_band is not None:
        if toefl_band >= 5:
            score += 8
        elif toefl_band >= 4:
            score += 5
        elif toefl_band >= 3:
            score += 2
        else:
            score -= 2

    target_raw = answers.get("q2-target-program", "")
    target_program = target_raw.strip().lower() if isinstance(target_raw, str) else ""
    if "i don't know" in target_program or "guidance" in target_program:
        score -= 3
    elif target_program:
        score += 2

    return int(max(35, min(95, round(score))))


def _extract_performance_score(parsed: dict[str, Any], answers: AnswerMap) -> int:
    candidate = parsed.get("Performance")
    if isinstance(candidate, dict):
        for key in ("score", "value", "performance"):
            if key in candidate:
                number = _extract_number(candidate.get(key))
                if number is not None:
                    return int(max(35, min(95, round(number))))
    number = _extract_number(candidate)
    if number is not None:
        return int(max(35, min(95, round(number))))
    return _estimate_performance_from_answers(answers)


def _normalize_section(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return {
            "heading": str(raw.get("heading", "")),
            "body": _normalize_body(raw.get("body")),
        }
    return {"heading": "", "body": []}


def _normalize_action_item(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return {
            "action": str(raw.get("action", "")),
            "timeline": str(raw.get("timeline", "")),
            "why": str(raw.get("why", "")),
        }
    return {"action": "", "timeline": "", "why": ""}


def _toefl_band_to_legacy_total(value: Any) -> int | None:
    """Convert TOEFL 1–6 band to approximate legacy 0–120 equivalent."""
    n = _extract_number(value)
    if n is None:
        return None
    # Clamp to official band range first, then map linearly to legacy 120 scale.
    n = max(1.0, min(6.0, n))
    return int(round(n * 20))


def _list_of_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_risk_item(raw: Any) -> dict[str, str]:
    if isinstance(raw, dict):
        return {
            "issue": str(raw.get("issue", "")).strip(),
            "impact": str(raw.get("impact", "")).strip(),
            "note": str(raw.get("note", "")).strip(),
            "evidenceBasis": str(raw.get("evidenceBasis", "")).strip(),
            "assessmentType": str(raw.get("assessmentType", "")).strip(),
        }
    return {
        "issue": "",
        "impact": "",
        "note": "",
        "evidenceBasis": "",
        "assessmentType": "",
    }


def _default_readiness_status(score: int) -> str:
    if score >= 85:
        return "High readiness with targeted refinements needed"
    if score >= 70:
        return "Strong potential but not fully application-ready yet"
    if score >= 55:
        return "Promising but not application-ready yet"
    return "Early stage profile; foundational gaps must be closed first"


def _build_questionnaire_grounding(answers: AnswerMap) -> list[dict[str, str]]:
    """Evidence ledger tied only to questionnaire inputs."""
    mapping: list[tuple[str, str]] = [
        ("q1-degree-country", "Degree country influences pathway context and credential comparability framing."),
        ("q1b-degree-type", "Degree type anchors eligibility framing for FTD pathways."),
        ("q2-target-program", "Target program determines the primary pathway recommendation."),
        ("q3-practice-states", "State preferences shape licensure planning and school strategy."),
        ("q4-visa", "Visa status affects near-term feasibility and sequencing."),
        ("q5-masters-vs-home", "Master's willingness changes bridge strategy options."),
        ("q6-loan-cosigner", "Cosigner availability is a partial financing signal (not full financial profile)."),
        ("q7-clinical-years", "Clinical years contribute to competitiveness and narrative strength."),
        ("q8-inbde", "INBDE status is a major readiness signal for many pathways."),
        ("q9-toefl", "TOEFL band indicates English readiness (1–6 scale)."),
        ("q10-start-cycle", "Target cycle defines urgency and roadmap pacing."),
    ]
    ledger: list[dict[str, str]] = []
    for qid, influence in mapping:
        raw = answers.get(qid, "")
        if isinstance(raw, list):
            answer = ", ".join(str(x) for x in raw if str(x).strip()) or "Not provided"
        else:
            answer = str(raw).strip() or "Not provided"
        ledger.append({"questionId": qid, "answer": answer, "pathwayInfluence": influence})
    return ledger


def _assessment_boundaries_default() -> list[str]:
    return [
        "Detailed budget, liquid funds, and tuition affordability were not collected.",
        "Academic GPA/class rank and transcript detail were not collected.",
        "Bench test performance and interview readiness were not directly collected.",
        "Research/publication depth and U.S. exposure quality were not directly collected.",
        "Final licensure eligibility must be verified with each state board.",
    ]


def _normalize_response(parsed: dict[str, Any], answers: AnswerMap) -> dict[str, Any]:
    country_raw = str(answers.get("q1-degree-country", "")).strip()
    degree_raw = str(answers.get("q1b-degree-type", "")).strip()
    years_raw = str(answers.get("q7-clinical-years", "")).strip()
    target_program_raw = str(answers.get("q2-target-program", "")).strip()
    visa_raw = str(answers.get("q4-visa", "")).strip()
    masters_raw = str(answers.get("q5-masters-vs-home", "")).strip()
    cosigner_raw = str(answers.get("q6-loan-cosigner", "")).strip()
    inbde_raw = str(answers.get("q8-inbde", "")).strip()
    toefl_raw = str(answers.get("q9-toefl", "")).strip()
    cycle_raw = str(answers.get("q10-start-cycle", "")).strip()

    states_raw = answers.get("q3-practice-states", [])
    preferred_states = _list_of_strings(states_raw)

    toefl_legacy = _toefl_band_to_legacy_total(toefl_raw)
    profile_snapshot_default = {
        "country": country_raw or "Unknown",
        "degree": degree_raw or "Not specified",
        "clinicalExperience": years_raw or "Not specified",
        "targetProgram": target_program_raw or "Not specified",
        "preferredStates": preferred_states,
        "visaStatus": visa_raw or "Not specified",
        "mastersInterest": masters_raw or "Not specified",
        "loanCosigner": cosigner_raw or "Not specified",
        "inbdeStatus": inbde_raw or "Not specified",
        "toeflScore": toefl_raw or "Not specified",
        "toeflLegacyEquivalent120": f"{toefl_legacy}/120" if toefl_legacy is not None else "",
        "targetCycle": cycle_raw or "Not specified",
    }

    profile_raw = parsed.get("profileSnapshot", {})
    profile_snapshot = dict(profile_snapshot_default)
    if isinstance(profile_raw, dict):
        for key in profile_snapshot:
            val = profile_raw.get(key)
            if key == "preferredStates":
                normalized_states = _list_of_strings(val)
                if normalized_states:
                    profile_snapshot[key] = normalized_states
            elif val is not None and str(val).strip():
                profile_snapshot[key] = str(val).strip()

    performance = _extract_performance_score(parsed, answers)

    readiness_raw = parsed.get("readinessScore", {})
    readiness_status = _default_readiness_status(performance)
    readiness_strengths: list[str] = []
    readiness_gaps: list[str] = []
    if isinstance(readiness_raw, dict):
        maybe_overall = _extract_number(readiness_raw.get("overall"))
        if maybe_overall is not None:
            performance = int(max(35, min(95, round(maybe_overall))))
        if isinstance(readiness_raw.get("status"), str) and readiness_raw.get("status", "").strip():
            readiness_status = str(readiness_raw.get("status")).strip()
        readiness_strengths = _list_of_strings(readiness_raw.get("strengths"))
        readiness_gaps = _list_of_strings(readiness_raw.get("gaps"))

    pathway_raw = parsed.get("pathwayRecommendation", {})
    pathway = {
        "primaryPathway": "",
        "verdict": "",
        "whyThisFits": [],
        "secondaryStrategy": "",
    }
    if isinstance(pathway_raw, dict):
        pathway["primaryPathway"] = str(pathway_raw.get("primaryPathway", "")).strip()
        pathway["verdict"] = str(pathway_raw.get("verdict", "")).strip()
        pathway["whyThisFits"] = _list_of_strings(pathway_raw.get("whyThisFits"))
        pathway["secondaryStrategy"] = str(pathway_raw.get("secondaryStrategy", "")).strip()

    risks: list[dict[str, str]] = []
    for item in parsed.get("mainRisks", []) if isinstance(parsed.get("mainRisks", []), list) else []:
        risk = _normalize_risk_item(item)
        if risk["issue"] or risk["note"]:
            issue_l = risk["issue"].lower()
            # Prevent overclaiming when we do not have full financial details.
            if ("financ" in issue_l or "loan" in issue_l or "cosigner" in issue_l) and not cosigner_raw:
                risk["impact"] = "Unassessed"
                risk["assessmentType"] = "Unassessed"
                risk["note"] = (
                    "Only partial financing data is available from questionnaire. "
                    "Treat this as unassessed until budget/funding details are collected."
                )
            # Prevent false English blocker when TOEFL is already competitive.
            if "english" in issue_l or "toefl" in issue_l:
                n = _extract_number(toefl_raw)
                if n is not None and n >= 4.5:
                    if risk["impact"].lower() in {"high", "critical"}:
                        risk["impact"] = "Low"
                    if not risk["assessmentType"]:
                        risk["assessmentType"] = "Evidence-Based"
                    if "strength" not in risk["note"].lower():
                        risk["note"] = (
                            "TOEFL band is at/above threshold; English is not a major blocker "
                            "based on collected inputs."
                        )
            risks.append(risk)

    next_90_days = _list_of_strings(parsed.get("next90DaysPlan"))
    next_12_18_months = _list_of_strings(parsed.get("next12To18Months"))
    state_planning_note = str(parsed.get("statePlanningNote", "")).strip()
    expert_conclusion = str(parsed.get("expertConclusion", "")).strip()
    assessment_boundaries = _list_of_strings(parsed.get("assessmentBoundaries"))
    if not assessment_boundaries:
        assessment_boundaries = _assessment_boundaries_default()
    questionnaire_grounding = parsed.get("questionnaireGrounding", [])
    if not isinstance(questionnaire_grounding, list) or not questionnaire_grounding:
        questionnaire_grounding = _build_questionnaire_grounding(answers)

    sections: list[dict[str, Any]] = []
    for item in parsed.get("sections", []) if isinstance(parsed.get("sections", []), list) else []:
        sec = _normalize_section(item)
        if sec["heading"] and sec["body"]:
            sections.append(sec)

    action_plan: list[dict[str, str]] = []
    for item in parsed.get("actionPlan", []) if isinstance(parsed.get("actionPlan", []), list) else []:
        act = _normalize_action_item(item)
        if act["action"]:
            action_plan.append(act)

    executive_summary = str(parsed.get("executiveSummary", "")).strip()
    key_insight = str(parsed.get("keyInsight", "")).strip()
    body = _normalize_body(parsed.get("Body"))
    if not body and not sections:
        body = _normalize_body(load_analysis_mock().get("Body"))

    # Backward-compatible envelope fields
    result: dict[str, Any] = {
        "responseSchemaVersion": "v2-premium",
        "Country": profile_snapshot["country"],
        "degree": profile_snapshot["degree"],
        "yearsOfExp": profile_snapshot["clinicalExperience"],
        "Performance": performance,
        # Premium report contract
        "profileSnapshot": profile_snapshot,
        "readinessScore": {
            "overall": performance,
            "status": readiness_status,
            "strengths": readiness_strengths,
            "gaps": readiness_gaps,
        },
        "pathwayRecommendation": pathway,
        "mainRisks": risks,
        "next90DaysPlan": next_90_days,
        "next12To18Months": next_12_18_months,
        "questionnaireGrounding": questionnaire_grounding,
        "assessmentBoundaries": assessment_boundaries,
        "statePlanningNote": state_planning_note
        or "State licensure rules vary by state and can change. Verify with official state board sources before final decisions.",
        "expertConclusion": expert_conclusion,
    }

    if executive_summary:
        result["executiveSummary"] = executive_summary
    if sections:
        result["sections"] = sections
    if action_plan:
        result["actionPlan"] = action_plan
    if key_insight:
        result["keyInsight"] = key_insight
    if body:
        result["Body"] = body

    return result


def _interpret_toefl_band(band: str) -> str:
    """Pre-interpret TOEFL and include approximate legacy-equivalent for model calibration."""
    n = _extract_number(band)
    if n is None:
        return "unknown TOEFL value"
    legacy = _toefl_band_to_legacy_total(n)
    legacy_note = f"(approx legacy equivalent: {legacy}/120)" if legacy is not None else ""
    if n >= 5.5:
        return f"band {n} {legacy_note} — EXCELLENT. This is a major strength. Do NOT recommend improving English."
    if n >= 5.0:
        return f"band {n} {legacy_note} — VERY STRONG. Above threshold. This is a strength. Do NOT recommend improving English."
    if n >= 4.5:
        return f"band {n} {legacy_note} — COMPETITIVE. Meets threshold for most programs."
    if n >= 4.0:
        return f"band {n} {legacy_note} — BORDERLINE. Slightly below threshold; improvement recommended."
    if n >= 3.0:
        return f"band {n} {legacy_note} — BELOW THRESHOLD. Significant English preparation needed."
    return f"band {n} {legacy_note} — CRITICAL GAP. Intensive English preparation required."


def _build_profile_summary(answers: AnswerMap) -> str:
    """Pre-analyze the profile so the model gets clear directives on strengths vs gaps."""
    parts = []

    country = answers.get("q1-degree-country", "Unknown")
    degree = answers.get("q1b-degree-type", "Unknown")
    parts.append(f"COUNTRY: {country}, DEGREE: {degree}")

    target = answers.get("q2-target-program", "Not specified")
    parts.append(f"TARGET PROGRAM: {target}")

    states = answers.get("q3-practice-states", [])
    if isinstance(states, list) and states:
        parts.append(f"TARGET STATES: {', '.join(states)}")
    elif isinstance(states, str) and states:
        parts.append(f"TARGET STATES: {states}")

    visa = answers.get("q4-visa", "Not specified")
    parts.append(f"VISA STATUS: {visa}")

    masters = answers.get("q5-masters-vs-home", "Not specified")
    parts.append(f"MASTER'S PREFERENCE: {masters}")

    cosigner = answers.get("q6-loan-cosigner", "Not specified")
    parts.append(f"LOAN COSIGNER: {cosigner}")

    years = answers.get("q7-clinical-years", "Not specified")
    if isinstance(years, str):
        y = _clinical_years_score_component(years)
        if y >= 5:
            parts.append(f"CLINICAL YEARS: {years} — STRONG. Above average for FTD applicants.")
        elif y >= 3:
            parts.append(f"CLINICAL YEARS: {years} — SOLID. Meets expectations for most programs.")
        elif y >= 1:
            parts.append(f"CLINICAL YEARS: {years} — LIMITED. Below the competitive range; U.S. exposure could compensate.")
        else:
            parts.append(f"CLINICAL YEARS: {years} — MINIMAL. This is a gap that needs addressing.")

    inbde = answers.get("q8-inbde", "Not specified")
    if isinstance(inbde, str):
        if inbde.strip().lower() == "yes":
            parts.append("INBDE: PASSED — This is a major strength. Most FTD applications are rejected without this.")
        else:
            parts.append("INBDE: NOT PASSED — This is the #1 gap. Most programs will not review without a pass.")

    toefl = answers.get("q9-toefl", "")
    if isinstance(toefl, str) and toefl.strip():
        legacy = _toefl_band_to_legacy_total(toefl)
        if legacy is not None:
            parts.append(f"TOEFL RAW INPUT: band {toefl}; converted equivalent = {legacy}/120 for model calibration.")
        parts.append(f"TOEFL INTERPRETATION: {_interpret_toefl_band(toefl)}")

    cycle = answers.get("q10-start-cycle", "Not specified")
    parts.append(f"TARGET CYCLE: {cycle}")

    return "\n".join(parts)


SYSTEM_PROMPT_TEMPLATE = """You are DentNav — the most expert pathway strategist for foreign-trained dentists (FTDs) pursuing U.S. dentistry.

HARD RULES (violating any = failed response):
1. Return JSON only (no markdown, no prose outside JSON).
2. The questionnaire TOEFL value is on 1–6 band scale, but you are provided an equivalent 0–120 conversion in PROFILE ANALYSIS to prevent misclassification.
3. If TOEFL band is 4.5+ (or equivalent >=90/120), do NOT classify English as a major blocker.
4. Every section must visibly use profile signals: visa, cosigner, target cycle, state preference, INBDE, TOEFL, and master's willingness.
5. Tone must be calibrated honesty: clear, direct, high-value, not generic praise.
6. DO NOT assume facts not collected in questionnaire. If a factor is not collected, mark it "Unassessed" instead of labeling as high risk.

PROFILE ANALYSIS (use this — I've already interpreted their strengths and gaps):
{profile_summary}

JSON SCHEMA — return ONLY this structure:
{{
  "responseSchemaVersion": "v2-premium",
  "profileSnapshot": {{
    "country": "string",
    "degree": "string",
    "clinicalExperience": "string",
    "targetProgram": "string",
    "preferredStates": ["string"],
    "visaStatus": "string",
    "mastersInterest": "string",
    "loanCosigner": "string",
    "inbdeStatus": "string",
    "toeflScore": "string",
    "toeflLegacyEquivalent120": "string",
    "targetCycle": "string"
  }},
  "readinessScore": {{
    "overall": 0,
    "status": "string",
    "strengths": ["string"],
    "gaps": ["string"]
  }},
  "pathwayRecommendation": {{
    "primaryPathway": "string",
    "verdict": "string",
    "whyThisFits": ["string"],
    "secondaryStrategy": "string"
  }},
  "mainRisks": [
    {{"issue": "string", "impact": "High|Medium|Low|Unassessed", "note": "string", "evidenceBasis": "string", "assessmentType": "Evidence-Based|Unassessed"}}
  ],
  "next90DaysPlan": ["string"],
  "next12To18Months": ["string"],
  "questionnaireGrounding": [
    {{"questionId": "qX", "answer": "string", "pathwayInfluence": "string"}}
  ],
  "assessmentBoundaries": ["string"],
  "statePlanningNote": "string",
  "expertConclusion": "string"
}}

CONTENT QUALITY REQUIREMENTS:
- "profileSnapshot" must echo the user's values accurately.
- "readinessScore.overall" must be 35–95 and aligned to evidence.
- "readinessScore.status" should be one decisive verdict line (for example: "Promising but not application-ready yet").
- "whyThisFits", "strengths", and "gaps" should be concrete bullets, not generic phrases.
- "mainRisks" must be evidence-bound to collected fields; if evidence is missing, use impact "Unassessed".
- "next90DaysPlan" must have 6 clear actions.
- "next12To18Months" must have 5 strategic milestones.
- "questionnaireGrounding" must explicitly show how each collected answer shaped the pathway.
- "assessmentBoundaries" must list what was not collected and therefore not inferred.
- Mention that there is no universal path; fit depends on profile, finances, visa, and goals.
- Mention state licensure is state-specific and must be verified with boards.
- If target cycle is farther out (e.g., 2028), explicitly call this out as planning advantage.

{knowledge_base}"""


ANALYSIS_JSON_SCHEMA: dict[str, Any] = {
    "name": "dentnav_premium_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "responseSchemaVersion",
            "profileSnapshot",
            "readinessScore",
            "pathwayRecommendation",
            "mainRisks",
            "next90DaysPlan",
            "next12To18Months",
            "questionnaireGrounding",
            "assessmentBoundaries",
            "statePlanningNote",
            "expertConclusion",
        ],
        "properties": {
            "responseSchemaVersion": {"type": "string"},
            "profileSnapshot": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "country",
                    "degree",
                    "clinicalExperience",
                    "targetProgram",
                    "preferredStates",
                    "visaStatus",
                    "mastersInterest",
                    "loanCosigner",
                    "inbdeStatus",
                    "toeflScore",
                    "toeflLegacyEquivalent120",
                    "targetCycle",
                ],
                "properties": {
                    "country": {"type": "string"},
                    "degree": {"type": "string"},
                    "clinicalExperience": {"type": "string"},
                    "targetProgram": {"type": "string"},
                    "preferredStates": {"type": "array", "items": {"type": "string"}},
                    "visaStatus": {"type": "string"},
                    "mastersInterest": {"type": "string"},
                    "loanCosigner": {"type": "string"},
                    "inbdeStatus": {"type": "string"},
                    "toeflScore": {"type": "string"},
                    "toeflLegacyEquivalent120": {"type": "string"},
                    "targetCycle": {"type": "string"},
                },
            },
            "readinessScore": {
                "type": "object",
                "additionalProperties": False,
                "required": ["overall", "status", "strengths", "gaps"],
                "properties": {
                    "overall": {"type": "number"},
                    "status": {"type": "string"},
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "gaps": {"type": "array", "items": {"type": "string"}},
                },
            },
            "pathwayRecommendation": {
                "type": "object",
                "additionalProperties": False,
                "required": ["primaryPathway", "verdict", "whyThisFits", "secondaryStrategy"],
                "properties": {
                    "primaryPathway": {"type": "string"},
                    "verdict": {"type": "string"},
                    "whyThisFits": {"type": "array", "items": {"type": "string"}},
                    "secondaryStrategy": {"type": "string"},
                },
            },
            "mainRisks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["issue", "impact", "note", "evidenceBasis", "assessmentType"],
                    "properties": {
                        "issue": {"type": "string"},
                        "impact": {"type": "string"},
                        "note": {"type": "string"},
                        "evidenceBasis": {"type": "string"},
                        "assessmentType": {"type": "string"},
                    },
                },
            },
            "next90DaysPlan": {"type": "array", "items": {"type": "string"}},
            "next12To18Months": {"type": "array", "items": {"type": "string"}},
            "questionnaireGrounding": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["questionId", "answer", "pathwayInfluence"],
                    "properties": {
                        "questionId": {"type": "string"},
                        "answer": {"type": "string"},
                        "pathwayInfluence": {"type": "string"},
                    },
                },
            },
            "assessmentBoundaries": {"type": "array", "items": {"type": "string"}},
            "statePlanningNote": {"type": "string"},
            "expertConclusion": {"type": "string"},
        },
    },
}


async def generate_analysis_from_answers(answers: AnswerMap) -> dict[str, Any]:
    if not settings.has_openai_config:
        raise ValueError("Missing OPENAI_API_KEY")

    profile_summary = _build_profile_summary(answers)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        profile_summary=profile_summary,
        knowledge_base=KNOWLEDGE_BASE,
    )

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Generate this person's pathway analysis now. Remember:\n"
                "- Follow the exact JSON schema in the system prompt\n"
                "- Use the profile signals explicitly (visa, cosigner, target cycle, states, INBDE, TOEFL, master's)\n"
                "- TOEFL is provided as band and converted equivalent; calibrate correctly (band 5 ~= 100/120 and is strong)\n"
                "- Be specific, verdict-first, and roadmap-oriented\n\n"
                f"Raw answers:\n{_stringify_answers(answers)}"
            ),
        },
    ]

    completion = await client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.35,
        max_tokens=4096,
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content or "{}"
    parsed = json.loads(_strip_markdown_code_fence(content))
    return _normalize_response(parsed, answers)
