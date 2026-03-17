from collections import defaultdict
from datetime import datetime
import numpy as np


class TrendAnalysisEngine:

    def __init__(self, db_manager):
        self.db = db_manager

    def trend_by_category(self, period="month"):

        analyses = self.db.get_all_analyses_with_date()
        trend = defaultdict(lambda: defaultdict(int))

        for a in analyses:
            aid = a["id"]
            created = a["created_at"]

            if isinstance(created, str):
                created = datetime.fromisoformat(created)

            if period == "year":
                time_key = created.strftime("%Y")
            elif period == "day":
                time_key = created.strftime("%Y-%m-%d")
            else:
                time_key = created.strftime("%Y-%m")

            cats = self.db.get_category_distribution(aid)

            for cat, freq in cats.items():
                trend[cat][time_key] += freq

        return trend

    def compute_policy_score(self, trend_data):

        scores = {}

        for key, time_series in trend_data.items():
            times = sorted(time_series.keys())
            values = [time_series[t] for t in times]

            if len(values) < 2:
                scores[key] = 0
                continue

            growth = (values[-1] - values[-2]) / (values[-2] + 1e-6)

            mean = np.mean(values)
            std = np.std(values)

            z_score = (values[-1] - mean) / (std + 1e-6)

            score = (0.6 * growth) + (0.4 * z_score)

            scores[key] = float(score)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked