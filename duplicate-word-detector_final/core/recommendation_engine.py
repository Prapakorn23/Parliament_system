print("Recommendation Engine Loaded")

import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity


class HybridRecommendationEngine:

    def __init__(self, db_manager, alpha=0.7, beta=0.3):
        self.db = db_manager
        self.alpha = alpha
        self.beta = beta

    def combine_vectors(self, keyword_vec, category_vec):
        combined = defaultdict(float)

        for k, v in keyword_vec.items():
            combined[f"kw_{k}"] += self.alpha * v

        for k, v in category_vec.items():
            combined[f"cat_{k}"] += self.beta * v

        return combined

    def vector_to_numpy(self, vector_dict, feature_space):
        return np.array([vector_dict.get(f, 0) for f in feature_space])

    def recommend(self, target_analysis_id, top_n=5):

        all_ids = self.db.get_all_analysis_ids()

        target_kw = self.db.get_word_frequencies(target_analysis_id)
        target_cat = self.db.get_category_distribution(target_analysis_id)

        target_vec = self.combine_vectors(target_kw, target_cat)

        feature_space = set(target_vec.keys())
        all_vectors = {}

        for aid in all_ids:
            kw = self.db.get_word_frequencies(aid)
            cat = self.db.get_category_distribution(aid)
            vec = self.combine_vectors(kw, cat)

            all_vectors[aid] = vec
            feature_space.update(vec.keys())

        feature_space = list(feature_space)

        target_np = self.vector_to_numpy(target_vec, feature_space).reshape(1, -1)

        scores = []

        for aid, vec in all_vectors.items():
            if aid == target_analysis_id:
                continue

            vec_np = self.vector_to_numpy(vec, feature_space).reshape(1, -1)
            score = cosine_similarity(target_np, vec_np)[0][0]
            scores.append((aid, float(score)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
