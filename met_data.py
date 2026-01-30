"""
MET (Metabolic Equivalent of Task) data from the Compendium of Physical Activities.
Loads assets/met.csv into memory for activity suggestions and calorie estimates.
Uses CSV directly (no SQLite) so the data is easy to update by replacing the file.
"""
import csv
import os
import sys
from difflib import get_close_matches

# In-memory cache of MET activities: list of dicts with keys description, activity, met, code
_met_activities = None


def _get_met_csv_path():
    """Resolve path to assets/met.csv, for both script and PyInstaller .exe."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", "met.csv")


def load_met_activities():
    """
    Load MET activities from assets/met.csv into memory.
    Returns list of dicts: {description, activity, met, code}.
    """
    global _met_activities
    if _met_activities is not None:
        return _met_activities
    path = _get_met_csv_path()
    if not os.path.exists(path):
        _met_activities = []
        return _met_activities
    activities = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                met_val = float(row["MET"])
            except (ValueError, KeyError):
                continue
            description = (row.get("Description") or "").strip()
            activity = (row.get("Actvitiy") or "").strip()  # CSV typo preserved
            code = (row.get("Code") or "").strip()
            if description:
                activities.append({
                    "description": description,
                    "activity": activity,
                    "met": met_val,
                    "code": code,
                })
    _met_activities = activities
    return _met_activities


def search_met_activities(query, limit=10):
    """
    Search MET activities by description and category.
    Prefers substring matches (query appears in text); falls back to fuzzy match if none.
    Returns list of dicts with keys description, activity, met, code.
    """
    activities = load_met_activities()
    if not activities or not (query or "").strip():
        return []
    query = query.strip().lower()
    # 1) Substring match: query appears in description or activity (e.g. "swimming" in "Swimming, crawl, ...")
    searchable = [
        (a["description"].lower(), (a["activity"] or "").lower(), a)
        for a in activities
    ]
    substring_matches = []
    for desc_lower, act_lower, a in searchable:
        if query in desc_lower or query in act_lower:
            substring_matches.append(a)
    if substring_matches:
        # Prefer descriptions that start with the query, then the rest
        def rank_key(a):
            d = a["description"].lower()
            return (0 if d.startswith(query) else 1, d)
        substring_matches.sort(key=rank_key)
        return substring_matches[:limit]
    # 2) Fallback: fuzzy match on full searchable text
    names = [desc + " " + act for desc, act, _ in searchable]
    matches = get_close_matches(query, names, n=limit, cutoff=0.35)
    seen = set()
    result = []
    for m in matches:
        idx = names.index(m)
        a = searchable[idx][2]
        key = (a["description"], a["met"])
        if key not in seen:
            seen.add(key)
            result.append(a)
    return result[:limit]
