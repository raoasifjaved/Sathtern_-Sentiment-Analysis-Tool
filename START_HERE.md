# START HERE — Sentio

## Part 1 — Setup
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Part 2 — Verify
```powershell
python run_checks.py
```
Expected ending:
`ALL CHECKS PASSED`

## Part 3 — Launch
```powershell
streamlit run app.py
```

## Part 4 — First safe test
Use **Multiple reviews** and enter:
```text
I love this product. It is excellent and easy to use.
The service was terrible and very frustrating.
The package arrived on Tuesday at 10 AM.
```

## Part 5 — Inspect
Open Results, Visualization, Metrics, and Export.

## Part 6 — CSV test
Create a CSV with a `text` column and upload it.

## Suggested assignment screenshots
1. Home UI
2. Reviews entered
3. Results with Positive/Negative/Neutral labels
4. Visualization chart
5. Transparent percentage calculations
6. Export controls
