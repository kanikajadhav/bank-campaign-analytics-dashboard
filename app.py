"""
Bank Marketing Campaign Performance Dashboard
============================================
Technologies: Python, Pandas, SQLite, SQL, Streamlit, Plotly
Dataset: UCI Bank Marketing Dataset (auto-downloaded)
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campaign Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #02070f; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A3A5C 0%, #1F5C99 100%);
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stMultiSelect span { color: #082442 !important; }
    
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #7396ba !important;
}

    div[data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E0E7EF;
        border-left: 5px solid #1F5C99;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(31,92,153,0.07);
    }
    div[data-testid="metric-container"] label {
        color: #6B7A99 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #1A3A5C !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
    }

    .section-title {
        color: #1A3A5C;
        font-size: 1.05rem;
        font-weight: 700;
        padding: 6px 0 4px 0;
        border-bottom: 2px solid #1F5C99;
        margin-bottom: 8px;
    }

    .insight-box {
        background: #EBF4FF;
        border-left: 4px solid #1F5C99;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.88rem;
        color: #000205;
    }

    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #1F5C99, #2980b9);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 600;
    }
    .stButton > button:hover { background: #1A3A5C; color: white; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Chart constants ───────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    plot_bgcolor="#1a1a1a",
    paper_bgcolor="#1a1a1a",
    font=dict(family="Arial", color="#FFFFFF"),
    margin=dict(t=30, b=30, l=10, r=10),
    coloraxis_showscale=False,
)
BLUE_SCALE = ["#AED6F1", "#5DADE2", "#2E86C1", "#1F5C99", "#1A3A5C"]
PRIMARY    = "#1F5C99"
SECONDARY  = "#4A90BE"


# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset...")
def load_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip"
    try:
        import urllib.request, zipfile, io as _io
        with urllib.request.urlopen(url, timeout=15) as r:
            z = zipfile.ZipFile(_io.BytesIO(r.read()))
            with z.open("bank-additional/bank-additional-full.csv") as f:
                df = pd.read_csv(f, sep=";")
    except Exception:
        df = _synthetic()

    df.columns = df.columns.str.strip().str.lower().str.replace("-", "_")
    df.rename(columns={"y": "subscribed"}, inplace=True)
    df["subscribed_flag"] = (df["subscribed"] == "yes").astype(int)
    df.replace("unknown", pd.NA, inplace=True)

    df["age_group"] = pd.cut(df["age"],
        bins=[17, 25, 35, 45, 55, 65, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"])
    df["campaign_calls_group"] = pd.cut(df["campaign"],
        bins=[0, 1, 3, 5, 100],
        labels=["1 call", "2-3 calls", "4-5 calls", "6+ calls"])
    df["age_group"]            = df["age_group"].astype(str)
    df["campaign_calls_group"] = df["campaign_calls_group"].astype(str)
    return df


def _synthetic():
    import numpy as np
    np.random.seed(42)
    n = 5000
    return pd.DataFrame({
        "age":      np.random.randint(18, 80, n),
        "job":      np.random.choice(["admin.", "technician", "services", "management",
                                       "retired", "blue-collar", "student", "entrepreneur"], n),
        "marital":  np.random.choice(["married", "single", "divorced"], n, p=[0.6, 0.3, 0.1]),
        "education":np.random.choice(["university.degree", "high.school",
                                       "basic.9y", "professional.course"], n),
        "contact":  np.random.choice(["telephone", "cellular"], n, p=[0.36, 0.64]),
        "month":    np.random.choice(["jan","feb","mar","apr","may","jun",
                                       "jul","aug","sep","oct","nov","dec"], n),
        "duration": np.random.exponential(250, n).astype(int).clip(1, 3000),
        "campaign": np.random.randint(1, 15, n),
        "poutcome": np.random.choice(["nonexistent", "failure", "success"], n, p=[0.86, 0.10, 0.04]),
        "y":        np.random.choice(["yes", "no"], n, p=[0.113, 0.887])
    })


# ── Thread-safe SQL: fresh connection every call ──────────────────────────────
def run_sql(df, query):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("campaign", conn, index=False, if_exists="replace")
    try:
        result = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return result


# ── Load & filter ─────────────────────────────────────────────────────────────
df = load_data()

with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")
    job_opts     = sorted(df["job"].dropna().unique().tolist())
    month_opts   = sorted(df["month"].dropna().unique().tolist())
    contact_opts = sorted(df["contact"].dropna().unique().tolist())
    sel_jobs    = st.multiselect("💼 Job Category",   job_opts,     default=job_opts)
    sel_months  = st.multiselect("📅 Campaign Month", month_opts,   default=month_opts)
    sel_contact = st.multiselect("📞 Contact Method", contact_opts, default=contact_opts)
    age_range   = st.slider("👤 Age Range", 18, 95, (18, 95))
    st.markdown("---")
    st.caption("Data: UCI Bank Marketing Dataset\n41,188 records · 20 features")

mask = (
    df["job"].isin(sel_jobs) &
    df["month"].isin(sel_months) &
    df["contact"].isin(sel_contact) &
    df["age"].between(age_range[0], age_range[1])
)
dff = df[mask].copy()

if dff.empty:
    st.warning("No data matches current filters. Adjust sidebar filters.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#1A3A5C,#1F5C99,#2980b9);
            padding:24px 32px;border-radius:14px;margin-bottom:20px;">
  <h1 style="color:white;margin:0;font-size:1.8rem;">📊 Bank Marketing Campaign Analytics</h1>
  <p style="color:#AED6F1;margin:4px 0 0 0;font-size:0.9rem;">
    Interactive dashboard · customer response rates · conversion drivers · campaign optimisation
  </p>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total     = len(dff)
converted = int(dff["subscribed_flag"].sum())
conv_rate = round(100 * converted / total, 2)
avg_dur   = int(dff["duration"].mean())
avg_calls = round(float(dff["campaign"].mean()), 1)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📞 Total Contacts",    f"{total:,}")
k2.metric("✅ Conversions",       f"{converted:,}")
k3.metric("📈 Conversion Rate",   f"{conv_rate}%")
k4.metric("⏱ Avg Call Duration", f"{avg_dur}s")
k5.metric("📋 Avg Calls/Contact", f"{avg_calls}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Job + Monthly trend ────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Conversion Rate by Job Category</div>', unsafe_allow_html=True)
    job_df = (dff.dropna(subset=["job"])
                 .groupby("job")
                 .agg(total=("subscribed_flag","count"), converted=("subscribed_flag","sum"))
                 .assign(rate=lambda x: (100*x.converted/x.total).round(2))
                 .sort_values("rate", ascending=True).reset_index())
    fig1 = px.bar(job_df, x="rate", y="job", orientation="h",
                  color="rate", color_continuous_scale=BLUE_SCALE,
                  text="rate", labels={"rate":"Conv. Rate (%)","job":""})
    fig1.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
    fig1.update_layout(**CHART_LAYOUT, height=380,
                       xaxis=dict(showgrid=True, gridcolor="#F0F4F8"),
                       yaxis=dict(showgrid=False))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">Monthly Volume vs Conversion Rate</div>', unsafe_allow_html=True)
    month_order = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    mon_df = (dff.dropna(subset=["month"])
                 .groupby("month")
                 .agg(contacts=("subscribed_flag","count"), converted=("subscribed_flag","sum"))
                 .assign(rate=lambda x: (100*x.converted/x.contacts).round(2))
                 .reindex([m for m in month_order if m in dff["month"].dropna().values])
                 .reset_index())
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Bar(x=mon_df["month"], y=mon_df["contacts"],
                          name="Contacts", marker_color=SECONDARY, marker_line_width=0),
                   secondary_y=False)
    fig2.add_trace(go.Scatter(x=mon_df["month"], y=mon_df["rate"],
                              name="Conv. Rate %", mode="lines+markers",
                              line=dict(color=PRIMARY, width=3),
                              marker=dict(size=8, color=PRIMARY)),
                   secondary_y=True)
    fig2.update_layout(**CHART_LAYOUT, height=380,
                       legend=dict(orientation="h", y=1.12, x=0),
                       xaxis=dict(showgrid=False))
    fig2.update_yaxes(title_text="Contacts", gridcolor="#F0F4F8", secondary_y=False)
    fig2.update_yaxes(title_text="Conv. Rate (%)", showgrid=False, secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Age + Contact ──────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-title">Customer Response by Age Group</div>', unsafe_allow_html=True)
    age_df = (dff.dropna(subset=["age_group"])
                 .query("age_group != 'nan'")
                 .groupby(["age_group","subscribed"])
                 .size().reset_index(name="count"))
    fig3 = px.bar(age_df, x="age_group", y="count", color="subscribed",
                  barmode="group",
                  color_discrete_map={"yes": PRIMARY, "no": SECONDARY},
                  labels={"age_group":"Age Group","count":"Count","subscribed":"Subscribed"})
    fig3.update_traces(marker_line_width=0)
    fig3.update_layout(**CHART_LAYOUT, height=350,
                       legend=dict(orientation="h", y=1.12, title=""),
                       xaxis=dict(showgrid=False),
                       yaxis=dict(gridcolor="#F0F4F8"))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">Contact Method Effectiveness</div>', unsafe_allow_html=True)
    contact_df = (dff.dropna(subset=["contact"])
                     .groupby("contact")
                     .agg(total=("subscribed_flag","count"), converted=("subscribed_flag","sum"))
                     .assign(rate=lambda x: (100*x.converted/x.total).round(2))
                     .reset_index())
    fig4 = make_subplots(rows=1, cols=2, specs=[[{"type":"pie"},{"type":"bar"}]],
                         subplot_titles=("Volume Split","Conversion Rate %"))
    fig4.add_trace(go.Pie(labels=contact_df["contact"], values=contact_df["total"],
                          hole=0.5, marker_colors=[PRIMARY, SECONDARY],
                          textinfo="label+percent", showlegend=False), row=1, col=1)
    fig4.add_trace(go.Bar(x=contact_df["contact"], y=contact_df["rate"],
                          marker_color=[PRIMARY, SECONDARY],
                          text=(contact_df["rate"].astype(str) + "%"),
                          textposition="outside", showlegend=False,
                          marker_line_width=0), row=1, col=2)
    fig4.update_layout(**CHART_LAYOUT, height=350)
    fig4.update_yaxes(gridcolor="#F0F4F8", row=1, col=2)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Duration + Calls ───────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-title">Call Duration vs Conversion</div>', unsafe_allow_html=True)
    sample = dff.sample(min(2000, len(dff)), random_state=42)
    fig5 = px.histogram(sample, x="duration", color="subscribed", nbins=50,
                        barmode="overlay", opacity=0.8,
                        color_discrete_map={"yes": PRIMARY, "no": SECONDARY},
                        labels={"duration":"Call Duration (seconds)","subscribed":"Subscribed"})
    fig5.update_traces(marker_line_width=0)
    fig5.update_layout(**CHART_LAYOUT, height=350,
                       legend=dict(orientation="h", y=1.12, title=""),
                       xaxis=dict(showgrid=False),
                       yaxis=dict(gridcolor="#F0F4F8"))
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown('<div class="section-title">Conversion Rate by No. of Campaign Calls</div>', unsafe_allow_html=True)
    calls_df = (dff.dropna(subset=["campaign_calls_group"])
                   .query("campaign_calls_group != 'nan'")
                   .groupby("campaign_calls_group")
                   .agg(total=("subscribed_flag","count"), converted=("subscribed_flag","sum"))
                   .assign(rate=lambda x: (100*x.converted/x.total).round(2))
                   .reset_index())
    fig6 = px.bar(calls_df, x="campaign_calls_group", y="rate",
                  color="rate", color_continuous_scale=BLUE_SCALE, text="rate",
                  labels={"campaign_calls_group":"Number of Calls","rate":"Conversion Rate (%)"})
    fig6.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
    fig6.update_layout(**CHART_LAYOUT, height=350,
                       xaxis=dict(showgrid=False),
                       yaxis=dict(gridcolor="#F0F4F8"))
    st.plotly_chart(fig6, use_container_width=True)

# ── Key Insights ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">💡 Key Insights</div>', unsafe_allow_html=True)
ic1, ic2, ic3 = st.columns(3)
with ic1:
    best_job = job_df.sort_values("rate", ascending=False).iloc[0]
    st.markdown(f'<div class="insight-box">🏆 <b>{best_job["job"].title()}</b> has the highest conversion rate at <b>{best_job["rate"]}%</b></div>', unsafe_allow_html=True)
with ic2:
    best_month = mon_df.sort_values("rate", ascending=False).iloc[0]
    st.markdown(f'<div class="insight-box">📅 <b>{best_month["month"].title()}</b> is the best performing month at <b>{best_month["rate"]}%</b> conversion</div>', unsafe_allow_html=True)
with ic3:
    best_contact = contact_df.sort_values("rate", ascending=False).iloc[0]
    st.markdown(f'<div class="insight-box">📞 <b>{best_contact["contact"].title()}</b> contact converts at <b>{best_contact["rate"]}%</b> — outperforming other methods</div>', unsafe_allow_html=True)

# ── SQL Explorer ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🔎 Live SQL Query Explorer</div>', unsafe_allow_html=True)
st.caption("Write SQL directly against the `campaign` table. Standard SQLite syntax supported.")

default_q = """SELECT job, education,
       COUNT(*) AS total_contacts,
       SUM(subscribed_flag) AS conversions,
       ROUND(100.0 * SUM(subscribed_flag) / COUNT(*), 2) AS conversion_rate
FROM campaign
GROUP BY job, education
ORDER BY conversion_rate DESC
LIMIT 15"""

user_query = st.text_area("SQL Query", value=default_q, height=140)
run_col, _ = st.columns([1, 5])

if run_col.button("▶ Run Query"):
    try:
        result = run_sql(dff, user_query)
        st.dataframe(result, use_container_width=True, height=300)
        st.success(f"✅ Query returned {len(result):,} rows")
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export Result as CSV", csv,
                           "query_result.csv", "text/csv")
    except Exception as e:
        st.error(f"SQL Error: {e}")

# ── Raw Data ──────────────────────────────────────────────────────────────────
with st.expander("📋 Raw Data Preview"):
    st.dataframe(dff.head(200), use_container_width=True)
    csv_full = dff.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Filtered Dataset", csv_full,
                       "filtered_campaign_data.csv", "text/csv")

st.markdown("---")
st.caption("📊 Campaign Analytics Dashboard · Python · Pandas · SQLite · Streamlit · Plotly")