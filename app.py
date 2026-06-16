import pandas as pd
from rapidfuzz import process, fuzz

# Load Excel files
existing = pd.read_excel("input/existing_products.xlsx")
new = pd.read_excel("input/new_products.xlsx")

# Clean column names
existing.columns = existing.columns.str.strip()
new.columns = new.columns.str.strip()

# Rename columns (safe handling)
existing = existing.rename(columns={
    "Material": "Code",
    "Material Description": "Description"
})

new = new.rename(columns={
    "MaterialCode": "Code",
    "Material Description": "Description"
})

# Prepare data
existing_desc = existing["Description"].astype(str).tolist()

results = []

# Threshold (important)
THRESHOLD = 60

for _, row in new.iterrows():

    new_desc = str(row["Description"])

    # Get top 50 matches
    matches = process.extract(
        new_desc,
        existing_desc,
        scorer=fuzz.token_sort_ratio,
        limit=50
    )

    # Keep ONLY best match above threshold
    best_match = None
    best_score = 0

    for match in matches:
        if match[1] > best_score:
            best_match = match[0]
            best_score = match[1]

    # Save only meaningful matches
    if best_score >= THRESHOLD:
        results.append({
            "New Product": new_desc,
            "Best Match": best_match,
            "Similarity (%)": best_score,
            "Status": "Possible Match" if best_score < 90 else "High Confidence"
        })

# Export
output_df = pd.DataFrame(results)
output_df.to_excel("output/similarity_report.xlsx", index=False)

print("DONE ✔ Clean report generated in output folder")