"""
classifier.py — Hybrid NRCLex + TextBlob Emotion Engine
=========================================================
Classifies email body text into one of four categories:
  Happy | Normal | Sad | Angry

Design principles
-----------------
* Subjectivity gate: automated / transactional emails score low on
  TextBlob subjectivity.  We default them to Normal before even
  consulting NRCLex, because functional language ("click here",
  "your account", "2-step verification") carries no personal emotion.

* Frequency threshold: NRCLex emotion must represent at least
  MIN_EMOTION_FREQ of the analysed tokens to be considered dominant.
  Without this gate a single fear-adjacent word ("locked") in a
  100-word security alert would dominate.

* Fear ≠ Sad by default: security alerts, password resets and
  notifications legitimately contain fear-adjacent words.  We only
  escalate fear → Sad when polarity also confirms negativity.

* Polarity-only fallbacks use tighter bands and require non-trivial
  subjectivity, so purely objective negative statements ("0 items
  found") don't bleed into Sad/Angry.
"""

import re
from textblob import TextBlob
from nrclex import NRCLex

# Load the lexicon once at module import time (NRCLex 4.x API).
_nrc = NRCLex()

MIN_EMOTION_FREQ = 0.13
MIN_SUBJECTIVITY = 0.12

# Domain cues for high-precision email triage
ANGRY_SIGNALS = [
    r'\bunacceptable\b', r'\bterrible\b', r'\bhorrible\b', r'\bfurious\b',
    r'\boutraged?\b', r'\bdisgusted?\b', r'\bhow dare\b', r'\bridiculous\b',
    r'\bdemand\b', r'\bruined\b', r'\bworst\b', r'\blawsuit\b', r'\bincompetent\b',
    r'\bpissed\b', r'\bangry\b', r'\bfrustrated?\b', r'\brefund\b', r'\bcomplaint\b',
    r'\bunprofessional\b', r'\bpathetic\b', r'\bshameful\b', r'\bcheat(ed|ing)?\b',
    r'\bscam\b', r'\bappalled\b', r'\bgrossly\b', r'\bunresolved\b', r'\bdisappointed\b',
    r'\bworst service\b', r'\bcancel my subscription\b', r'\bchargeback\b'
]

SAD_SIGNALS = [
    r'\bcondolences?\b', r'\bheartbroken\b', r'\bpassed away\b', r'\bloss of\b',
    r'\bmourning\b', r'\bgrief\b', r'\bdevastat(ed|ing)\b', r'\brest in peace\b',
    r'\brip\b', r'\bmiss you\b', r'\bsad to hear\b', r'\bdeeply saddened\b',
    r'\bheartache\b', r'\bsorrow\b', r'\bcrying\b', r'\bdepressed\b',
    r'\blonely\b', r'\bempty\b', r'\bunfortunate news\b', r'\bsaddest\b',
    r'\bregret to inform\b', r'\bgrieving\b'
]

HAPPY_SIGNALS = [
    r'\bcongratulat(ions|e)\b', r'\bcongrats\b', r'\bwonderful\b', r'\bfantastic\b',
    r'\bgreat news\b', r'\bthrilled\b', r'\bdelighted\b', r'\bcelebrat(e|ing|ion)\b',
    r'\bawesome\b', r'\bpleased to announce\b', r'\bthank you so much\b',
    r'\bloved\b', r'\bamazing\b', r'\bexcited\b', r'\bjoyful\b', r'\bcheers\b',
    r'\bgreat weekend\b', r'\bhave a great\b'
]

TRANSACTIONAL_SIGNALS = [
    r'\bverification code\b', r'\bsecurity alert\b', r'\b2-step verification\b',
    r'\bpassword reset\b', r'\border confirmation\b', r'\btracking number\b',
    r'\bmeeting minutes\b', r'\binvoice\b', r'\bstatement\b', r'\bterms of service\b',
    r'\bprivacy policy\b', r'\bunsubscribe\b', r'\bno-reply\b', r'\bdonotreply\b',
    r'\bautomated message\b', r'\breceipt\b', r'\bscheduled maintenance\b',
    r'\bdowntime\b', r'\bcan you send me\b'
]

_META_EMOTIONS = frozenset({"positive", "negative", "anticipation", "trust", "surprise"})


def _score_patterns(text: str, patterns: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for p in patterns if re.search(p, text_lower))


def classify_emotion(body_text: str) -> tuple[str, float, float]:
    """
    Return (label, polarity, subjectivity) for the given text.

    label ∈ {"Happy", "Normal", "Sad", "Angry"}
    polarity    ∈ [-1.0, 1.0]   (TextBlob sentence polarity)
    subjectivity ∈ [0.0, 1.0]   (0 = objective, 1 = subjective)
    """
    snippet = body_text[:5000]

    # ── TextBlob Sentiment ────────────────────────────────────────────
    blob       = TextBlob(snippet)
    polarity   = blob.sentiment.polarity
    subj       = blob.sentiment.subjectivity

    # ── Domain Pattern Matches ─────────────────────────────────────────
    angry_cues = _score_patterns(snippet, ANGRY_SIGNALS)
    sad_cues   = _score_patterns(snippet, SAD_SIGNALS)
    happy_cues = _score_patterns(snippet, HAPPY_SIGNALS)
    trans_cues = _score_patterns(snippet, TRANSACTIONAL_SIGNALS)

    # ── NRCLex Emotion Frequencies ────────────────────────────────────
    _nrc.load_raw_text(snippet)
    freq      = _nrc.affect_frequencies
    core_freq = {k: v for k, v in freq.items() if k not in _META_EMOTIONS}
    dominant  = max(core_freq, key=core_freq.get) if core_freq else None
    dom_val   = core_freq.get(dominant, 0.0) if dominant else 0.0

    sad_val        = core_freq.get("sadness", 0.0)
    anger_val      = core_freq.get("anger",   0.0)
    disgust_val    = core_freq.get("disgust", 0.0)
    anger_combined = anger_val + disgust_val

    # ── 1. TRANSACTIONAL FILTER ────────────────────────────────────────
    if trans_cues > 0 and angry_cues == 0 and sad_cues == 0 and happy_cues == 0:
        return "Normal", polarity, subj

    # ── 2. HIGH-PRECISION CUES ────────────────────────────────────────
    # Angry cues (e.g. unacceptable, terrible, how dare, refund, complaint)
    if angry_cues > 0 and sad_cues == 0:
        return "Angry", polarity, subj

    # Sad cues (e.g. heartbroken, passed away, condolences, mourning, miss you)
    if sad_cues > 0 and sad_cues >= angry_cues:
        return "Sad", polarity, subj

    # Happy cues (e.g. congratulations, fantastic, celebrate, thrilled)
    if happy_cues > 0 and happy_cues > angry_cues and happy_cues > sad_cues:
        return "Happy", polarity, subj

    # ── 3. LOW SUBJECTIVITY GATE ───────────────────────────────────────
    # If no explicit emotional cues matched and subjectivity is near zero, it is transactional/neutral
    if subj < MIN_SUBJECTIVITY and angry_cues == 0 and sad_cues == 0 and happy_cues == 0:
        return "Normal", polarity, subj

    # ── 4. ANGRY EMOTION ENGINE ───────────────────────────────────────
    if anger_combined >= MIN_EMOTION_FREQ and anger_combined >= sad_val:
        return "Angry", polarity, subj
    if dominant in ("anger", "disgust") and dom_val >= MIN_EMOTION_FREQ:
        return "Angry", polarity, subj
    if polarity < -0.45 and subj > 0.30 and sad_val < 0.20:
        return "Angry", polarity, subj

    # ── 5. HAPPY EMOTION ENGINE ───────────────────────────────────────
    if dominant == "joy" and dom_val >= MIN_EMOTION_FREQ:
        return "Happy", polarity, subj
    if polarity > 0.35 and subj > 0.15 and freq.get("positive", 0.0) > freq.get("negative", 0.0):
        return "Happy", polarity, subj

    # ── 6. SAD EMOTION ENGINE ─────────────────────────────────────────
    if dominant == "sadness" and dom_val >= MIN_EMOTION_FREQ:
        return "Sad", polarity, subj
    if dominant == "fear" and dom_val >= MIN_EMOTION_FREQ and polarity < -0.18:
        return "Sad", polarity, subj
    if polarity < -0.25 and subj > 0.25:
        return "Sad", polarity, subj

    # ── DEFAULT ───────────────────────────────────────────────────────
    return "Normal", polarity, subj
