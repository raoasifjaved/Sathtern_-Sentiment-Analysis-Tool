# Sentio — Sentiment Analysis Studio

An educational Python + Streamlit sentiment analysis application for Task 4.

## Requirements covered
- Analyze user reviews or comments
- Display results clearly
- Use Python and NLP libraries
- Detect Positive, Negative, or Neutral sentiment
- Visualize results

## Features
- Single review, multi-review, or CSV input
- NLTK VADER sentiment analysis when the lexicon is available
- Small transparent offline fallback lexicon if the VADER resource cannot be loaded
- Positive/negative/neutral classification using configurable compound-score thresholds
- Bar-chart visualization and percentage distribution
- SQLite analysis history
- CSV, JSON, and Markdown export
- Deterministic metrics for reproducibility

## Run on Windows
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run_checks.py
streamlit run app.py
```

## CSV format
```csv
text
"The product is easy to use and very helpful."
"The application is slow and frustrating."
"The meeting starts at 10 AM."
```

## Accuracy notes
The sentiment label is derived from the compound score. It is not a ground-truth measurement of a person's internal emotional state.

The dashboard calculates dataset percentages locally:
`count / total × 100`

Review sarcasm, mixed sentiment, negation, domain-specific terms, and ambiguous cases manually.

## Responsible use
Do not use automated sentiment labels as the sole basis for employment, admissions, lending, disciplinary decisions, or other high-impact decisions about people.
