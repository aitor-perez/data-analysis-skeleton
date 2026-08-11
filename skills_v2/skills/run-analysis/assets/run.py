# run.py — Analysis script
# Run from this folder:
#   python run.py

import sys, duckdb, json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

DB_PATH = Path("__DB_PATH__")
Path("figures").mkdir(exist_ok=True)
con = duckdb.connect(str(DB_PATH), read_only=True)

query = """
SELECT *
FROM sample
LIMIT 10
"""
df = con.sql(query).df()

# Optional figure
# fig, ax = plt.subplots(figsize=(8, 5))
# ax.bar(df['col'], df['value'])
# fig.savefig("figures/chart.pdf", bbox_inches="tight")
# plt.close()

output = {
    "query": query.strip(),
    "n_results": len(df),
    "results": df.to_dict(orient="records"),
    "description": "Describe what this analysis does.",
    "interpretation": "Describe what the results mean.",
    "figures": [],
}

with open("results.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"✓ {len(df)} results → results.json")
