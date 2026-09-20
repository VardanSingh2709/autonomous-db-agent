import streamlit as st
import sys, os, time
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.agents.investigator import investigate, investigate_general, QUESTIONS

st.set_page_config(page_title="Autonomous Database Investigation Agent", layout="wide")

st.title("🔍 Autonomous Database Investigation Agent")
st.markdown(
    """
    This agent doesn't just write one SQL query and answer — it **inspects the database schema,
    tests multiple hypotheses across regions/products/channels/time, and independently verifies
    its own conclusion against the database** before responding.

    Pick a question below and click **Run Investigation** to watch it work.
    """
)

# --- Curated general questions, for variety beyond the 5 root-cause scenarios ---
GENERAL_QUESTIONS = {
    "How many customers do we have?": "simple",
    "What is our total revenue across all time?": "aggregation",
    "Which product category generates the most total revenue?": "joins",
    "How did total order count change from Q2 to Q3 2024?": "time_comparison",
}

tab1, tab2 = st.tabs(["🕵️ Root-Cause Investigations", "⚡ Quick Questions"])

# ===================== TAB 1: Root-cause investigations =====================
with tab1:
    scenario_key = st.selectbox(
        "Choose a business question",
        options=list(QUESTIONS.keys()),
        format_func=lambda k: QUESTIONS[k],
        key="scenario_select",
    )
    run_clicked = st.button("Run Investigation", type="primary", key="run_scenario")

    if run_clicked:
        progress_placeholder = st.empty()
        def update_progress(msg):
            progress_placeholder.info(msg)

        start = time.time()
        answer, trace = investigate(QUESTIONS[scenario_key], scenario_key, on_step=update_progress)
        elapsed = time.time() - start
        progress_placeholder.empty()

        st.session_state["last_result"] = {
            "scenario_key": scenario_key, "question": QUESTIONS[scenario_key],
            "answer": answer, "trace": trace, "elapsed": elapsed,
        }

    result = st.session_state.get("last_result")
    if result and result["scenario_key"] == scenario_key:
        st.divider()
        st.subheader("Agent Investigation")
        query_count = 0
        for entry in result["trace"]:
            if entry["tool"] == "inspect_schema":
                st.markdown("✅ Inspected database schema")
            elif entry["tool"] == "execute_readonly_sql":
                query_count += 1
                with st.expander(f"✅ Query {query_count}"):
                    st.code(entry["args"]["query"], language="sql")
                    st.write("Result:")
                    st.json(entry["result"])
            elif entry["tool"] == "submit_final_answer":
                verified = entry["verification"]["verified"]
                icon = "✅" if verified else "⚠️"
                label = "Submitted answer — verified" if verified else "Submitted answer — rejected, retrying"
                with st.expander(f"{icon} {label}"):
                    st.json(entry["args"])
                    st.write("Verification result:")
                    st.json(entry["verification"])

        st.divider()
        st.subheader("Final Answer")
        answer = result["answer"]
        if "summary" in answer:
            st.success(answer["summary"])

        # --- Chart: Q2 vs Q3 for whichever dimension this scenario identified ---
        chart_pairs = [
            ("root_cause_q2_revenue", "root_cause_q3_revenue", "Revenue ($)"),
            ("root_cause_q2_churn_pct", "root_cause_q3_churn_pct", "Churn Rate (%)"),
            ("root_cause_q2_orders", "root_cause_q3_orders", "Orders"),
            ("root_cause_q2_avg_orders", "root_cause_q3_avg_orders", "Avg Orders/Customer"),
            ("q2_avg_order_value", "q3_avg_order_value", "Avg Order Value ($)"),
        ]
        for q2_key, q3_key, label in chart_pairs:
            if q2_key in answer and q3_key in answer:
                fig = go.Figure(data=[
                    go.Bar(x=["Q2 2024", "Q3 2024"], y=[answer[q2_key], answer[q3_key]],
                           marker_color=["#4C78A8", "#E45756"])
                ])
                fig.update_layout(title=label, yaxis_title=label, height=350)
                st.plotly_chart(fig, use_container_width=True)
                break

        with st.expander("Full structured answer"):
            st.json(answer)

        st.divider()
        st.subheader("Investigation Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Steps", len(result["trace"]))
        col2.metric("Queries executed", query_count)
        last_verification = next((e["verification"] for e in reversed(result["trace"]) if "verification" in e), None)
        col3.metric("Answer verified", "Yes" if last_verification and last_verification.get("verified") else "No")
        col4.metric("Time elapsed", f"{result['elapsed']:.1f}s")
    elif result is None:
        st.info("Pick a question above and click **Run Investigation** to see the agent in action.")

# ===================== TAB 2: Quick general questions =====================
with tab2:
    st.caption("Simpler lookups the agent also handles — no multi-step investigation needed.")
    question_text = st.selectbox("Choose a question", options=list(GENERAL_QUESTIONS.keys()), key="general_select")
    run_general = st.button("Run", type="primary", key="run_general")

    if run_general:
        with st.spinner("Thinking..."):
            start = time.time()
            answer, trace = investigate_general(question_text)
            elapsed = time.time() - start
        st.session_state["general_result"] = {"question": question_text, "answer": answer, "trace": trace, "elapsed": elapsed}

    gresult = st.session_state.get("general_result")
    if gresult and gresult["question"] == question_text:
        st.divider()
        st.success(f"**Answer:** {gresult['answer'].get('answer', 'N/A')}")
        st.caption(gresult["answer"].get("explanation", ""))
        col1, col2 = st.columns(2)
        col1.metric("Steps", len(gresult["trace"]))
        col2.metric("Time elapsed", f"{gresult['elapsed']:.1f}s")

# ===================== Permanent evaluation results section =====================
st.divider()
st.header("📊 Evaluation Results (Measured, Not Estimated)")
st.markdown(
    """
    A 51-question benchmark was run against both this agentic system and a simple
    one-shot Text-to-SQL baseline (one query, no verification, no tools).
    """
)
st.table({
    "Category": ["Simple", "Aggregation", "Joins", "Time comparison", "Root-cause / multi-step"],
    "Baseline (1 query)": ["100%", "100%", "100%", "83%", "0%"],
    "This Agentic System": ["100%", "100%", "100%", "100%", "100%"],
})
st.caption(
    "Agentic architecture shows no measurable advantage on simple lookups — a one-shot query "
    "performs equally well. The gap is entirely, and dramatically, on multi-step root-cause "
    "questions, where independent verification is the difference between 0% and 100% accuracy."
)