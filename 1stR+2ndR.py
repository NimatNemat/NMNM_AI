from pymongo import MongoClient
import pandas as pd
import numpy as np
client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db2"]
user_table = db['user_table']
restaurant_table = db['restaurant_table']
group_members_table = db['group_members_table']
user_rating_table = db['user_rating_table']
like_table = db['like_table']
review_table = db['review_table']
taste_playlist_restaurants_table = db['taste_playlist_restaurants_table']
restaurant_recommend_table = db['restaurant_recommend_table']


def get_group_members(group_name, user_id):
    return list(group_members_table.find({'groupName': group_name, 'userId': {'$ne': user_id}}))  # 특정 그룹의 모든 멤버 가져오기 (userId를 제외한)


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

def get_like_count(restaurant_id):
    return like_table.count_documents({'restaurantId': restaurant_id})

def get_taste_playlist_count(restaurant_id):
    return taste_playlist_restaurants_table.count_documents({'restaurantId': restaurant_id})

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

def recommend_stores(scored_stores):
    recommended_stores = [{'store_id': store_id,'review_count': count['review_count'],    'sum_ratings': count['sum_ratings'],     'name': get_store_name(store_id),    'like_count': get_like_count(store_id),     'taste_playlist_count': get_taste_playlist_count(store_id)} for store_id, count in scored_stores.items()]

    for store in recommended_stores:
        store['weighted_score'] = calculate_weighted_score(store)

    recommended_stores.sort(key=lambda x: x['weighted_score'], reverse=True)
    return recommended_stores


# 데이터베이스에서 사용자 평점 테이블을 가져오는 함수
def get_user_rating_table():
    client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
    db = client["restaurant_db2"]
    user_rating_table = db["user_rating_table"]
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
    # 예측 끝난 결과를 레스토랑아이디 순서대로 오름차순 정렬하는 코드라 실질적으로 사이트에서 사용할 때는
    # 제외해도 되는 코드인 것 같다. 어차피 예측 평점 순으로 정렬할거니까
    all_ratings.sort_index(inplace=True)

    return all_ratings




# 출력 옵션 설정
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
pd.set_option('display.max_rows', None)

# 모든 사용자의 userId 가져오기
all_user_ids = [user['userId'] for user in user_table.find()]


# 각 사용자에 대해 첫 번째 추천과 두 번째 추천 실행
for user_id in all_user_ids:
    # 해당 사용자가 속한 그룹 찾기
    user_group = group_members_table.find_one({'userId': user_id})
    group_name = user_group['groupName'] if user_group else ""

    group_members = get_group_members(group_name, user_id)  # 그룹 멤버 가져오기
    scored_stores = get_scored_stores(group_members)  # 점수가 매겨진 가게 목록 가져오기
    recommended_stores = recommend_stores(scored_stores)

    scored_stores = get_scored_stores(group_members)  # 점수가 매겨진 가게 목록 가져오기
    recommended_stores = recommend_stores(scored_stores)

    # 첫 번째 추천 결과에서 레스토랑 아이디 가져오기
    first_recommend = [store['store_id'] for store in recommended_stores]

    print("userId:"+user_id)
    for n in first_recommend:
        print(n)

    # 두 번째 추천 결과 실행
    predicted_ratings = predict_user_ratings(user_id)
    predicted_ratings_only = predicted_ratings.dropna(subset=['rating'])
    sorted_predicted_ratings = predicted_ratings_only.sort_values(by='rating', ascending=False)
    second_recommend = sorted_predicted_ratings.index.tolist()

    for n in second_recommend:
        print(n)
    print("-------------------------------------------------------------------")

    # restaurant_recommend_table에 데이터 저장
    # 이전 추천 결과를 찾고, 결과가 없으면 새로운 데이터를 추가하고,
    # 결과가 있으면 firstRecommend, secondRecommend 필드를 업데이트합니다.
    existing_recommendation = restaurant_recommend_table.find_one({'userId': user_id})
    if existing_recommendation:
        restaurant_recommend_table.update_one(
            {'userId': user_id},
            {'$set': {
                'firstRecommend': first_recommend,
                'secondRecommend': second_recommend
            }}
        )
    else:
        restaurant_recommend_table.insert_one({
            'userId': user_id,
            'firstRecommend': first_recommend,
            'secondRecommend': second_recommend
        })




