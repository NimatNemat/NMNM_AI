from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
import numpy as np
from bson import json_util, ObjectId
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")
db = client["restaurant_db2"]
user_table = db['user_table']
user_rating_table = db['user_rating_table']
restaurant_table = db['restaurant_table']
review_table = db['review_table']
taste_playlist_table = db['taste_playlist_table']
groups_table = db['groups_table']


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
def predict_user_ratings_for_third(user_ids,user_rating_table):
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

def predict_user_ratings_for_second(user_id,user_rating_table):
    # 사용자 평점 데이터 불러오기
    user_rating_data = get_user_rating_table(user_rating_table)
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
    # 예측 끝난 결과를 레스토랑아이디 순서대로 오름차순 정렬하는 코드라 실질적으로 사이트에서 사용할 때는
    # 제외해도 되는 코드인 것 같다. 어차피 예측 평점 순으로 정렬할거니까
    all_ratings.sort_index(inplace=True)

    return all_ratings

def get_group_members(group_name):
    return list(user_table.find({'groupName': group_name}))  # 특정 그룹의 모든 멤버 가져오기 (userId를 제외한)


def get_scored_stores(group_members):
    scored_stores = {}

    for member in group_members:
        user_id = member['userId']
        user_ratings = user_rating_table.find({'userId': user_id})

        for user_rating in user_ratings:
            restaurant_id = user_rating['restaurantId']
            rating = user_rating['rating']
            if rating > 0:
                if restaurant_id not in scored_stores:
                    scored_stores[restaurant_id] = {'review_count': 0, 'sum_ratings': 0}
                scored_stores[restaurant_id]['review_count'] += 1
                scored_stores[restaurant_id]['sum_ratings'] += rating

    return scored_stores


def get_store_name(store_id):
    store = restaurant_table.find_one({'restaurantId': store_id})
    return store['name'] if store else None

def get_like_count(restaurant_id, group_name):
    # 같은 그룹의 사용자 목록 가져오기
    same_group_users = user_table.find({'groupName': group_name})

    # 같은 그룹의 사용자 ID 목록 생성
    same_group_user_ids = [user['userId'] for user in same_group_users]

    # 레스토랑의 좋아요를 누른 사용자 목록 가져오기
    restaurant = restaurant_table.find_one({'restaurantId': restaurant_id})
    like_user_list = restaurant.get('likeUserList', []) if restaurant else []

    # 리스트가 None인 경우 빈 리스트로 처리
    if like_user_list is None:
        like_user_list = []

    # 같은 그룹의 사용자들이 좋아요를 누른 횟수 카운트
    like_count = sum([1 for user_id in like_user_list if user_id in same_group_user_ids])

    return like_count




def get_taste_playlist_count(restaurant_id, group_name):
    # 같은 그룹의 사용자 목록 가져오기
    same_group_users = user_table.find({'groupName': group_name})

    # 같은 그룹의 사용자 ID 목록 생성
    same_group_user_ids = [user['userId'] for user in same_group_users]

    # 맛플레이리스트에 레스토랑이 추가된 횟수를 찾기 위해 해당 레스토랑과 같은 그룹의 사용자들이 추가한 경우만 카운트
    taste_playlist_count = 0
    for user_id in same_group_user_ids:
        user_taste_playlists = taste_playlist_table.find({'userId': user_id})
        for taste_playlist in user_taste_playlists:
            taste_playlist_count += sum(1 for entry in taste_playlist['playlistDetail'] if entry[0] == restaurant_id)

    return taste_playlist_count

WEIGHTS = {
    'like_count': 5,
    'avg_rating': 4,
    'taste_playlist_count': 3,
    'review_count': 1
}

def calculate_weighted_score(store):
    avg_rating = store['sum_ratings'] / store['review_count']
    weighted_score = (store['review_count'] * WEIGHTS['like_count']
                      + store['taste_playlist_count'] * WEIGHTS['taste_playlist_count']
                      + avg_rating * WEIGHTS['avg_rating']
                      + store['review_count'] * WEIGHTS['review_count'])
    return weighted_score

def recommend_stores(scored_stores,group_name):
    recommended_stores = [{'store_id': store_id,'review_count': count['review_count'],    'sum_ratings': count['sum_ratings'],     'name': get_store_name(store_id),    'like_count': get_like_count(store_id,group_name),     'taste_playlist_count': get_taste_playlist_count(store_id,group_name)} for store_id, count in scored_stores.items()]

    for store in recommended_stores:
        store['weighted_score'] = calculate_weighted_score(store)

    recommended_stores.sort(key=lambda x: x['weighted_score'], reverse=True)
    return recommended_stores




app = FastAPI()


origins = [
    "http://localhost:3000",  # React 앱을 실행하고 있는 URL
    "http://localhost:8080",  # 필요한 경우 다른 URL 추가
]

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 위에서 정의한 origins를 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post('/thirdRecommend')
async def predict_ratings(user_ids: list[str] = []):

    if not user_ids:
        return {"error": "User IDs are required"}, 400

    predicted_ratings = predict_user_ratings_for_third(user_ids, user_rating_table)
    predicted_ratings_only = predicted_ratings.dropna(subset=['rating'])
    sorted_predicted_ratings = predicted_ratings_only.sort_values(by='rating', ascending=False)
    restaurant_ids = sorted_predicted_ratings.index.tolist()
    # 레스토랑 아이디를 레스토랑 객체로 변환
    recommended_restaurants = [get_restaurant_by_id(restaurant_id) for restaurant_id in restaurant_ids]

    # None 값을 필터링
    recommended_restaurants = [restaurant for restaurant in recommended_restaurants if restaurant is not None]
    # imageUrl 필드 추가
    for restaurant in recommended_restaurants:
        try:
            image_file = restaurant.get("imageFile", None)
            if image_file and isinstance(image_file, ObjectId):
                restaurant["imageUrl"] = f"/images/{str(image_file)}"
            else:
                restaurant["imageUrl"] = None
        except Exception as e:
            print(f"An error occurred while adding imageUrl to restaurant: {e}")
            restaurant["imageUrl"] = None
    return jsonify_with_objectid(recommended_restaurants)




@app.get('/firstRecommendUpdate')
async def firstRecommendUpdate(groupName: str):

    group_members = get_group_members(groupName)  # 그룹 멤버 가져오기
    scored_stores = get_scored_stores(group_members)  # 점수가 매겨진 가게 목록 가져오기
    recommended_stores = recommend_stores(scored_stores, groupName)

    # 첫 번째 추천 결과에서 레스토랑 아이디 가져오기
    first_recommend = [store['store_id'] for store in recommended_stores]
    # 레스토랑 아이디를 레스토랑 객체로 변환
    #first_recommend_restaurants = [get_restaurant_by_id(restaurant_id) for restaurant_id in first_recommend]

    groups_table.update_one(
        {'groupName': groupName},
        {'$set': {
            'firstRecommend': first_recommend,
        }}
    )


@app.get('/secondRecommendUpdate')
async def secondRecommendUpdate(userId: str):
    predicted_ratings = predict_user_ratings_for_second(userId,user_rating_table)
    predicted_ratings_only = predicted_ratings.dropna(subset=['rating'])
    sorted_predicted_ratings = predicted_ratings_only.sort_values(by='rating', ascending=False)
    second_recommend = sorted_predicted_ratings.index.tolist()

    user_table.update_one(
        {'userId': userId},
        {'$set': {
            'secondRecommend': second_recommend
        }}
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost',port=5000)