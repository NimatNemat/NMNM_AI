import pymongo
import random

store_list = [
    "가츠시 건대점",
    "양분식 건대점",
    "돈조은날",
    "한해",
    "통큰감자탕",
    "타이인플레이트 건대점",
    "화원식당",
    "알촌 건국대점",
    "홍콩정통중국요리",
    "위락밥집",
    "김밥대학라면학과",
    "춘천골닭갈비",
    "왕소구이",
    "원스테이크",
    "주먹구구",
    "또또떡볶이",
    "아미고프란고 건대점",
    "쌍둥이네칼국수",
    "행컵 건대점",
    "하루 건대후문점",
    "시홍쓰",
    "비엣포",
    "우동연가 화양점",
    "왕돈까스왕냉면 세종대점",
    "206숯불구이",
    "본가왕뼈감자탕",
    "고을칼국수",
    "세종원",
    "세종김밥떡볶이",
    "이항아",
    "싸다김밥 어린이대공원역점",
    "순샐러드",
    "이든한끼",
    "아람보리밥국수",
    "철순이네김치찌개",
    "성민식당",
    "미스사이공 세종대점",
    "계절밥상",
    "할매순대국&양선지뼈해장국 세종대점",
    "마가을고기",
    "더바스켓치킨&떡볶이 세종대점",
    "또래끼리",
    "무한정수제돈까스 군자점",
    "춘선만두",
    "석기시대짜장마을",
    "베트남쌀국수",
    "뉴욕떡볶이",
    "디델리 세종대점",
    "마라강호마라탕",
    "썬더치킨 세종대점",
    "카레당",
    "콩심 어린이대공원점",
    "돈카와치 어린이대공원점",
    "이이요",
    "능라도분식",
    "능동타코집",
    "이화만두",
    "하오츠",
    "서울뼈칼국수",
    "해미보쌈순대국",
    "능동국시",
    "돈토",
    "새우공장",
    "미로네분식",
    "세종하늘마루",
    "꼬밥",
    "금성김밥"
]

client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
restaurant_collection = db["restaurant_table"] # "restaurant_table"이라는 새 컬렉션을 생성합니다.
user_rating_collection = db["user_rating_table"] # "user_rating_table"이라는 새 컬렉션을 생성합니다.


selected_stores = random.sample(store_list, 28)
print(selected_stores)

restaurant_ids = []

# 랜덤 음식점 이름과 name 칼럼을 비교하고, restaurantId를 얻어내기
for store in selected_stores:
    query = {"name": store}
    result = restaurant_collection.find_one(query)
    if result:
        restaurant_ids.append(result["restaurantId"])

print(restaurant_ids)


# 지정한 userId(10~14)
specified_userId = 14

# restaurant_ids를 사용하여 rating 값을 5로 설정
for restaurant_id in restaurant_ids:
    query = {"userId": specified_userId, "restaurantId": restaurant_id}
    new_values = {"$set": {"rating": 5}}
    user_rating_collection.update_one(query, new_values)