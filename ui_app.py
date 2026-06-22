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
st.subheader("📁 Upload Excel Files Here")

existing_file = st.file_uploader("Upload Existing Products File", type=["xlsx"])
new_file = st.file_uploader("Upload New Products File", type=["xlsx"])

# =========================
#Threshold slider
# =========================
threshold = st.slider("🎯 Similarity Threshold", 0, 100, 60)

match_mode = st.radio(
    "Match Mode",
    [
        "Best Match Only",
        "Top 10 Matches",
        "All Matches Above Threshold"
    ]
)

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
    # VALIDATION 
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

    # =========================
    # Convert to list
    # =========================
    existing_list = existing["Description"].astype(str).tolist()

    results = []

    for _, row in new.iterrows():

        new_desc = str(row["Description"])

    # =========================
    # BEST MATCH ONLY
    # =========================
        if match_mode == "Best Match Only":

            match = process.extractOne(
                new_desc,
                existing_list,
                scorer=fuzz.token_sort_ratio
            )

            if match and match[1] >= threshold:

                results.append({
                    "New Product": new_desc,
                    "Rank": 1,
                    "Matched Product": match[0],
                    "Similarity (%)": round(match[1], 2)
                })

    # =========================
    # TOP 10 MATCHES
    # =========================
        elif match_mode == "Top 10 Matches":

            matches = process.extract(
                new_desc,
                existing_list,
                scorer=fuzz.token_sort_ratio,
                limit=10
            )

            rank = 1

            for matched_desc, score, _ in matches:

                if score >= threshold:

                    results.append({
                        "New Product": new_desc,
                        "Rank": rank,
                        "Matched Product": matched_desc,
                        "Similarity (%)": round(score, 2)
                    })

                    rank += 1

    # =========================
    # ALL MATCHES ABOVE THRESHOLD
    # =========================
        elif match_mode == "All Matches Above Threshold":

            matches = process.extract(
                new_desc,
                existing_list,
                scorer=fuzz.token_sort_ratio,
                limit=None
            )

            rank = 1

            for matched_desc, score, _ in matches:

                if score >= threshold:

                    results.append({
                        "New Product": new_desc,
                        "Rank": rank,
                        "Matched Product": matched_desc,
                        "Similarity (%)": round(score, 2)
                    })

                    rank += 1

    df = pd.DataFrame(results)

    # =========================
    # OUTPUT
    # =========================
    st.subheader("📊 Matching Results")

    st.success(f"Found {len(df)} matching records")

    st.dataframe(   
        df,
        use_container_width=True,
        hide_index=True
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Report",
        csv,
        "product_matching_report.csv",
        "text/csv"
    )







