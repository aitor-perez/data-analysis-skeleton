"""Helpers to load analysis results into reports and deliverables."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

REQUIRED_KEYS = {"query", "n_results", "results", "description", "interpretation", "figures"}


def _analyses_path(analyses_dir: str | Path, name: str) -> Path:
    return Path(analyses_dir) / name


def _results_path(analyses_dir: str | Path, name: str) -> Path:
    return _analyses_path(analyses_dir, name) / "results.json"


def validate_results(data: dict, name: str) -> None:
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


def load_analysis(name: str, analyses_dir: str | Path) -> dict:
    """Load results.json from a named analysis subfolder.

    Args:
        name: subfolder name (e.g., "value_frequency").
        analyses_dir: directory containing analysis subfolders (typically the
            project's ``3_analyses`` directory).

    Returns:
        dict with keys: query, n_results, results, description, interpretation, figures.
    """
    p = _results_path(analyses_dir, name)
    if not p.exists():
        raise FileNotFoundError(
            f"Analysis '{name}' not found at {p}. "
            f"Run the analysis script to generate results.json."
        )
    with open(p) as f:
        data = json.load(f)
    validate_results(data, name)
    return data


def load_value(
    name: str,
    column: str,
    analyses_dir: str | Path,
    *,
    agg: str = "first",
) -> int | float | str:
    """Load a single scalar value from an analysis, useful for dashboard value boxes.

    Args:
        name: subfolder name (e.g., "value_frequency").
        column: column name to extract from results.
        analyses_dir: directory containing analysis subfolders.
        agg: aggregation method — "first" (default), "sum", "mean", "min", "max", "count".

    Returns:
        The scalar value (number or string).
    """
    data = load_analysis(name, analyses_dir)
    values = [row[column] for row in data["results"] if column in row]
    n_total = len(data["results"])
    n_found = len(values)
    if not values:
        available = list(data["results"][0].keys()) if data["results"] else "(empty)"
        raise KeyError(
            f"Column '{column}' not found in analysis '{name}'. Available: {available}"
        )
    if n_found < n_total:
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


def load_figure(name: str, fig_name: str, analyses_dir: str | Path) -> str:
    """Return the path to a figure from a named analysis.

    Args:
        name: subfolder name (e.g., "value_frequency").
        fig_name: filename of the figure (e.g., "bar_chart.pdf").
        analyses_dir: directory containing analysis subfolders.

    Returns:
        str path to the figure file.
    """
    p = _analyses_path(analyses_dir, name) / "figures" / fig_name
    if not p.exists():
        raise FileNotFoundError(
            f"Figure '{fig_name}' not found in analysis '{name}' at {p}. "
            f"Run the analysis script to generate the figure."
        )
    return str(p)
