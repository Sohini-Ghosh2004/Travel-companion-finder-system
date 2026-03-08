#!/usr/bin/python3


'''

  """ ML model for recommending users with similar interest in travel """



Content-based	        -->         User profile features (age, budget, style)
Collaborative filtering	-->         User–POI rating matrix
Geo similarity	        -->         Latitude + longitude



[import]:

from recommender import TravelRecommender
recommender = TravelRecommender()
results = recommender.recommend(user_id = 69, top_n = 10)

'''


import pandas as pd
import numpy as np
import mysql.connector
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from geopy.distance import geodesic


class TravelRecommender:

    def __init__(self):
        self.scaler = MinMaxScaler()

        self.users_df = None
        self.ratings_df = None

        self.content_similarity_matrix = None
        self.cf_similarity_matrix = None
        self.cf_user_index_map = None

        self.w_content = 0
        self.w_cf = 0
        self.w_geo = 0


    
    def _get_connection(self):
        return mysql.connector.connect(host = "localhost", user = "user", password = "1234!", database = "travel")


    
    def _load_data(self):
        conn = self._get_connection()

        # pandas dataframe
        # self.users_df = pd.read_excel(self.file_path, sheet_name="users")
        # self.ratings_df = pd.read_excel(self.file_path, sheet_name="poi_ratings")

        self.users_df = pd.read_sql(""" SELECT u.*, d.latitude, d.longitude FROM users u LEFT JOIN destination d ON u.destination_id = d.destination_id """, conn)
        self.ratings_df = pd.read_sql(""" SELECT * FROM ratings """, conn)

        conn.close()

        # fix for new user uuid
        self.users_df["user_id"] = self.users_df["user_id"].astype(str)
        self.ratings_df["user_id"] = self.ratings_df["user_id"].astype(str)

        if self.users_df.empty:
            raise ValueError("No users found in database")


    # pipeline >w<
    def _build_model(self):
        self._build_content_model()
        self._build_clustering()
        self._build_collaborative_model()
        self._compute_dynamic_weights()


    # # content based model
    def _build_content_model(self):
        # features = self.users_df.drop(columns=["id", "latitude", "longitude"], errors="ignore")
        features = self.users_df.drop(columns=["user_id", "destination_id", "latitude", "longitude", "cluster"], errors="ignore")

        # keep only numeric columns
        features = features.select_dtypes(include=[np.number])

        features_scaled = self.scaler.fit_transform(features)
        self.content_similarity_matrix = cosine_similarity(features_scaled)


    # K Means Clustering
    def _build_clustering(self):
        # features = self.users_df.drop(columns=["id", "latitude", "longitude"], errors="ignore")
        features = self.users_df.drop(columns=["user_id", "destination_id", "latitude", "longitude", "cluster"], errors="ignore")

        # keep only numeric columns
        features = features.select_dtypes(include=[np.number])

        scaled = self.scaler.transform(features)
        k = max(2, int(np.sqrt(len(self.users_df) / 2)))
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        self.users_df["cluster"] = kmeans.fit_predict(scaled)


    # collaborative filtering
    def _build_collaborative_model(self):
        if self.ratings_df.empty:
            self.cf_similarity_matrix = None
            self.cf_user_index_map = {}
            return

        self.ratings_df["avg_rating"] = self.ratings_df[["rating_food", "rating_safety", "rating_fun"]].mean(axis=1)
        user_item_matrix = self.ratings_df.pivot_table(index="user_id",columns="poi_id",values="avg_rating").fillna(0)
        self.cf_similarity_matrix = cosine_similarity(user_item_matrix)
        self.cf_user_index_map = {user_id: idx for idx, user_id in enumerate(user_item_matrix.index)}


    def _geo_similarity(self, idx1, idx2):

        # handle null value
        if pd.isna(self.users_df.loc[idx1, "latitude"]) or pd.isna(self.users_df.loc[idx2, "latitude"]):
            return 0

        coord1 = ( self.users_df.loc[idx1, "latitude"], self.users_df.loc[idx1, "longitude"])
        coord2 = ( self.users_df.loc[idx2, "latitude"], self.users_df.loc[idx2, "longitude"])

        distance_km = geodesic(coord1, coord2).km

        return 1 / (1 + distance_km)


    
    def _compute_dynamic_weights(self):

        content_var = np.var(self.content_similarity_matrix)

        cf_var = np.var(self.cf_similarity_matrix) if self.cf_similarity_matrix is not None else 0

        geo_samples = [
            self._geo_similarity(i, i + 1)
            for i in range(min(5, len(self.users_df) - 1))
        ]

        geo_var = np.var(geo_samples)

        total = content_var + cf_var + geo_var

        if total == 0:
            self.w_content = self.w_cf = self.w_geo = 0
        else:
            self.w_content = content_var / total
            self.w_cf = cf_var / total
            self.w_geo = geo_var / total


    
    def _hybrid_score(self, user_idx, other_idx):

        content_score = self.content_similarity_matrix[user_idx][other_idx]

        user_id = self.users_df.loc[user_idx, "user_id"]
        other_id = self.users_df.loc[other_idx, "user_id"]

        # CF score
        if (
            self.cf_similarity_matrix is not None and
            user_id in self.cf_user_index_map and
            other_id in self.cf_user_index_map
        ):
            cf_idx1 = self.cf_user_index_map[user_id]
            cf_idx2 = self.cf_user_index_map[other_id]
            cf_score = self.cf_similarity_matrix[cf_idx1][cf_idx2]
        else:
            cf_score = 0

        geo_score = self._geo_similarity(user_idx, other_idx)

        cluster_score = 1 if (
            self.users_df.loc[user_idx, "cluster"] ==
            self.users_df.loc[other_idx, "cluster"]
        ) else 0

        final_score = ( self.w_content * content_score + self.w_cf * cf_score + self.w_geo * geo_score + 0.1 * cluster_score )

        return final_score



    # recommend top n users (default 5)
    def recommend(self, user_id, top_n=5):
        self._load_data()
        self._build_model()

        if user_id not in self.users_df["user_id"].values:
            raise ValueError("User ID not found")

        user_idx = self.users_df.index[self.users_df["user_id"] == user_id][0]

        scores = []

        for idx in range(len(self.users_df)):
            if idx == user_idx:
                continue

            score = self._hybrid_score(user_idx, idx)

            scores.append({
                "user_id": str(self.users_df.loc[idx, "user_id"]),          # change
                "score": float(score)
            })

        scores = sorted(scores, key=lambda x: x["score"], reverse=True)

        return scores[:top_n]