import re
from collections import Counter

from config import settings

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except Exception:
    SentimentIntensityAnalyzer = None

FALLBACK_LEXICON = {
    # Small transparent fallback for offline demonstration; not a substitute for VADER.
    "amazing": 3.0, "awesome": 3.0, "excellent": 3.0, "fantastic": 3.0,
    "great": 2.5, "good": 1.8, "love": 2.8, "loved": 2.8, "like": 1.5,
    "happy": 2.0, "helpful": 2.0, "easy": 1.4, "fast": 1.2, "perfect": 3.0,
    "best": 2.5, "enjoy": 2.0, "enjoyed": 2.0, "recommend": 2.2,
    "bad": -2.0, "poor": -2.0, "terrible": -3.0, "awful": -3.0,
    "hate": -2.8, "hated": -2.8, "slow": -1.3, "difficult": -1.5,
    "confusing": -1.4, "frustrating": -2.2, "frustrated": -2.2,
    "broken": -2.2, "worse": -2.0, "worst": -3.0, "disappointing": -2.3,
    "disappointed": -2.3, "problem": -1.3, "problems": -1.3, "bug": -1.7,
    "bugs": -1.7, "fail": -2.0, "failed": -2.0,
}

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

class SentimentEngine:
    def __init__(self):
        self._analyzer = None
        self.mode = "Fallback Lexicon"
        if SentimentIntensityAnalyzer is not None:
            try:
                self._analyzer = SentimentIntensityAnalyzer()
                self.mode = "NLTK VADER"
            except LookupError:
                # Try to download only the model resource, never the whole corpus package.
                try:
                    import nltk
                    nltk.download("vader_lexicon", quiet=True)
                    self._analyzer = SentimentIntensityAnalyzer()
                    self.mode = "NLTK VADER"
                except Exception:
                    self._analyzer = None
            except Exception:
                self._analyzer = None

    def scores(self, text: str):
        if self._analyzer is not None:
            return self._analyzer.polarity_scores(text)
        tokens = [t.lower() for t in TOKEN_RE.findall(text)]
        raw = sum(FALLBACK_LEXICON.get(t, 0.0) for t in tokens)
        neg = sum(1 for t in tokens if FALLBACK_LEXICON.get(t, 0) < 0)
        pos = sum(1 for t in tokens if FALLBACK_LEXICON.get(t, 0) > 0)
        scale = max(1.0, len(tokens) * 0.8)
        compound = max(-1.0, min(1.0, raw / scale))
        total_hits = pos + neg
        if total_hits:
            positive = pos / total_hits
            negative = neg / total_hits
        else:
            positive = negative = 0.0
        neutral = max(0.0, 1.0 - positive - negative)
        return {
            "neg": round(negative, 4),
            "neu": round(neutral, 4),
            "pos": round(positive, 4),
            "compound": round(compound, 4),
        }

    def analyze(self, text: str, sensitivity: str = "Balanced", row_id: int = 1):
        scores = self.scores(text)
        pos, neg = self.thresholds(sensitivity)
        compound = scores["compound"]
        if compound >= pos:
            label = "Positive"
        elif compound <= neg:
            label = "Negative"
        else:
            label = "Neutral"
        return {
            "id": row_id,
            "text": text,
            "label": label,
            "compound": scores["compound"],
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"],
        }

    def thresholds(self, sensitivity: str):
        if sensitivity == "Strict":
            return max(0.10, settings.positive_threshold), min(-0.10, settings.negative_threshold)
        if sensitivity == "Sensitive":
            return min(0.02, settings.positive_threshold), max(-0.02, settings.negative_threshold)
        return settings.positive_threshold, settings.negative_threshold

    def summarize_results(self, rows):
        total = len(rows)
        counts = Counter(row["label"] for row in rows)
        positive = counts.get("Positive", 0)
        negative = counts.get("Negative", 0)
        neutral = counts.get("Neutral", 0)
        positive_pct = round((positive / total * 100) if total else 0.0, 1)
        negative_pct = round((negative / total * 100) if total else 0.0, 1)
        # Make the displayed distribution sum to exactly 100.0 after rounding.
        neutral_pct = round(100.0 - positive_pct - negative_pct, 1) if total else 0.0
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_pct": positive_pct,
            "negative_pct": negative_pct,
            "neutral_pct": neutral_pct,
            "engine": self.mode,
        }
