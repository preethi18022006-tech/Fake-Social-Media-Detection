import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="FAKE-GUARD",
    page_icon="🛡️",
    layout="wide"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #f6f8fc;
}
.kpi {
    background: white;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.risk-box {
    background: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
.badge-high {color:white;background:#e74c3c;padding:6px 14px;border-radius:20px;}
.badge-med {color:white;background:#f39c12;padding:6px 14px;border-radius:20px;}
.badge-low {color:white;background:#2ecc71;padding:6px 14px;border-radius:20px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("fake_guard_results.csv")

# -----------------------------
# ADVANCED DASHBOARD RISK COMPUTATION (KEY FIX)
# -----------------------------
# Log scale posts (amplifies heavy posting)
df["posts_score"] = np.log1p(df["total_posts"]) / np.log1p(df["total_posts"].max())

# Square duplicate ratio (amplifies repetition)
df["dup_score"] = (df["duplicate_ratio"] ** 2) / (
    (df["duplicate_ratio"].max() ** 2) + 1e-9
)

# Invert + normalize text length (short repetitive text = risky)
df["length_score"] = (
    df["avg_text_length"].max() - df["avg_text_length"]
) / df["avg_text_length"].max()

# Weighted raw risk (0–1)
df["raw_risk"] = (
    0.45 * df["posts_score"] +
    0.40 * df["dup_score"] +
    0.15 * df["length_score"]
)

# Percentile-based scaling → full 0–100 spread
df["dashboard_risk"] = df["raw_risk"].rank(pct=True) * 100

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🛡️ FAKE-GUARD")
st.sidebar.caption("Central Monitoring Dashboard")

selected_user = st.sidebar.selectbox(
    "Select Account ID",
    df["user_id"].unique()
)

# -----------------------------
# Header
# -----------------------------
st.title("Fake Social Media Account Detection")
st.caption("Central Agency Risk Monitoring Dashboard")

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="kpi">
<h3>{len(df)}</h3>
<p>Total Accounts</p>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi">
<h3>{(df['dashboard_risk'] >= 70).sum()}</h3>
<p>High Risk</p>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi">
<h3>{(df['dashboard_risk'].between(40,70)).sum()}</h3>
<p>Medium Risk</p>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi">
<h3>{(df['dashboard_risk'] < 40).sum()}</h3>
<p>Low Risk</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Selected account details
# -----------------------------
row = df[df["user_id"] == selected_user].iloc[0]
risk = row["dashboard_risk"]

if risk >= 70:
    badge = "<span class='badge-high'>HIGH RISK</span>"
elif risk >= 40:
    badge = "<span class='badge-med'>MEDIUM RISK</span>"
else:
    badge = "<span class='badge-low'>LOW RISK</span>"

left, right = st.columns([2,1])

left.markdown(f"""
<div class="risk-box">
<h2>Account Risk Overview</h2>
<h1>{risk:.2f}</h1>
{badge}
<br><br>
<b>User ID:</b> {selected_user}
</div>
""", unsafe_allow_html=True)

right.markdown("### Risk Level")
right.progress(int(risk))

# -----------------------------
# Behavioral indicators
# -----------------------------
st.markdown("### 📊 Behavioral Indicators")
m1, m2, m3 = st.columns(3)

m1.metric("Total Posts", int(row["total_posts"]))
m2.metric("Avg Text Length", int(row["avg_text_length"]))
m3.metric("Duplicate Ratio", round(row["duplicate_ratio"], 3))

# -----------------------------
# Recommended action
# -----------------------------
st.markdown("### 🚨 Recommended Action")

if risk >= 70:
    st.error("Immediate suspension + Legal escalation")
elif risk >= 40:
    st.warning("Manual analyst review required")
else:
    st.success("No action required")

# -----------------------------
# Top risky accounts table
# -----------------------------
st.markdown("---")
st.markdown("### 🔥 Top High-Risk Accounts")

top_df = df.sort_values("dashboard_risk", ascending=False).head(5)
st.dataframe(
    top_df[["user_id", "dashboard_risk", "total_posts", "duplicate_ratio"]],
    use_container_width=True
)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("## ⚙️ Dynamic Account Risk Prediction (Rule-Based)")

st.write(
    "This module simulates real-time risk assessment using "
    "behavioral rules (no ML model involved)."
)

# Input fields
d_posts = st.number_input(
    "Total Posts",
    min_value=0,
    value=30
)

d_len = st.number_input(
    "Average Text Length",
    min_value=1,
    value=50
)

d_dup = st.slider(
    "Duplicate Content Ratio",
    0.0, 1.0, 0.1
)

if st.button("Calculate Dynamic Risk"):
    risk = 0

    # Posting frequency rule
    if d_posts > 200:
        risk += 40
    elif d_posts > 100:
        risk += 25
    elif d_posts > 50:
        risk += 15

    # Text length rule
    if d_len < 20:
        risk += 30
    elif d_len < 50:
        risk += 15

    # Duplicate ratio rule
    if d_dup > 0.6:
        risk += 40
    elif d_dup > 0.3:
        risk += 25
    elif d_dup > 0.1:
        risk += 10

    risk = min(risk, 100)

    st.metric("Dynamic Risk Score", risk)

    if risk >= 70:
        st.error("HIGH RISK: Likely Fake Account")
    elif risk >= 40:
        st.warning("MEDIUM RISK: Suspicious Account")
    else:
        st.success("LOW RISK: Likely Genuine")
st.markdown("""
<hr>
<p style="text-align:center;color:gray;font-size:13px;">
FAKE-GUARD | Cybersecurity & Social Media Threat Intelligence<br>
</p>
""", unsafe_allow_html=True)