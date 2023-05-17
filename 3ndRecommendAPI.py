from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
import numpy as np
from bson import json_util
import json
from fastapi import FastAPI, Request

client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")
db = client["restaurant_db2"]
user_table = db['user_table']
user_rating_table = db['user_rating_table']
restaurant_table = db['restaurant_table']



def jsonify_with_objectid(data):
    return json.loads(json_util.dumps(data))


# 데이터베이스에서 사용자 평점 테이블을 가져오는 함수
def get_user_rating_table(user_rating_table):
    data = []
    for row in user_rating_table.find():
        data.append(row)
    return data

# 코사인 유사도를 계산하는 함수
def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0

    return np.dot(a, b) / (norm_a * norm_b)

def get_restaurant_by_id(restaurant_id):
    restaurant = restaurant_table.find_one({'restaurantId': restaurant_id})
    if restaurant is None:
        return {"error": f"Could not find restaurant with id {restaurant_id}"}
    else:
        return restaurant


def create_new_user_ratings(user_ids, user_rating_table):
    user_rating_data = get_user_rating_table(user_rating_table)
    ratings_df = pd.DataFrame(user_rating_data)
    user_restaurant_matrix = ratings_df.pivot_table(index='userId', columns='restaurantId', values='rating',
                                                    fill_value=0)

    selected_users = user_restaurant_matrix.loc[user_ids]
    rating_counts = selected_users.astype(bool).sum(axis=0)
    rating_sum = selected_users.sum(axis=0)

    min_count = round(len(user_ids) / 2)
    avg_ratings = rating_sum.where(rating_counts >= min_count, 0) / rating_counts.where(rating_counts >= min_count, 1)

    # 집합 인원수의 절반에 반올림한 값 이상의 인원 수가 각 레스토랑에 대해서 평점을 매긴 경우만 평균값으로 계산
    valid_avg_ratings = avg_ratings.where(rating_counts >= min_count, 0)

    return valid_avg_ratings


# 사용자 평점을 예측하는 함수
def predict_user_ratings(user_ids,user_rating_table):
    # 사용자 평점 데이터 불러오기
    new_user_ratings = create_new_user_ratings(user_ids, user_rating_table)
    user_rating_data = get_user_rating_table(user_rating_table)
    ratings_df = pd.DataFrame(user_rating_data)

    # 사용자-음식점 행렬 만들기
    user_restaurant_matrix = ratings_df.pivot_table(index='userId', columns='restaurantId', values='rating', fill_value=0)

    new_user_ratings.name = "new_user"
    user_restaurant_matrix = pd.concat([user_restaurant_matrix, pd.DataFrame(new_user_ratings).T], axis=0)

    # 유사도 행렬 계산
    similarity_matrix = user_restaurant_matrix.apply(
        lambda row: cosine_similarity(row, user_restaurant_matrix.loc["new_user"]), axis=1)

    # 유사도 행렬에서 대상 사용자 제거
    similarity_matrix.drop(user_ids+["new_user"], inplace=True)

    unrated_restaurants = new_user_ratings[new_user_ratings == 0].index

    # 평가하지 않은 음식점에 대한 평점 예측
    predicted_ratings = []
    for restaurant in unrated_restaurants:
        # 유사한 사용자들의 평점 가중 평균 구하기
        ratings_from_similar_users = user_restaurant_matrix.loc[similarity_matrix.index, restaurant]
        weighted_ratings = ratings_from_similar_users * similarity_matrix
        predicted_rating = weighted_ratings.sum() / np.abs(similarity_matrix).sum()
        predicted_ratings.append((restaurant, predicted_rating))

    # 원래 평점과 예측 평점 결합
    predicted_ratings_df = pd.DataFrame(predicted_ratings, columns=['restaurantId', 'rating']).set_index('restaurantId')
    all_ratings = pd.concat([new_user_ratings[new_user_ratings != 0], predicted_ratings_df], axis=0)

    # 결합된 평점을 음식점 인덱스로 정렬
    # 예측 끝난 결과를 레스토랑아이디 순서대로 오름차순 정렬하는 코드라 실질적으로 사이트에서 사용할 때는
    # 제외해도 되는 코드인 것 같다. 어차피 예측 평점 순으로 정렬할거니까
    all_ratings.sort_index(inplace=True)

    return all_ratings






app = FastAPI()

@app.post('/thirdRecommend')
async def predict_ratings(request: Request):
    json_data = await request.json()
    user_ids = json_data.get('user_ids', [])

    if not user_ids:
        return {"error": "User IDs are required"}, 400

    predicted_ratings = predict_user_ratings(user_ids, user_rating_table)
    predicted_ratings_only = predicted_ratings.dropna(subset=['rating'])
    sorted_predicted_ratings = predicted_ratings_only.sort_values(by='rating', ascending=False)
    restaurant_ids = sorted_predicted_ratings.index.tolist()

    # 레스토랑 아이디를 레스토랑 객체로 변환
    recommended_restaurants = [get_restaurant_by_id(restaurant_id) for restaurant_id in restaurant_ids]

    # None 값을 필터링
    recommended_restaurants = [restaurant for restaurant in recommended_restaurants if restaurant is not None]

    return jsonify_with_objectid(recommended_restaurants), 200


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='3.39.232.5', port=5000)
