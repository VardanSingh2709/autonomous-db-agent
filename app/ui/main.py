import streamlit as st
import sys, os, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.agents.investigator import investigate, QUESTIONS

st.set_page_config(page_title="Autonomous Database Investigation Agent", layout="wide")

st.title("🔍 Autonomous Database Investigation Agent")
st.caption(
    "Ask a business question. The agent inspects the database schema, writes and "
    "runs its own SQL, tests hypotheses, and verifies its conclusion against the "
    "database independently before answering."
)

# --- Question selection ---
scenario_key = st.selectbox(
    "Choose a sample question",
    options=list(QUESTIONS.keys()),
    format_func=lambda k: QUESTIONS[k],
)

run_clicked = st.button("Run Investigation", type="primary")

# --- Run the investigation (blocking) and store the result ---
if run_clicked:
    with st.spinner("Investigating... this involves several real LLM calls and may take up to a minute."):
        start = time.time()
        answer, trace = investigate(QUESTIONS[scenario_key], scenario_key)
        elapsed = time.time() - start

    st.session_state["last_result"] = {
        "scenario_key": scenario_key,
        "question": QUESTIONS[scenario_key],
        "answer": answer,
        "trace": trace,
        "elapsed": elapsed,
    }

# --- Display the most recent result, if one exists ---
result = st.session_state.get("last_result")

if result and result["scenario_key"] == scenario_key:
    st.divider()

    # --- Investigation trace ---
    st.subheader("Agent Investigation")
    query_count = 0
    for entry in result["trace"]:
        if entry["tool"] == "inspect_schema":
            st.markdown("✅ Inspected database schema")
        elif entry["tool"] == "execute_readonly_sql":
            query_count += 1
            label = f"✅ Query {query_count}"
            with st.expander(label):
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

    # --- Final answer ---
    st.divider()
    st.subheader("Final Answer")
    if "summary" in result["answer"]:
        st.success(result["answer"]["summary"])
    with st.expander("Full structured answer"):
        st.json(result["answer"])

    # --- Investigation metrics (all real, never fabricated) ---
    st.divider()
    st.subheader("Investigation Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Steps", len(result["trace"]))
    col2.metric("Queries executed", query_count)
    last_verification = next(
        (e["verification"] for e in reversed(result["trace"]) if "verification" in e), None
    )
    verified_label = "Yes" if last_verification and last_verification.get("verified") else "No"
    col3.metric("Answer verified", verified_label)
    col4.metric("Time elapsed", f"{result['elapsed']:.1f}s")

elif result is None:
    st.info("Pick a question above and click **Run Investigation** to see the agent in action.")