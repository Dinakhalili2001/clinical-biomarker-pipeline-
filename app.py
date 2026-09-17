"""
Clinical Biomarker & Remote Monitoring Dashboard
====================================================
Interactive Streamlit app combining the ELISA NETs/cfDNA pipeline and
the wearable vitals dashboard into one web app.

Run with:
    streamlit run app.py
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Allow importing our existing pipeline modules
sys.path.append(os.path.join(os.path.dirname(__file__), "elisa_pipeline"))
sys.path.append(os.path.join(os.path.dirname(__file__), "wearable_dashboard"))

from nets_elisa_pipeline import run_pipeline, summarize_pre_post
from wearable_dashboard import generate_wearable_data, flag_elevated_heart_rate

st.set_page_config(page_title="Biomarker & Monitoring Dashboard", layout="wide")

st.title("Clinical Biomarker & Remote Monitoring Dashboard")
st.caption("ELISA NETs/cfDNA analysis + wearable vitals monitoring, built with Python + Streamlit")

tab1, tab2 = st.tabs(["🧪 ELISA NETs/cfDNA Pipeline", "⌚ Wearable Vitals Dashboard"])

# ---------------------------------------------------------------------
# TAB 1: ELISA pipeline
# ---------------------------------------------------------------------
with tab1:
    st.header("ELISA NETs/cfDNA Analysis")
    st.write(
        "Upload your own standards and samples CSVs, or use the bundled "
        "sample data to see how the pipeline works."
    )

    use_sample = st.checkbox("Use bundled sample data", value=True)

    if use_sample:
        standards_path = "sample_data/standards_data.csv"
        samples_path = "sample_data/samples_data.csv"
        results = run_pipeline(standards_path, samples_path)
    else:
        standards_file = st.file_uploader("Upload standards_data.csv", type="csv", key="standards")
        samples_file = st.file_uploader("Upload samples_data.csv", type="csv", key="samples")
        results = None
        if standards_file and samples_file:
            standards_path = "temp_standards.csv"
            samples_path = "temp_samples.csv"
            with open(standards_path, "wb") as f:
                f.write(standards_file.getbuffer())
            with open(samples_path, "wb") as f:
                f.write(samples_file.getbuffer())
            results = run_pipeline(standards_path, samples_path)

    if results is not None:
        st.subheader("Processed Results")
        st.dataframe(
            results[["plate_id", "patient_id", "timepoint", "final_concentration", "flag"]],
            use_container_width=True,
        )

        comparison = summarize_pre_post(results)
        st.subheader("Pre vs Post Treatment Comparison")
        st.dataframe(comparison, use_container_width=True)

        fig, ax = plt.subplots(figsize=(7, 4))
        colors = ["crimson" if x > 0 else "steelblue" for x in comparison["percent_change"]]
        ax.bar(comparison.index, comparison["percent_change"], color=colors)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel("% Change")
        ax.set_title("% Change in NETs Concentration (Post vs Pre)")
        st.pyplot(fig)

# ---------------------------------------------------------------------
# TAB 2: Wearable dashboard
# ---------------------------------------------------------------------
with tab2:
    st.header("Wearable Vitals Monitoring")

    threshold = st.slider("Heart rate alert threshold (bpm)", 60, 100, 80)
    min_days = st.slider("Minimum consecutive days to trigger alert", 1, 7, 3)

    data = generate_wearable_data()
    data = flag_elevated_heart_rate(data, threshold=threshold, min_consecutive_days=min_days)

    st.subheader("14-Day Vitals Data")
    st.dataframe(data, use_container_width=True)

    if data["alert"].any():
        st.warning("⚠️ Sustained elevated heart rate detected on flagged days above.")

    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    axes[0].plot(data["date"], data["heart_rate"], marker="o", color="crimson")
    alert_days = data[data["alert"]]
    if not alert_days.empty:
        axes[0].scatter(alert_days["date"], alert_days["heart_rate"], color="black", zorder=5, label="Alert")
        axes[0].legend()
    axes[0].axhline(threshold, color="gray", linestyle="--", linewidth=0.8)
    axes[0].set_ylabel("Heart Rate (bpm)")

    axes[1].plot(data["date"], data["steps"], marker="o", color="steelblue")
    axes[1].set_ylabel("Steps")
    axes[1].set_xlabel("Date")

    plt.tight_layout()
    st.pyplot(fig)
