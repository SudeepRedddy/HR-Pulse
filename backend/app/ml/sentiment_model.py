"""
HRPulse — Sentiment Analysis Model
Uses HuggingFace distilbert-base-uncased-finetuned-sst-2-english (pretrained).
No training needed — inference only.

Input: feedback_text string
Output: sentiment label (POSITIVE/NEGATIVE) + confidence score
"""

from typing import Dict, List, Optional

try:
    from transformers import pipeline as hf_pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# ── Model singleton ──────────────────────────
_sentiment_pipeline = None

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"


def _get_pipeline():
    """Lazy-load the sentiment analysis pipeline."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None and TRANSFORMERS_AVAILABLE:
        print("  [Sentiment] Loading DistilBERT model...")
        try:
            _sentiment_pipeline = hf_pipeline(
                "sentiment-analysis",
                model=MODEL_NAME,
                truncation=True,
                max_length=512,
            )
            print("  [Sentiment] Model loaded successfully")
        except Exception as e:
            print(f"  [Sentiment] Failed to load model: {e}")
            _sentiment_pipeline = None
    return _sentiment_pipeline


def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment of a single text.
    Returns: {label: str, score: float, normalized_label: str}
    """
    pipe = _get_pipeline()

    if pipe is None:
        # Mock fallback
        return _mock_sentiment(text)

    try:
        result = pipe(text[:512])[0]
        label = result["label"]  # POSITIVE or NEGATIVE
        score = round(result["score"], 4)

        # Normalize to positive/neutral/negative
        if label == "POSITIVE" and score >= 0.85:
            normalized = "positive"
        elif label == "NEGATIVE" and score >= 0.85:
            normalized = "negative"
        else:
            normalized = "neutral"

        # Convert score to 0-1 sentiment scale (0 = very negative, 1 = very positive)
        if label == "POSITIVE":
            sentiment_score = round(0.5 + score * 0.5, 4)
        else:
            sentiment_score = round(0.5 - score * 0.5, 4)

        return {
            "label": normalized,
            "score": sentiment_score,
            "confidence": score,
            "raw_label": label,
        }
    except Exception as e:
        return _mock_sentiment(text)


def analyze_batch(texts: List[str]) -> List[Dict]:
    """Analyze sentiment for a batch of texts."""
    pipe = _get_pipeline()

    if pipe is None:
        return [_mock_sentiment(t) for t in texts]

    try:
        results = pipe([t[:512] for t in texts], batch_size=32)
        output = []
        for result in results:
            label = result["label"]
            score = round(result["score"], 4)

            if label == "POSITIVE" and score >= 0.85:
                normalized = "positive"
            elif label == "NEGATIVE" and score >= 0.85:
                normalized = "negative"
            else:
                normalized = "neutral"

            if label == "POSITIVE":
                sentiment_score = round(0.5 + score * 0.5, 4)
            else:
                sentiment_score = round(0.5 - score * 0.5, 4)

            output.append({
                "label": normalized,
                "score": sentiment_score,
                "confidence": score,
                "raw_label": label,
            })
        return output
    except Exception:
        return [_mock_sentiment(t) for t in texts]


def _mock_sentiment(text: str) -> Dict:
    """Generate a plausible mock sentiment based on keyword analysis."""
    text_lower = text.lower()

    positive_words = ["enjoy", "great", "excellent", "proud", "supportive", "appreciate",
                      "motivated", "outstanding", "valuable", "happy", "love", "growth",
                      "flexibility", "innovative", "rewarding"]
    negative_words = ["overwhelmed", "frustrated", "poor", "disappointed", "unsupported",
                      "unreasonable", "low", "cut", "resentment", "micromanagement",
                      "confusion", "leaving", "undervalued"]

    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    if pos_count > neg_count:
        score = min(0.95, 0.65 + pos_count * 0.05)
        return {"label": "positive", "score": round(score, 4), "confidence": round(score, 4), "raw_label": "POSITIVE"}
    elif neg_count > pos_count:
        score = max(0.05, 0.35 - neg_count * 0.05)
        return {"label": "negative", "score": round(score, 4), "confidence": round(1 - score, 4), "raw_label": "NEGATIVE"}
    else:
        return {"label": "neutral", "score": 0.5, "confidence": 0.6, "raw_label": "NEUTRAL"}


def get_department_sentiment(feedbacks: List[Dict]) -> Dict[str, float]:
    """
    Calculate average sentiment score per department.
    Input: list of {department, sentiment_score} dicts
    Returns: {department_name: avg_score}
    """
    dept_scores = {}
    dept_counts = {}

    for fb in feedbacks:
        dept = fb.get("department", "Unknown")
        score = fb.get("sentiment_score", 0.5)
        dept_scores[dept] = dept_scores.get(dept, 0) + score
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    return {
        dept: round(dept_scores[dept] / dept_counts[dept], 4)
        for dept in dept_scores
    }
