# Data Export Template
# ====================
# Use this template when the final deliverable is a data file (CSV, Excel, JSON)
# rather than a formatted document.
#
# Usage:
#   1. Copy this file into a dated subfolder: 4_output/YYYY-MM-DD-description/export.py
#   2. Edit the script to load and combine analyses as needed
#   3. Run: cd 4_output/YYYY-MM-DD-description && python export.py
#
# The golden rule still applies: never hardcode data. Load everything from
# 3_analyses/*/results.json using the helpers.

import sys; sys.path.insert(0, "..")
from helpers import load_analysis, load_value
import pandas as pd
import json

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

OUTPUT_FILE = "export.csv"  # Change extension for .xlsx or .json

# -----------------------------------------------------------------------------
# Load analyses
# -----------------------------------------------------------------------------

# Example: load one or more analyses
# data = load_analysis("value_frequency")
# df = pd.DataFrame(data["results"])

# Example: combine multiple analyses
# freq = load_analysis("value_frequency")
# levels = load_analysis("schein_levels")
# df = pd.merge(
#     pd.DataFrame(freq["results"]),
#     pd.DataFrame(levels["results"]),
#     on="id"
# )

# -----------------------------------------------------------------------------
# Transform (if needed)
# -----------------------------------------------------------------------------

# Example: select/rename columns, compute derived fields, filter rows
# df = df[["col1", "col2", "col3"]]
# df = df.rename(columns={"col1": "Category", "col2": "Count"})
# df["Percentage"] = df["Count"] / df["Count"].sum() * 100

# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------

# Placeholder: replace with your actual DataFrame
df = pd.DataFrame()  # DELETE THIS LINE and uncomment the examples above

if OUTPUT_FILE.endswith(".csv"):
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✓ Exported {len(df)} rows to {OUTPUT_FILE}")

elif OUTPUT_FILE.endswith(".xlsx"):
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✓ Exported {len(df)} rows to {OUTPUT_FILE}")

elif OUTPUT_FILE.endswith(".json"):
    # For JSON, you might want records orientation
    with open(OUTPUT_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)
    print(f"✓ Exported {len(df)} records to {OUTPUT_FILE}")

else:
    raise ValueError(f"Unknown output format: {OUTPUT_FILE}")
