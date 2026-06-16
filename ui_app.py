import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Product Similarity Checker")

existing_file = st.file_uploader("Upload Existing Excel")
new_file = st.file_uploader("Upload New Excel")

threshold = st.slider("Threshold", 0, 100, 60)

if existing_file and new_file:

    existing = pd.read_excel(existing_file)
    new = pd.read_excel(new_file)

    existing.columns = existing.columns.str.strip()
    new.columns = new.columns.str.strip()

    existing = existing.rename(columns={
        "Material": "Code",
        "Material Description": "Description"
    })

    new = new.rename(columns={
        "MaterialCode": "Code",
        "Material Description": "Description"
    })

    existing_list = existing["Description"].astype(str).tolist()

    results = []

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
                "Similarity": match[1]
            })

    df = pd.DataFrame(results)

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download", csv, "report.csv", "text/csv")