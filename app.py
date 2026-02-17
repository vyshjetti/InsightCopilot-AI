import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
h3 { font-weight:600; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="InsightCopilot AI",
    layout="wide"
)

# -----------------------------
# HEADER
# -----------------------------
st.title("InsightCopilot AI")
st.subheader("Enterprise KPI Intelligence Assistant")
st.divider()

# -----------------------------
# FILE UPLOAD
# -----------------------------
st.header("Upload Business Dataset")
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# -----------------------------
# DATA VARIABLES (SAFE DEFAULTS)
# -----------------------------
df = None
main_metric = None
total_value = None
avg_value = None
row_count = None

# -----------------------------
# LOAD DATA
# -----------------------------
if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # --- AUTO DATE DETECTION ---
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    date_cols = [col for col in df.columns if "date" in col.lower()]
    if len(date_cols) > 0:
        df = df.sort_values(by=date_cols[0])

    # --- SMART METRIC DETECTION ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    for col in numeric_cols:
        if "revenue" in col.lower() or "sales" in col.lower() or "total" in col.lower():
            main_metric = col
            break

    if main_metric is None and len(numeric_cols) > 0:
        main_metric = numeric_cols[0]

    # --- KPI CALCULATIONS ---
    row_count = len(df)
    if main_metric:
        total_value = round(df[main_metric].sum(), 2)
        avg_value = round(df[main_metric].mean(), 2)

    st.success("Dataset loaded successfully")
    st.subheader("Data Preview")
    st.dataframe(df.head())

# -----------------------------
# KPI CARDS (DYNAMIC)
# -----------------------------
col1, col2, col3 = st.columns(3)

if df is not None and main_metric is not None:

    col1.metric(
        label=f"Total {main_metric}",
        value=f"{total_value:,.2f}"
    )

    col2.metric(
        label=f"Average {main_metric}",
        value=f"{avg_value:,.2f}"
    )

    col3.metric(
        label="Total Records",
        value=f"{row_count:,}"
    )

else:
    col1.metric("Revenue", "$120,000")
    col2.metric("Active Users", "3,420")
    col3.metric("Churn Rate", "4.2%")

st.divider()

# -----------------------------
# ASK INSIGHT SECTION
# -----------------------------
st.header("Ask InsightCopilot")

user_question = st.text_input(
    "Ask a business question (e.g., Explain revenue trends)"
)

# -----------------------------
# LAYOUT
# -----------------------------
left, right = st.columns([2,1])

# -----------------------------
# LEFT PANEL — ENTERPRISE VISUALIZATION
# -----------------------------
with left:
    st.subheader("Data Visualization")

    if df is not None:

        # Prevent ID columns from dropdown
        safe_columns = [c for c in df.columns if "id" not in c.lower()]

        x_axis = st.selectbox("Select X-axis", safe_columns)
        y_axis = st.selectbox("Select Y-axis", df.select_dtypes(include="number").columns)

        # -----------------------------
        # ENTERPRISE SMART VISUALIZATION LOGIC
        # -----------------------------
        if "id" in x_axis.lower():
            st.warning("InsightCopilot detected an ID column. Switching to distribution view.")
            chart = px.histogram(df, x=y_axis, title="Distribution Analysis")

        else:
            date_cols = [col for col in df.columns if "date" in col.lower()]

            if len(date_cols) > 0 and x_axis in date_cols:
                agg_df = df.groupby(x_axis, as_index=False)[y_axis].sum()

                chart = px.line(
                    agg_df,
                    x=x_axis,
                    y=y_axis,
                    title="InsightCopilot Trend Analysis"
                )
            else:
                agg_df = df.groupby(x_axis, as_index=False)[y_axis].sum()

                chart = px.bar(
                    agg_df,
                    x=x_axis,
                    y=y_axis,
                    title="InsightCopilot Comparative Analysis"
                )

        st.plotly_chart(chart, use_container_width=True)

    else:
        st.info("Upload a dataset to see charts")

# -----------------------------
# RIGHT PANEL — EXECUTIVE SUMMARY
# -----------------------------
with right:
    st.subheader("Executive Summary")

    if df is not None and user_question and main_metric is not None:

        avg_value = round(df[main_metric].mean(), 2)
        max_value = df[main_metric].max()
        min_value = df[main_metric].min()

        st.markdown(f"""
### Key Business Insight
Average **{main_metric}** is **{avg_value}**, with peak performance at **{max_value}**.

### Risk or Concern
Performance variability detected — monitor fluctuations.

### Executive Recommendation
Investigate drivers behind lower values like **{min_value}** and optimize strategy.
""")
    else:
        st.info("Upload data and ask a question to generate insights")
