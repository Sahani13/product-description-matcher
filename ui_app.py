import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Product Matching System", layout="centered")

st.markdown(
    "<h2 style='text-align: center;'>📦 Product Description Matching System</h2>",
    unsafe_allow_html=True
)

# =========================
# INFO SECTION
# =========================
st.info("""
📌 IMPORTANT: Excel File Structure

✔ Existing Products File and New Products File must contain:
- Material OR MaterialCode
- Material Description

⚠️ File must be .xlsx format only
⚠️ Do NOT modify column names unnecessarily

The system will match product descriptions using similarity scoring.
""")

# =========================
# SAMPLE FORMAT
# =========================
st.subheader("📊 Expected Excel Format")

st.markdown("### ✔ Products File Example")
st.table({
    "Material": ["5000197", "5000198"],
    "Material Description": [
        "GS - SAL - 6 inch Local Billet",
        "Unprinted Polythene"
    ]
})

# =========================
# UPLOAD SECTION
# =========================
st.subheader("📁 Upload Excel Files")

st.write("""
Please ensure your Excel files follow the correct format.

✔ Only .xlsx files  
✔ First sheet only  
✔ No merged cells  
✔ Correct column names required  
""")

existing_file = st.file_uploader("Upload Existing Products File", type=["xlsx"])
new_file = st.file_uploader("Upload New Products File", type=["xlsx"])

threshold = st.slider("🎯 Similarity Threshold", 0, 100, 60)

# =========================
# PROCESSING
# =========================
if existing_file and new_file:

    # Read Excel
    existing = pd.read_excel(existing_file)
    new = pd.read_excel(new_file)

    # Clean column names
    existing.columns = existing.columns.str.strip()
    new.columns = new.columns.str.strip()

    # =========================
    # VALIDATION (SAFE)
    # =========================
    if (
        "Material" not in existing.columns
        and "MaterialCode" not in existing.columns
    ):
        st.error("❌ Existing file must contain 'Material' or 'MaterialCode'")
        st.stop()

    if "Material Description" not in existing.columns:
        st.error("❌ Existing file missing 'Material Description'")
        st.stop()

    if (
        "Material" not in new.columns
        and "MaterialCode" not in new.columns
    ):
        st.error("❌ New file must contain 'Material' or 'MaterialCode'")
        st.stop()

    if "Material Description" not in new.columns:
        st.error("❌ New file missing 'Material Description'")
        st.stop()

    # =========================
    # STANDARDIZE COLUMNS
    # =========================
    existing = existing.rename(columns={
        "Material": "Code",
        "MaterialCode": "Code",
        "Material Description": "Description"
    })

    new = new.rename(columns={
        "Material": "Code",
        "MaterialCode": "Code",
        "Material Description": "Description"
    })

    # Convert to list
    existing_list = existing["Description"].astype(str).tolist()

    results = []

    # =========================
    # MATCHING LOGIC
    # =========================
    for _, row in new.iterrows():

        new_desc = str(row["Description"])

        match = process.extractOne(
            new_desc,
            existing_list,
            scorer=fuzz.token_sort_ratio
        )

        if match and match[1] >= threshold:
            results.append({
                "New Product": new_desc,
                "Best Match": match[0],
                "Similarity (%)": match[1]
            })

    df = pd.DataFrame(results)

    # =========================
    # OUTPUT
    # =========================
    st.subheader("📊 Matching Results")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Report",
        csv,
        "product_matching_report.csv",
        "text/csv"
    )
