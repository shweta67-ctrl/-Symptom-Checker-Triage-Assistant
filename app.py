"""
app.py
Streamlit front-end for the AI-Powered Symptom Checker & Triage Assistant.
Run with:  streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from symptom_engine import (
    analyse_symptoms,
    TRIAGE_COLOURS,
    TRIAGE_ICONS,
    urgency_colour,
)

# ---------------------------------------------------------------------------
# Page config (must be the very first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Symptom Checker & Triage Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load env
# ---------------------------------------------------------------------------

load_dotenv()

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []  # list of past checks in this session

# ---------------------------------------------------------------------------
# Sidebar — API key + about
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        placeholder="AIza...",
        help="Get your free key at https://aistudio.google.com/app/apikey",
    )

    st.markdown("---")
    st.markdown("### 🩺 About")
    st.info(
        "This tool uses **Gemini 3.6 Flash** to analyse your symptoms and "
        "recommend a triage level:\n\n"
        "🟢 **Self-Care** — manageable at home\n\n"
        "🟠 **See a Doctor** — needs professional review\n\n"
        "🔴 **Emergency** — seek immediate help\n\n"
        "---\n"
        "_This is not a substitute for professional medical advice._"
    )

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 📋 Session History")
        for i, h in enumerate(reversed(st.session_state.history), 1):
            level = h.get("triage_level", "N/A")
            icon = TRIAGE_ICONS.get(level, "⚪")
            snippet = h.get("_symptoms_snippet", "—")
            st.markdown(f"**{i}.** {icon} {level}  \n_{snippet}_")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🩺 AI Symptom Checker & Triage Assistant")
st.caption(
    "Powered by **Gemini 3.6 Flash** · Enter your symptoms below and receive "
    "an instant AI-driven triage recommendation."
)
st.divider()

# ---------------------------------------------------------------------------
# Disclaimer banner
# ---------------------------------------------------------------------------

st.warning(
    "⚠️ **Medical Disclaimer** — This application provides AI-generated "
    "informational guidance only. It does **not** constitute medical advice, "
    "diagnosis, or treatment. Always consult a qualified healthcare provider. "
    "In a life-threatening emergency, **call 911 (or your local emergency number) immediately**.",
    icon="⚠️",
)

st.divider()

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------

st.subheader("📝 Patient Information")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    symptoms = st.text_area(
        "Describe your symptoms *",
        height=130,
        placeholder=(
            "e.g. I have a severe headache that started this morning, "
            "accompanied by nausea and sensitivity to light..."
        ),
        help="Be as specific as possible — location, character, triggers, etc.",
    )

with col2:
    age = st.text_input(
        "Age",
        placeholder="e.g. 34",
        help="Your age in years (optional but improves accuracy)",
    )
    sex = st.selectbox(
        "Biological Sex",
        options=["Not specified", "Male", "Female", "Other"],
    )
    duration = st.text_input(
        "Symptom Duration",
        placeholder="e.g. 2 days, 3 hours",
        help="How long you have been experiencing these symptoms",
    )

with col3:
    severity = st.slider(
        "Self-Reported Severity",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = barely noticeable · 10 = worst imaginable",
    )
    st.caption(f"Selected severity: **{severity}/10**")

    history = st.text_input(
        "Medical History / Chronic Conditions",
        placeholder="e.g. diabetes, hypertension",
    )
    medications = st.text_input(
        "Current Medications",
        placeholder="e.g. metformin 500 mg, aspirin",
    )

notes = st.text_area(
    "Additional Notes (optional)",
    height=70,
    placeholder="Any recent travel, known allergies, recent injuries, etc.",
)

st.divider()

# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------

run_col, clear_col, _ = st.columns([2, 1, 4])

with run_col:
    analyse_btn = st.button(
        "🔍 Analyse Symptoms",
        type="primary",
        use_container_width=True,
        disabled=not api_key_input,
    )

with clear_col:
    if st.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.result = None
        st.rerun()

if not api_key_input:
    st.info("👈 Please enter your **Gemini API Key** in the sidebar to begin.")

# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------

if analyse_btn:
    if not symptoms.strip():
        st.error("Please describe your symptoms before analysing.")
    else:
        with st.spinner("🤖 Consulting Gemini 3.6 Flash…  This may take a few seconds."):
            result = analyse_symptoms(
                api_key=api_key_input,
                symptoms=symptoms.strip(),
                age=age.strip() or "Not specified",
                sex=sex,
                duration=duration.strip() or "Not specified",
                severity=severity,
                history=history.strip() or "None",
                medications=medications.strip() or "None",
                notes=notes.strip() or "None",
            )

        if "error" in result:
            st.error(f"❌ Error from AI engine: {result['error']}")
            if "raw_response" in result:
                with st.expander("Raw AI response"):
                    st.code(result["raw_response"])
        else:
            result["_symptoms_snippet"] = symptoms[:60] + ("…" if len(symptoms) > 60 else "")
            st.session_state.result = result
            st.session_state.history.append(result)

# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------

if st.session_state.result:
    res = st.session_state.result
    level = res.get("triage_level", "Unknown")
    score = res.get("urgency_score", 0)
    icon = TRIAGE_ICONS.get(level, "⚪")
    colour = TRIAGE_COLOURS.get(level, "#555")
    u_colour = urgency_colour(score)

    st.divider()
    st.subheader("📊 Triage Assessment")

    # ── Top-level metric row ──────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric(
        label="Triage Level",
        value=f"{icon} {level}",
    )
    m2.metric(
        label="Urgency Score",
        value=f"{score} / 10",
        delta=None,
    )
    conditions_count = len(res.get("possible_conditions", []))
    m3.metric(
        label="Possible Conditions Identified",
        value=conditions_count,
    )

    # ── Triage level coloured banner ──────────────────────────────────────
    triage_messages = {
        "Self-Care": (
            "🟢 **Self-Care Recommended** — Your symptoms appear manageable at home. "
            "Monitor your condition and follow the self-care tips below."
        ),
        "See a Doctor": (
            "🟠 **See a Doctor** — Your symptoms warrant a professional medical evaluation. "
            "Schedule an appointment or visit an urgent-care clinic."
        ),
        "Emergency": (
            "🔴 **EMERGENCY — Seek Immediate Help** — Your symptoms may indicate a "
            "serious or life-threatening condition. **Call 911 or go to the nearest "
            "emergency room immediately.**"
        ),
    }

    banner_fn = {
        "Self-Care": st.success,
        "See a Doctor": st.warning,
        "Emergency": st.error,
    }.get(level, st.info)

    banner_fn(triage_messages.get(level, f"{icon} {level}"))

    # ── Summary ───────────────────────────────────────────────────────────
    st.markdown("#### 🧠 AI Summary")
    st.info(res.get("summary", "No summary provided."))

    # ── Urgency score bar ─────────────────────────────────────────────────
    st.markdown("#### 📈 Urgency Score")
    st.progress(score / 10, text=f"Urgency: {score}/10")

    st.divider()

    # ── Two-column layout for conditions + red flags ──────────────────────
    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### 🔬 Possible Conditions")
        conditions = res.get("possible_conditions", [])
        if conditions:
            for cond in conditions:
                likelihood = cond.get("likelihood", "Unknown")
                badge = {"Low": "🔵 Low", "Moderate": "🟡 Moderate", "High": "🔴 High"}.get(
                    likelihood, f"⚪ {likelihood}"
                )
                with st.expander(f"**{cond.get('name', 'Unknown')}** — {badge}"):
                    st.markdown(cond.get("description", "No description."))
        else:
            st.markdown("_No specific conditions identified._")

    with right:
        st.markdown("#### 🚨 Red Flags to Watch For")
        red_flags = res.get("red_flags", [])
        if red_flags:
            for flag in red_flags:
                st.error(f"⚠️ {flag}")
        else:
            st.success("No critical red flags identified.")

    st.divider()

    # ── Self-care tips ────────────────────────────────────────────────────
    st.markdown("#### 💊 Self-Care Tips")
    tips = res.get("self_care_tips", [])
    if tips:
        tip_cols = st.columns(min(len(tips), 3))
        for i, tip in enumerate(tips):
            tip_cols[i % len(tip_cols)].success(f"✅ {tip}")
    else:
        st.markdown("_No specific self-care tips provided._")

    st.divider()

    # ── When to escalate ─────────────────────────────────────────────────
    st.markdown("#### 📞 When to Escalate Care")
    st.warning(f"⬆️ {res.get('when_to_escalate', 'Consult a doctor if symptoms worsen.')}")

    # ── Disclaimer ────────────────────────────────────────────────────────
    st.divider()
    st.caption(f"📋 {res.get('disclaimer', '')}")

    # ── Export ────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 💾 Export Report")

    import json as _json
    export_clean = {k: v for k, v in res.items() if not k.startswith("_")}
    st.download_button(
        label="⬇️ Download JSON Report",
        data=_json.dumps(export_clean, indent=2),
        file_name="triage_report.json",
        mime="application/json",
        use_container_width=False,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "🩺 AI Symptom Checker & Triage Assistant · Powered by Gemini 3.6 Flash · "
    "Not a substitute for professional medical advice."
)
