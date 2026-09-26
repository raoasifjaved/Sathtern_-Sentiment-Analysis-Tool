import io
import re
import pandas as pd
import streamlit as st

from config import settings
from sentiment_engine import SentimentEngine
from database import SentimentDB
from exporters import export_csv, export_json, export_markdown

st.set_page_config(
    page_title="Sentio — Sentiment Analysis Studio",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.hero {
    padding: 1.4rem 1.5rem;
    border: 1px solid rgba(127,127,127,.18);
    border-radius: 20px;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, rgba(79,70,229,.12), rgba(14,165,233,.10));
}
.note {
    padding: .8rem 1rem;
    border: 1px solid rgba(127,127,127,.18);
    border-radius: 12px;
    background: rgba(127,127,127,.05);
}
</style>
""", unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None

engine = SentimentEngine()
db = SentimentDB(settings.database_path)

with st.sidebar:
    st.title("💬 Sentio")
    st.caption("Sentiment analysis learning workspace")

    st.divider()
    st.subheader("Analysis setup")
    mode = st.radio(
        "Input mode",
        ["Single review", "Multiple reviews", "CSV file"],
        index=0,
    )
    sensitivity = st.select_slider(
        "Decision sensitivity",
        options=["Strict", "Balanced", "Sensitive"],
        value="Balanced",
        help="Controls the threshold used to classify VADER compound scores."
    )
    st.divider()
    st.info("Sentiment is an automated linguistic estimate, not a definitive statement about a person's emotions or intent.")
    st.divider()
    st.subheader("Recent analyses")
    for item in db.list_analyses(limit=8):
        label = f"{item['title']} · {item['items']} items"
        if st.button(label[:42], key=f"analysis_{item['id']}"):
            saved = db.get_analysis(item['id'])
            if saved:
                st.session_state.result = saved
                st.rerun()

st.markdown("""
<div class="hero">
<h1>💬 Sentio — Sentiment Analysis Studio</h1>
<p>Analyze reviews and comments, classify sentiment as positive, negative, or neutral,
and visualize the distribution with transparent, reproducible metrics.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("1. Provide Reviews or Comments")

rows = []
if mode == "Single review":
    title = st.text_input("Analysis title", placeholder="e.g. Product Feedback — September")
    text = st.text_area(
        "Review / comment",
        height=240,
        placeholder="Example: The app is easy to use and the search feature is fast, but the notification system is confusing.",
    )
    if text.strip():
        rows = [{"id": 1, "text": text.strip()}]

elif mode == "Multiple reviews":
    title = st.text_input("Analysis title", placeholder="e.g. Customer Reviews Batch 01")
    text = st.text_area(
        "Enter one review/comment per line",
        height=300,
        placeholder="Great product and very easy to use.\nThe service was slow and frustrating.\nThe delivery arrived on Tuesday.",
    )
    rows = [{"id": i, "text": line.strip()} for i, line in enumerate(text.splitlines(), start=1) if line.strip()]

else:
    title = st.text_input("Analysis title", placeholder="e.g. Uploaded Customer Reviews")
    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        help="The CSV must contain a column called 'text'. A 'review' or 'comment' column is also accepted.",
    )
    if uploaded:
        try:
            df = pd.read_csv(io.BytesIO(uploaded.getvalue()))
            lower_map = {str(c).lower().strip(): c for c in df.columns}
            source_col = lower_map.get("text") or lower_map.get("review") or lower_map.get("comment")
            if not source_col:
                st.error("CSV needs a 'text' column (or 'review'/'comment').")
            else:
                rows = [
                    {"id": i, "text": str(value).strip()}
                    for i, value in enumerate(df[source_col].fillna(""), start=1)
                    if str(value).strip()
                ]
                st.success(f"Loaded {len(rows)} text entries from {uploaded.name}.")
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not read the CSV: {exc}")

col_a, col_b = st.columns([2, 1])
with col_a:
    st.caption("For batch analysis, keep each review/comment as a separate row or line so the results remain traceable.")
with col_b:
    st.metric("Items ready", len(rows))

analyze = st.button("🔎 Analyze Sentiment", type="primary", use_container_width=True)

if analyze:
    if not rows:
        st.error("Please provide at least one review/comment.")
    elif len(rows) > settings.max_items:
        st.error(f"Please analyze at most {settings.max_items} items at a time.")
    else:
        result_rows = []
        for row in rows:
            result_rows.append(engine.analyze(row["text"], sensitivity=sensitivity, row_id=row["id"]))

        summary = engine.summarize_results(result_rows)
        result = {
            "title": title.strip() or "Untitled Sentiment Analysis",
            "sensitivity": sensitivity,
            "items": result_rows,
            "summary": summary,
        }
        result["id"] = db.save_analysis(result)
        st.session_state.result = result
        st.success("Sentiment analysis completed and saved.")

if st.session_state.result:
    result = st.session_state.result
    summary = result["summary"]
    items = result["items"]

    st.divider()
    st.subheader("2. Sentiment Results")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total items", summary["total"])
    c2.metric("Positive", summary["positive"])
    c3.metric("Negative", summary["negative"])
    c4.metric("Neutral", summary["neutral"])

    t1, t2, t3, t4 = st.tabs(["📋 Results", "📊 Visualization", "🧮 Metrics", "📦 Export"])

    with t1:
        df = pd.DataFrame(items)
        st.dataframe(
            df[["id", "text", "label", "compound", "positive", "negative", "neutral"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Scores are model outputs. The labels are generated from deterministic thresholds applied to the compound score.")

    with t2:
        chart_df = pd.DataFrame({
            "Sentiment": ["Positive", "Negative", "Neutral"],
            "Count": [summary["positive"], summary["negative"], summary["neutral"]],
        })
        st.bar_chart(chart_df.set_index("Sentiment"))

        st.markdown("### Percentage distribution")
        pct_df = pd.DataFrame({
            "Sentiment": ["Positive", "Negative", "Neutral"],
            "Percentage": [summary["positive_pct"], summary["negative_pct"], summary["neutral_pct"]],
        })
        st.dataframe(pct_df, use_container_width=True, hide_index=True)

    with t3:
        st.markdown("### Transparent classification rule")
        st.code(
            "compound >= positive_threshold  → Positive\n"
            "compound <= negative_threshold  → Negative\n"
            "otherwise                      → Neutral",
            language="text",
        )
        st.write(
            f"Balanced thresholds used in this run: `{settings.positive_threshold}` and `{settings.negative_threshold}`."
        )
        st.markdown("### Distribution calculation")
        st.write(f"Positive: `{summary['positive']} / {summary['total']} × 100 = {summary['positive_pct']:.1f}%`")
        st.write(f"Negative: `{summary['negative']} / {summary['total']} × 100 = {summary['negative_pct']:.1f}%`")
        st.write(f"Neutral: `{summary['neutral']} / {summary['total']} × 100 = {summary['neutral_pct']:.1f}%`")
        st.warning("Percentages describe this analyzed dataset only. They are not a population-level opinion estimate.")

    with t4:
        st.download_button(
            "⬇ CSV results",
            export_csv(result),
            file_name="sentiment_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "⬇ JSON analysis",
            export_json(result),
            file_name="sentiment_analysis.json",
            mime="application/json",
            use_container_width=True,
        )
        st.download_button(
            "⬇ Markdown report",
            export_markdown(result),
            file_name="sentiment_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.divider()
    st.subheader("3. Interpretation Notes")
    st.markdown(
        '<div class="note"><b>Important:</b> Sentiment analysis can miss sarcasm, context, mixed emotions, domain-specific language, and cultural nuances. Use the label as an automated signal and review important examples manually.</div>',
        unsafe_allow_html=True,
    )
