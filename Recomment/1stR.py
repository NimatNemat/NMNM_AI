from pymongo import MongoClient
import pandas as pd
client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db2"]
user_table = db['user_table']
restaurant_table = db['restaurant_table']
user_rating_table = db['user_rating_table']
review_table = db['review_table']
taste_playlist_table = db['taste_playlist_table']
groups_table = db['groups_table']


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


# 모든 사용자의 userId 가져오기
all_user_ids = [user['userId'] for user in user_table.find()]
all_group_names = [group['groupName'] for group in groups_table.find()]

# 각 사용자에 대해 첫 번째 추천과 두 번째 추천 실행
for group_name in all_group_names:

    group_members = get_group_members(group_name)  # 그룹 멤버 가져오기
    scored_stores = get_scored_stores(group_members)  # 점수가 매겨진 가게 목록 가져오기
    recommended_stores = recommend_stores(scored_stores,group_name)

    # 첫 번째 추천 결과에서 레스토랑 아이디 가져오기
    first_recommend = [store['store_id'] for store in recommended_stores]


    print("groupName:"+group_name)
    for n in first_recommend:
        print(n)

    groups_table.update_one(
        {'groupName': group_name},
        {'$set': {
            'firstRecommend': first_recommend,
        }}
    )





