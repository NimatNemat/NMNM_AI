import pandas as pd
from pymongo import MongoClient
import numpy as np

# 데이터베이스에서 사용자 평점 테이블을 가져오는 함수
def get_user_rating_table():
    client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
    db = client["restaurant_db2"]
    user_rating_table = db["user_rating_table"]
    data = []
    for row in user_rating_table.find():
        data.append(row)
    return data
#hello
# 코사인 유사도를 계산하는 함수
def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0

    return np.dot(a, b) / (norm_a * norm_b)

# 사용자 평점을 예측하는 함수
def predict_user_ratings(user_id):
    # 사용자 평점 데이터 불러오기
    user_rating_data = get_user_rating_table()
    ratings_df = pd.DataFrame(user_rating_data)

    # 사용자-음식점 행렬 만들기
    user_restaurant_matrix = ratings_df.pivot_table(index='userId', columns='restaurantId', values='rating', fill_value=0)

    # 유사도 행렬 계산
    similarity_matrix = user_restaurant_matrix.apply(
        lambda row: cosine_similarity(row, user_restaurant_matrix.loc[user_id]), axis=1)

    # 유사도 행렬에서 대상 사용자 제거
    similarity_matrix.drop(user_id, inplace=True)

    # 주어진 사용자가 평가하지 않은 음식점 찾기
    target_user_ratings = user_restaurant_matrix.loc[user_id]
    unrated_restaurants = target_user_ratings[target_user_ratings == 0].index

    # 평가하지 않은 음식점에 대한 평점 예측
    predicted_ratings = []
    for restaurant in unrated_restaurants:
        # 유사한 사용자들의 평점 가중 평균 구하기
        ratings_from_similar_users = user_restaurant_matrix.loc[similarity_matrix.index, restaurant]
        weighted_ratings = ratings_from_similar_users * similarity_matrix
        predicted_rating = weighted_ratings.sum() / np.abs(similarity_matrix).sum()
        predicted_ratings.append((restaurant, predicted_rating))

    # 원래 평점과 예측 평점 결합
    original_ratings = target_user_ratings[target_user_ratings != 0]
    predicted_ratings_df = pd.DataFrame(predicted_ratings, columns=['restaurantId', 'rating']).set_index('restaurantId')
    all_ratings = pd.concat([original_ratings, predicted_ratings_df], axis=0)

    # 결합된 평점을 음식점 인덱스로 정렬
    all_ratings.sort_index(inplace=True)

    return all_ratings

# 출력 옵션 설정
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
pd.set_option('display.max_rows', None)

# 사용자 ID 설정
your_user_id = "0"
# 사용자 ID를 변경하여 평점을 예측하려는 사용자에 대해 예측 수행
predicted_ratings = predict_user_ratings(your_user_id)
print(predicted_ratings)
print("------------------------------------------")

# 원래 평점이 있는 음식점 제거 (예측 평점에 NaN인 경우)
predicted_ratings_only = predicted_ratings.dropna(subset=['rating'])

# 예측 평점으로 정렬 (내림차순)
sorted_predicted_ratings = predicted_ratings_only.sort_values(by='rating', ascending=False)

print(sorted_predicted_ratings)
print("------------------------------------------")

# 예측 평점이 0인 음식점 제거
filtered_predicted_ratings = sorted_predicted_ratings[sorted_predicted_ratings['rating'] > 0]

# 필터링하고 정렬된 예측 평점 출력
print(filtered_predicted_ratings)

