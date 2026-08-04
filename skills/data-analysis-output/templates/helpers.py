# 4_output/helpers.py
# Helpers to load analysis data in Quarto documents.
#
# Each deliverable lives in a subfolder of 4_output/ (e.g. 2026-02-18-report/).
# Import from a .qmd Python chunk like this:
#
#   import sys; sys.path.insert(0, "..")
#   from helpers import load_analysis, load_figure
#
#   data = load_analysis("value_frequency")
#   fig  = load_figure("value_frequency", "bar_chart.pdf")

import json
from pathlib import Path

ANALYSES_DIR = Path(__file__).resolve().parent.parent / "3_analyses"

REQUIRED_KEYS = {"query", "n_results", "results", "description", "interpretation", "figures"}


def validate_results(data, name):
    """Check that a results.json dict conforms to the expected schema.

    Raises ValueError with a descriptive message if validation fails.
    """
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValueError(
            f"Analysis '{name}/results.json' is missing required keys: {missing}"
        )
    if not isinstance(data["results"], list):
        raise ValueError(
            f"Analysis '{name}/results.json': 'results' must be a list, "
            f"got {type(data['results']).__name__}"
        )
    if data["n_results"] != len(data["results"]):
        raise ValueError(
            f"Analysis '{name}/results.json': 'n_results' is {data['n_results']} "
            f"but 'results' has {len(data['results'])} items"
        )
    if not isinstance(data["figures"], list):
        raise ValueError(
            f"Analysis '{name}/results.json': 'figures' must be a list, "
            f"got {type(data['figures']).__name__}"
        )
    for i, fig in enumerate(data["figures"]):
        for key in ("file", "caption"):
            if key not in fig:
                raise ValueError(
                    f"Analysis '{name}/results.json': figures[{i}] is missing '{key}'"
                )


def load_analysis(name):
    """Load results.json from a named analysis subfolder.

    Args:
        name: subfolder name in 3_analyses/ (e.g., "value_frequency")

    Returns:
        dict with keys: query, n_results, results, description, interpretation, figures
    """
    p = ANALYSES_DIR / name / "results.json"
    if not p.exists():
        raise FileNotFoundError(
            f"Analysis '{name}' not found at {p}. "
            f"Run: cd 3_analyses/{name} && python run.py"
        )
    with open(p) as f:
        data = json.load(f)
    validate_results(data, name)
    return data


def load_value(name, column, agg="first"):
    """Load a single scalar value from an analysis, useful for dashboard value boxes.

    Args:
        name: subfolder name in 3_analyses/ (e.g., "value_frequency")
        column: column name to extract from results
        agg: aggregation method — "first" (default), "sum", "mean", "min", "max", "count"

    Returns:
        The scalar value (number or string)
    """
    data = load_analysis(name)
    values = [row[column] for row in data["results"] if column in row]
    n_total = len(data["results"])
    n_found = len(values)
    if not values:
        raise KeyError(
            f"Column '{column}' not found in analysis '{name}'. "
            f"Available: {list(data['results'][0].keys()) if data['results'] else '(empty)'}"
        )
    if n_found < n_total:
        import warnings
        warnings.warn(
            f"Column '{column}' missing in {n_total - n_found}/{n_total} rows "
            f"of analysis '{name}'. Aggregation uses only {n_found} rows."
        )
    if agg == "first":
        return values[0]
    if agg == "sum":
        return sum(values)
    if agg == "mean":
        return sum(values) / len(values)
    if agg == "min":
        return min(values)
    if agg == "max":
        return max(values)
    if agg == "count":
        return len(values)
    raise ValueError(f"Unknown aggregation '{agg}'. Use: first, sum, mean, min, max, count")


def load_figure(name, fig_name):
    """Return the path to a figure from a named analysis.

    Args:
        name: subfolder name in 3_analyses/ (e.g., "value_frequency")
        fig_name: filename of the figure (e.g., "bar_chart.pdf")

    Returns:
        str path to the figure file
    """
    p = ANALYSES_DIR / name / "figures" / fig_name
    if not p.exists():
        raise FileNotFoundError(
            f"Figure '{fig_name}' not found in analysis '{name}' at {p}. "
            f"Run: cd 3_analyses/{name} && python run.py"
        )
    return str(p)
