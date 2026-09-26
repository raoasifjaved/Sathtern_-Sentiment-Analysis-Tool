import json
import pandas as pd

def export_csv(result):
    return pd.DataFrame(result["items"]).to_csv(index=False)

def export_json(result):
    return json.dumps(result, indent=2, ensure_ascii=False)

def export_markdown(result):
    s = result["summary"]
    lines = [
        f"# Sentiment Analysis Report — {result['title']}",
        "",
        f"- Engine: {s['engine']}",
        f"- Sensitivity: {result['sensitivity']}",
        f"- Total items: {s['total']}",
        f"- Positive: {s['positive']} ({s['positive_pct']:.1f}%)",
        f"- Negative: {s['negative']} ({s['negative_pct']:.1f}%)",
        f"- Neutral: {s['neutral']} ({s['neutral_pct']:.1f}%)",
        "",
        "## Results",
    ]
    for row in result["items"]:
        lines.append(
            f"- #{row['id']} — **{row['label']}** — compound={row['compound']:.4f} — {row['text']}"
        )
    lines += [
        "",
        "## Note",
        "Sentiment labels are automated linguistic estimates. Review important or ambiguous examples manually.",
    ]
    return "\n".join(lines)
