import pymongo
import random

store_list = [
    "가츠시 건대점",
    "래빗홀버거컴퍼니",
    "미스터피자 대공원점",
    "백쉐프초밥가게",
    "돈조은날",
    "미가",
    "밀플랜비 서울건국대점",
    "건국갈비",
    "김밥대학라면학과",
    "가람성",
    "주먹구구",
    "원갈비",
    "동궁찜닭",
    "또또떡복이",
    "수내닭꼬치",
    "마늘은약이다보쌈족발 건대점",
    "아미고프란고 건대점",
    "행컵 건대점",
    "마당족발",
    "은혜즉석떡볶이",
    "하남돼지집 세종대점",
    "맛닭꼬 어린이대공원역점",
    "미친피자",
    "206숯불구이",
    "깍뚝",
    "우화등선",
    "고기굽는방앗간 어린이대공원역점",
    "세종김밥떡볶이",
    "이항아",
    "굽네치킨 화양점",
    "청년치킨 건대점",
    "싸다김밥 어린이대공원역점",
    "동경규동 세종대점",
    "인정국물떡볶이 건대점",
    "혜화동돈까스극장 서울화양점",
    "호식이두마리치킨 화양점",
    "화양돈",
    "네네치킨 화양건대점",
    "또봉이통닭 화양점",
    "아라치 군자점",
    "초월식당",
    "모다미육",
    "미식반점",
    "새벽집 군자점",
    "화양리정육식당",
    "1982떡볶이&컵밥",
    "인생족발 건대점",
    "행복한그릇",
    "구름계란덮밥 건대점",
    "도로시파스타 연정건대점",
    "리얼후라이 세종대점",
    "석관동떡볶이 세종대점",
    "얌샘김밥 세종대점",
    "피자스쿨 세종대점",
    "마가을고기",
    "도새기집",
    "더바스켓치킨&떡볶이 세종대점",
    "연이네식당",
    "탱탱보울",
    "맛이차이나",
    "또래끼리",
    "장수마을정육식당",
    "무한정수제돈까스 군자점",
    "석기시대짜장마을",
    "뉴욕떡볶이",
    "BBQ 군자점",
    "밀크밥버거 세종대점",
    "꼬꼬누리 세종대점",
    "디델리 세종대점",
    "손수제치킨",
    "썬더치킨 세종대점",
    "네네치킨 군자송정점",
    "카레당",
    "도미노피자 군자점",
    "파파존스 광진점",
    "돈카와치 어린이대공원점",
    "피자컴퍼니 군자점",
    "이화만두",
    "하오츠",
    "군자돈까스",
    "고봉민김밥인 서울군자점",
    "국대떡볶이 군자역점",
    "송정각",
    "더피자보이즈 광진군자점",
    "돈수작 능동본점",
    "이차돌 군자역점",
    "하남돼지집 군자역점",
    "주돈",
    "마리모",
    "무조건생고기삼겹살",
    "돈토",
    "본전주먹구이",
    "대돈1975",
    "마포구이",
    "한아름분식",
    "굽네치킨 군자점",
    "미로네분식",
    "마포참숯불갈비",
    "꼬밥",
    "60계 서울군자점",
    "써브웨이 세종대점",
    "맥도날드 어린이대공원점",
    "KFC 세종대점",
    "버거킹 군자능동점",
    "써브웨이 군자역점",
    "샐러디 군자역점"
]

client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
restaurant_collection = db["restaurant_table"] # "restaurant_table"이라는 새 컬렉션을 생성합니다.
user_rating_collection = db["user_rating_table"] # "user_rating_table"이라는 새 컬렉션을 생성합니다.


selected_stores = random.sample(store_list, 45)
print(selected_stores)

restaurant_ids = []

# 랜덤 음식점 이름과 name 칼럼을 비교하고, restaurantId를 얻어내기
for store in selected_stores:
    query = {"name": store}
    result = restaurant_collection.find_one(query)
    if result:
        restaurant_ids.append(result["restaurantId"])

print(restaurant_ids)


# 지정한 userId(15~19)
specified_userId = 19

# restaurant_ids를 사용하여 rating 값을 5로 설정
for restaurant_id in restaurant_ids:
    query = {"userId": specified_userId, "restaurantId": restaurant_id}
    new_values = {"$set": {"rating": 5}}
    user_rating_collection.update_one(query, new_values)