from pathlib import Path
import ast
import tempfile

BASE = Path(__file__).resolve().parent
PY_FILES = [
    "app.py", "config.py", "sentiment_engine.py", "database.py",
    "exporters.py", "run_checks.py",
]

print("[1/6] Checking Python syntax...")
for name in PY_FILES:
    ast.parse((BASE / name).read_text(encoding="utf-8"), filename=name)
print("      PASS")

print("[2/6] Initializing sentiment engine...")
from sentiment_engine import SentimentEngine
engine = SentimentEngine()
print(f"      PASS ({engine.mode})")

print("[3/6] Checking positive/negative/neutral classification...")
tests = [
    ("I love this excellent product. It is fast and easy to use.", "Positive"),
    ("This is terrible, slow, confusing, and frustrating.", "Negative"),
    ("The meeting is scheduled for Tuesday at 10 AM.", "Neutral"),
]
for text, expected in tests:
    result = engine.analyze(text, "Balanced")
    assert result["label"] == expected, (text, result)
print("      PASS")

print("[4/6] Checking deterministic distribution calculation...")
rows = [engine.analyze(x, "Balanced", i) for i, (x, _) in enumerate(tests, 1)]
summary = engine.summarize_results(rows)
assert summary["total"] == 3
assert summary["positive_pct"] + summary["negative_pct"] + summary["neutral_pct"] == 100.0
print(f"      PASS ({summary['positive_pct']:.1f}% / {summary['negative_pct']:.1f}% / {summary['neutral_pct']:.1f}%)")

print("[5/6] Checking SQLite persistence...")
from database import SentimentDB
with tempfile.TemporaryDirectory() as td:
    db = SentimentDB(str(Path(td) / "test.db"))
    payload = {
        "title": "Test",
        "sensitivity": "Balanced",
        "items": rows,
        "summary": summary,
    }
    rid = db.save_analysis(payload)
    loaded = db.get_analysis(rid)
    assert loaded["summary"]["total"] == 3
    assert len(db.list_analyses()) == 1
print("      PASS")

print("[6/6] Checking export functions...")
from exporters import export_csv, export_json, export_markdown
payload = {"title": "Test", "sensitivity": "Balanced", "items": rows, "summary": summary}
assert "Positive" in export_csv(payload)
assert '"summary"' in export_json(payload)
assert "# Sentiment Analysis Report" in export_markdown(payload)
print("      PASS")

print("\nALL CHECKS PASSED")
