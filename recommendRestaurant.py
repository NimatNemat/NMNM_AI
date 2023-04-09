from pymongo import MongoClient
client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db2"]
user_table = db['user_table']
restaurant_table = db['restaurant_table']
group_members_table = db['group_members_table']
user_rating_table = db['user_rating_table']
like_table = db['like_table']
review_table = db['review_table']
wishlist_table = db['wishlist_table']
taste_playlist_restaurants_table = db['taste_playlist_restaurants_table']

def get_group_members(group_name):
    return list(group_members_table.find({'groupName': group_name}))  # 특정 그룹의 모든 멤버 가져오기


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

def get_wishlist_count(restaurant_id):
    return wishlist_table.count_documents({'restaurantId': restaurant_id})

def get_taste_playlist_count(restaurant_id):
    return taste_playlist_restaurants_table.count_documents({'restaurantId': restaurant_id})

WEIGHTS = {
    'like_count': 5,
    'avg_rating': 4,
    'wishlist_count': 3.5,
    'taste_playlist_count': 2.5,
    'review_count': 1
}

def calculate_weighted_score(store):
    avg_rating = store['sum_ratings'] / store['review_count']
    weighted_score = (store['review_count'] * WEIGHTS['like_count']
                      + store['wishlist_count'] * WEIGHTS['wishlist_count']
                      + store['taste_playlist_count'] * WEIGHTS['taste_playlist_count']
                      + avg_rating * WEIGHTS['avg_rating']
                      + store['review_count'] * WEIGHTS['review_count'])
    return weighted_score

def recommend_stores(scored_stores):
    recommended_stores = [{'store_id': store_id, 'review_count': count['review_count'], 'sum_ratings': count['sum_ratings'], 'name': get_store_name(store_id), 'like_count': get_like_count(store_id), 'wishlist_count': get_wishlist_count(store_id), 'taste_playlist_count': get_taste_playlist_count(store_id)} for store_id, count in scored_stores.items()]

    for store in recommended_stores:
        store['weighted_score'] = calculate_weighted_score(store)

    recommended_stores.sort(key=lambda x: x['weighted_score'], reverse=True)
    return recommended_stores


num_restaurants = restaurant_table.count_documents({})


group_name = "A"  # 선택한 그룹 ID
group_members = get_group_members(group_name)  # 그룹 멤버 가져오기



for member in group_members:
    print(member)

scored_stores = get_scored_stores(group_members)  # 점수가 매겨진 가게 목록 가져오기
recommended_stores = recommend_stores(scored_stores)

print("Recommended stores for the new user:")
for store in recommended_stores:
    avg_rating = store['sum_ratings'] / store['review_count']
    print(f"{store['name']} (restaurantId: {store['store_id']}, weighted score: {store['weighted_score']:.2f}, review_count: {store['review_count']}, average rating: {avg_rating:.2f}, like count: {store['like_count']},wishlist count: {store['wishlist_count']},taste playlist count: {store['taste_playlist_count']})")

