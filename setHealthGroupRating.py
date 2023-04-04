import pymongo
import random

store_list = [
    "순샐러드",
    "진성가야지",
    "위락밥집",
    "건우식당",
    "화양식당",
    "이든한끼",
    "아람보리밥국수",
    "본죽 화양사거리점",
    "철순이네김치찌개 군자점",
    "성민식당",
    "계절밥상",
    "광주식당",
    "공주식당",
    "국수사랑채",
    "장원칼국수",
    "온미",
    "기와집 본점",
    "영미오리탕 군자점",
    "광나루유황오리주물럭",
    "행운식당",
    "서울뼈칼국수",
    "본죽 군자역점",
    "중앙식당",
    "순애식당",
    "어머이밥상",
    "콩심 어린이대공원점",
    "진한방삼계탕 군자점",
    "미건테이블",
    "감천식당",
    "짱돌",
    "고을칼국수",
    "써브웨이 세종대점",
    "샐러디 군자역점"
]

client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
restaurant_collection = db["restaurant_table"] # "restaurant_table"이라는 새 컬렉션을 생성합니다.
user_rating_collection = db["user_rating_table"] # "user_rating_table"이라는 새 컬렉션을 생성합니다.


selected_stores = random.sample(store_list, 18)
print(selected_stores)

restaurant_ids = []

# 랜덤 음식점 이름과 name 칼럼을 비교하고, restaurantId를 얻어내기
for store in selected_stores:
    query = {"name": store}
    result = restaurant_collection.find_one(query)
    if result:
        restaurant_ids.append(result["restaurantId"])

print(restaurant_ids)


# 지정한 userId(5~9)
specified_userId = 9

# restaurant_ids를 사용하여 rating 값을 5로 설정
for restaurant_id in restaurant_ids:
    query = {"userId": specified_userId, "restaurantId": restaurant_id}
    new_values = {"$set": {"rating": 5}}
    user_rating_collection.update_one(query, new_values)