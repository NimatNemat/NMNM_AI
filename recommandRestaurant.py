from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
user_table = db['user_table']
restaurant_table = db['restaurant_table']
group_members_table = db['group_members_table']
user_rating_table = db['user_rating_table']



def add_new_user():
    new_user_info = {
        'userId' : 'New Id',
        'userName': 'New User',
        'age': 25,
        'gender': 'M',
        'password': 'password123',
        'nickName': 'Newbie',
        'phoneNumber': '123-456-7890',
        'eMail': 'newuser@example.com'
    }
    result = user_table.insert_one(new_user_info)  # 새로운 유저 정보를 user_table에 추가
    return result.inserted_id


def join_group(user_id, group_name):
    group_members_table.insert_one({'userId': str(user_id), 'groupId': group_name})  # 유저를 그룹에 추가


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
                scored_stores[restaurant_id] = scored_stores.get(restaurant_id, 0) + 1  # 점수가 매겨진 가게 카운트

    return scored_stores  # 점수가 매겨진 가게 목록 반환


def get_store_name(store_id):
    store = restaurant_table.find_one({'restaurantId': store_id})
    return store['name'] if store else None


def recommend_stores(scored_stores):
    sorted_stores = sorted(scored_stores.items(), key=lambda x: x[1], reverse=True)
    recommended_stores = [{'store_id': store_id, 'count': count, 'name': get_store_name(store_id)} for store_id, count in sorted_stores]
    return recommended_stores

def generate_individual_user_ratings(user_id,num_restaurants):
    ratings = []
    for restaurant_id in range(num_restaurants):
        rating = {
            "userId": user_id,
            "restaurantId": restaurant_id,
            "rating" : 0
            #"rating": random.choice([0, 1, 2, 3, 4, 5])
        }
        ratings.append(rating)
    return ratings

num_restaurants = restaurant_table.count_documents({})

new_user_id = add_new_user()  # 새 유저 추가

document = user_table.find_one({'_id': new_user_id})
user_id = document['userId']
individual_user_ratings = generate_individual_user_ratings(user_id, num_restaurants)
group_name = "A"  # 선택한 그룹 ID
join_group(user_id, group_name)  # 그룹에 가입
group_members = get_group_members(group_name)  # 그룹 멤버 가져오기




for individual_user_rating in individual_user_ratings:
    user_rating_table.insert_one(individual_user_rating)

for member in group_members:
    print(member)

scored_stores = get_scored_stores(group_members)  # 점수가 매겨진 가게 목록 가져오기
recommended_stores = recommend_stores(scored_stores)

print("Recommended stores for the new user:")
for store in recommended_stores:
    print(f"{store['name']} (restaurantId: {store['store_id']}, count: {store['count']})")