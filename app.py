
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Loan Approval Analysis",
    page_icon="🏦",
    layout="wide"
)

st.markdown("""
<style>
.stApp {background-color: #f2f6fc;}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px #d7e0ee;
}
h1 {color: #173b70;}
</style>
""", unsafe_allow_html=True)

st.title("🏦 Loan Approval Analysis Dashboard")
st.write("Explore loan applications, customer profiles and approval patterns.")

# Load the dataset stored in this repository
file_path = Path("Loan_approval_data_2025.xlsx")

if not file_path.exists():
    st.error(
        "Dataset not found. Upload Loan_approval_data_2025.xlsx "
        "to the same GitHub repository as app.py."
    )
    st.stop()

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()

required = [
    "loan_status", "product_type", "loan_intent",
    "occupation_status", "age", "annual_income",
    "credit_score", "loan_amount"
]
missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Dataset columns not found: {', '.join(missing)}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# Normalize status labels; verify numeric coding with dataset documentation.
def label_status(value):
    if pd.isna(value):
        return "Unknown"
    value = str(value).strip().lower()
    if value in ["1", "approved", "approve", "yes"]:
        return "Approved"
    if value in ["0", "rejected", "reject", "no", "denied"]:
        return "Rejected"
    return value.title()

df["status_label"] = df["loan_status"].apply(label_status)

st.sidebar.header("🔎 Dashboard Filters")

products = st.sidebar.multiselect(
    "Loan Product",
    sorted(df["product_type"].dropna().unique()),
    default=sorted(df["product_type"].dropna().unique())
)
intents = st.sidebar.multiselect(
    "Loan Purpose",
    sorted(df["loan_intent"].dropna().unique()),
    default=sorted(df["loan_intent"].dropna().unique())
)
occupations = st.sidebar.multiselect(
    "Employment Status",
    sorted(df["occupation_status"].dropna().unique()),
    default=sorted(df["occupation_status"].dropna().unique())
)

filtered = df[
    df["product_type"].isin(products)
    & df["loan_intent"].isin(intents)
    & df["occupation_status"].isin(occupations)
].copy()

if filtered.empty:
    st.warning("No applications match these filters.")
    st.stop()

total = len(filtered)
approved = (filtered["status_label"] == "Approved").sum()
rejected = (filtered["status_label"] == "Rejected").sum()
approval_rate = approved / total * 100

a, b, c, d = st.columns(4)
a.metric("Total Applications", f"{total:,}")
b.metric("Approved", f"{approved:,}")
c.metric("Rejected", f"{rejected:,}")
d.metric("Approval Rate", f"{approval_rate:.1f}%")

e, f = st.columns(2)
e.metric("Average Loan Amount", f"{filtered['loan_amount'].mean():,.2f}")
f.metric("Average Credit Score", f"{filtered['credit_score'].mean():,.1f}")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("📊 Application Status")
    status_data = filtered["status_label"].value_counts().rename_axis(
        "Status"
    ).reset_index(name="Applications")
    fig = px.pie(
        status_data, names="Status", values="Applications",
        hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💳 Applications by Product")
    product_data = filtered["product_type"].value_counts().reset_index()
    product_data.columns = ["Product", "Applications"]
    fig = px.bar(
        product_data, x="Product", y="Applications",
        color="Applications", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🎯 Applications by Loan Purpose")
    intent_data = filtered["loan_intent"].value_counts().reset_index()
    intent_data.columns = ["Purpose", "Applications"]
    fig = px.bar(
        intent_data, x="Purpose", y="Applications",
        color="Applications", color_continuous_scale="Teal"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Credit Score by Status")
    fig = px.histogram(
        filtered, x="credit_score", color="status_label",
        barmode="overlay", opacity=0.7,
        color_discrete_sequence=["#16a085", "#e67e22", "#8e44ad"]
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("💰 Annual Income vs Loan Amount")
fig = px.scatter(
    filtered, x="annual_income", y="loan_amount",
    color="status_label", hover_data=["age", "credit_score"],
    color_discrete_sequence=px.colors.qualitative.Bold
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("💡 Business Insights")
st.write(
    f"After applying the selected filters, there are **{total:,} applications**. "
    f"Of these, **{approved:,} are labelled approved** and "
    f"**{rejected:,} are labelled rejected**. "
    f"The approval rate among all filtered applications is **{approval_rate:.1f}%**."
)

if not filtered["product_type"].dropna().empty:
    st.write(
        "Most common product: **"
        + str(filtered["product_type"].mode().iloc[0]) + "**."
    )
if not filtered["loan_intent"].dropna().empty:
    st.write(
        "Most common loan purpose: **"
        + str(filtered["loan_intent"].mode().iloc[0]) + "**."
    )

st.caption(
    "Interpretation note: confirm how loan_status values are coded "
    "in the original dataset documentation before presenting approval rates."
)

st.subheader("📋 Application Data")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "Download Filtered Data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_loan_applications.csv",
    mime="text/csv"
)
