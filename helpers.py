from itertools import permutations
import pandas as pd

from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def outersection(*pd_series):
    checks_idx = permutations(range(len(pd_series)), 2)
    diffs = []

    for idx_0, idx_1 in checks_idx:
        set_0 = set(pd_series[idx_0])
        set_1 = set(pd_series[idx_1])
        difference = set_0 - set_1
        if difference:
            columns = ["In this series", "but not in this", "difference"]
            data = [(idx_0, idx_1, row) for row in difference]
            diff = pd.DataFrame(data=data, columns=columns)
            diffs.append(diff)

    if diffs:
        return pd.concat(diffs, ignore_index=True)
    else:
        return None


def similiar_outersections(pd_outersection, scorer=fuzz.partial_ratio):
    diffs = [
        pd_outersection[pd_outersection["In this series"] == idx]
        for idx in pd_outersection["In this series"].unique()
    ]

    suggestions = []
    for diff_idx, diff in enumerate(diffs):
        series_idx = diff["but not in this"].tolist()
        for row_idx, row_series_idx in enumerate(series_idx):
            name = diff.iloc[row_idx]["difference"]
            names_outersection = diffs[row_series_idx]["difference"].tolist()
            suggestion = process.extractOne(
                name, names_outersection, scorer=scorer)
            suggestions.append(suggestion[0])

    return suggestions