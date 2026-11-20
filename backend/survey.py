"""Onboarding survey ("How do you study?").

The questions are defined here once; the browser renders them from
GET /api/profile/questions, and answers are validated against the same list.

Design rules (see docs/PERSONALIZATION.md and docs/research/):
* Non-diagnostic. No question asks about ADHD, any diagnosis, or medication.
  Adapted needs are offered to everyone as opt-in "focus support options".
* Original wording. Items are *informed by* published constructs (cited in
  `construct`), not copied from copyrighted instruments.
* Every question is optional, and the whole survey can be skipped or retaken.
* Answers are PRODUCT data used only to personalize the app for that user.
  They are never research data for the science-fair experiment, which uses
  simulated students only (human-participant research would need IRB/SRC
  approval under ISEF rules).
"""

from . import validation as v

FREQ = ["never", "rarely", "sometimes", "often", "always"]
FREQ_LABELS = ["Never", "Rarely", "Sometimes", "Often", "Always"]

SUPPORT_OPTIONS = [
    ("short_blocks", "Shorter study blocks with a break timer"),
    ("calm_mode", "Calm focus mode (hide everything except my task and timer)"),
    ("big_timer", "A big visual countdown so I can see time passing"),
    ("nudges", "Gentle nudges when I drift"),
    ("checkins", "Quick self check-ins (\"Was I on task just now?\")"),
    ("if_then", "An if-then plan for distractions at the start of each session"),
]

QUESTIONS = [
    {"id": "age_band", "section": "About you", "type": "choice",
     "text": "Which age group are you in?",
     "options": [["13-14", "13-14"], ["15-16", "15-16"], ["17-18", "17-18"], ["19+", "19 or older"]],
     "why": "Used only to choose sensible default session lengths.",
     "construct": "Practical"},
    {"id": "goal", "section": "About you", "type": "choice",
     "text": "What is your main study goal right now?",
     "options": [["test", "An upcoming test or exam"], ["homework", "Keeping up with homework"],
                 ["project", "A long-term project"], ["habits", "Building better study habits"]],
     "why": "Tells the planner whether to prioritize review before a deadline.",
     "construct": "Practical"},
    {"id": "alert_time", "section": "Your day", "type": "choice",
     "text": "When do you usually feel most alert?",
     "options": [["morning", "Morning"], ["afternoon", "Afternoon"], ["evening", "Evening"], ["night", "Late night"]],
     "why": "A starting guess for your best study time, until your own sessions show it.",
     "construct": "Chronotype (informed by the reduced Morningness-Eveningness Questionnaire; Adan & Almirall 1991)"},
    {"id": "wake_school", "section": "Your day", "type": "time",
     "text": "What time do you usually wake up on school days?",
     "why": "Together with the next question, estimates whether you are more of a morning or evening person.",
     "construct": "Chronotype (informed by the Munich ChronoType Questionnaire; Roenneberg et al. 2003)"},
    {"id": "wake_free", "section": "Your day", "type": "time",
     "text": "What time do you usually wake up on days off?",
     "why": "Sleeping much later on free days suggests an evening chronotype.",
     "construct": "Chronotype (MCTQ; Roenneberg et al. 2003)"},
    {"id": "place", "section": "Where and how you study", "type": "choice",
     "text": "Where do you usually study?",
     "options": [["desk", "At a desk"], ["bed", "On my bed or couch"], ["kitchen", "Kitchen or shared table"],
                 ["library", "Library or school"], ["other", "Somewhere else"]],
     "why": "Helps interpret your camera data (e.g. studying on a bed changes head angles).",
     "construct": "Study environment (informed by the MSLQ Time and Study Environment scale; Pintrich et al. 1991)"},
    {"id": "phone_pull", "section": "Where and how you study", "type": "scale",
     "text": "How often do your phone or other apps pull you away while studying?",
     "why": "If often, nudges and calm focus mode are suggested.",
     "construct": "Study environment management (MSLQ; Pintrich et al. 1991)"},
    {"id": "plans_ahead", "section": "Where and how you study", "type": "scale",
     "text": "How often do you plan your study time ahead?",
     "why": "If rarely, the personal plan does more of the scheduling for you.",
     "construct": "Time management (MSLQ Time and Study Environment; Pintrich et al. 1991)"},
    {"id": "keeps_going", "section": "Where and how you study", "type": "scale",
     "text": "When studying gets boring or hard, how often do you keep going anyway?",
     "why": "If rarely, shorter blocks with planned breaks are suggested.",
     "construct": "Effort regulation (MSLQ Effort Regulation; Pintrich et al. 1991)"},
    {"id": "starts_late", "section": "Where and how you study", "type": "scale",
     "text": "How often do you start assignments later than you meant to?",
     "why": "If often, the plan starts work earlier and adds more buffer time.",
     "construct": "Procrastination (informed by the Pure Procrastination Scale; Steel 2010)"},
    {"id": "break_after", "section": "Where and how you study", "type": "choice",
     "text": "How long can you usually study before you need a break?",
     "options": [["10", "About 10 minutes"], ["15", "About 15 minutes"], ["25", "About 25 minutes"],
                 ["45", "About 45 minutes"], ["60", "An hour or more"]],
     "why": "Your starting block length. Your own sessions adjust it over time.",
     "construct": "Practical; default range from Biwer et al. 2023 and Albulescu et al. 2022"},
    {"id": "supports", "section": "Focus support options", "type": "multi",
     "text": "Which of these would help you? Choose any (you can change them later in Settings).",
     "options": [list(o) for o in SUPPORT_OPTIONS],
     "why": "Turns on features designed to make studying easier. Available to everyone.",
     "construct": "Executive-function supports; W3C COGA 'Help users focus'; self-monitoring (Briesch & Briesch 2016)"},
]
QUESTION_IDS = [q["id"] for q in QUESTIONS]


def public_questions():
    out = []
    for q in QUESTIONS:
        q = dict(q)
        if q["type"] == "scale":
            q["options"] = [[k, lbl] for k, lbl in zip(FREQ, FREQ_LABELS)]
        out.append(q)
    return out


def validate_answers(raw):
    """Return a cleaned dict containing only known questions with valid answers.
    Missing or blank answers are simply left out (every question is optional)."""
    if not isinstance(raw, dict):
        raise v.ValidationError("answers must be an object")
    clean = {}
    for q in QUESTIONS:
        val = raw.get(q["id"])
        if val in (None, "", []):
            continue
        if q["type"] == "scale":
            if val not in FREQ:
                raise v.ValidationError(f"{q['id']}: choose one of {', '.join(FREQ)}")
        elif q["type"] == "choice":
            if val not in [o[0] for o in q["options"]]:
                raise v.ValidationError(f"{q['id']}: invalid choice")
        elif q["type"] == "multi":
            keys = {o[0] for o in q["options"]}
            if not isinstance(val, list) or not all(x in keys for x in val):
                raise v.ValidationError(f"{q['id']}: invalid options")
            val = sorted(set(val))
        elif q["type"] == "time":
            if not (isinstance(val, str) and len(val) == 5 and val[2] == ":"
                    and val[:2].isdigit() and val[3:].isdigit()
                    and int(val[:2]) < 24 and int(val[3:]) < 60):
                raise v.ValidationError(f"{q['id']}: time must look like 07:30")
        clean[q["id"]] = val
    return clean


def settings_from_answers(answers, settings):
    """Turn the chosen focus support options into app settings.
    Only switches features ON; users can change everything in Settings."""
    s = dict(settings)
    sup = set(answers.get("supports", []))
    if "short_blocks" in sup:
        s["block_timer"] = True
        s["block_min"] = min(s.get("block_min", 25), 15)
    if "calm_mode" in sup:
        s["calm_mode"] = True
    if "big_timer" in sup:
        s["big_timer"] = True
    if "nudges" in sup:
        s["nudges"] = True
    if "checkins" in sup:
        s["checkins"] = True
    if "if_then" in sup:
        s["if_then_prompt"] = True
    if answers.get("break_after") and "short_blocks" not in sup:
        s["block_min"] = max(10, min(50, int(answers["break_after"])))
    return s


def chronotype_hint(answers):
    """Mid-point style comparison of free-day vs school-day wake time (MCTQ idea).
    Returns 'evening', 'morning' or None. A soft hint only."""
    a, b = answers.get("wake_school"), answers.get("wake_free")
    if not (a and b):
        return None
    to_min = lambda t: int(t[:2]) * 60 + int(t[3:])  # noqa: E731
    diff = to_min(b) - to_min(a)
    if diff >= 120:
        return "evening"
    if diff <= 30:
        return "morning"
    return None
