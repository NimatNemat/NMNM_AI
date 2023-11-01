import random
import pymongo

store_list = [
    "가츠시 건대점",
    "미가",
    "샘터골 건대본점",
    "건국갈비",
    "춘천골닭갈비",
    "신통치킨 건대점",
    "원스테이크",
    "주먹구구",
    "원갈비",
    "동궁찜닭 건대점",
    "수내닭꼬치",
    "마늘은약이다보쌈족발 건대점",
    "아미고프란고 건대점",
    "하루 건대후문점",
    "마당족발",
    "왕십리정곱창",
    "하남돼지집 세종대점",
    "고향산천 원조숯불닭갈비",
    "맛닭꼬 어린이대공원역점",
    "왕돈까스왕냉면 세종대점",
    "206숯불구이",
    "육회이야기 화양점",
    "깍뚝",
    "우화등선",
    "고기굽는방앗간 어린이대공원역점",
    "치킨처럼 화양점",
    "이항아",
    "굽네치킨 화양점",
    "청년치킨 건대점",
    "육회공작소 세종대점",
    "혜화동돈까스극장 서울화양점",
    "호식이두마리치킨 화양점",
    "화양돈",
    "네네치킨 화양건대점",
    "녹원양꼬치",
    "또봉이통닭 화양점",
    "초월식당",
    "아라치 군자점",
    "모다미육",
    "본토고기구이",
    "새벽집 군자점",
    "오태식해바라기치킨 세종대점",
    "빅베어8",
    "수숯불직화꼬치 세종대점",
    "화양리정육식당",
"수돈재감자탕 화양점",
    "마가을고기",
    "도새기집",
    "더바스켓치킨&떡볶이 세종대점",
    "옥돌바베큐",
    "푸라닭치킨 군자점",
    "60계 서울군자점",
    "플라잉꼬꼬 군자점",
    "장안참나무 숯불갈비전문점",
    "세종하늘마루",
    "마포참숯불갈비",
    "버릴게없소",
    "굽네치킨 군자점",
    "호재래양꼬치",
    "막내막창",
    "마포구이",
    "라운지앤",
    "미친곱창",
    "대돈1975",
    "본전주먹구이",
    "돈토",
    "전통춘천닭갈비",
    "무조건생고기삼겹살",
    "마리모",
    "마왕족발 군자역점",
    "가미정",
    "주돈",
    "하남돼지집 군자역점",
    "이차돌 군자역점",
    "세광양대창 군자점",
    "돈수작 능동본점",
    "대명소곱창",
    "군자대한곱창 본점",
    "용식당",
    "군자돈까스",
    "참맛옛날통닭",
    "맵당 군자점",
    "정원(정원마늘보쌈)",
    "돈카와치 어린이대공원점",
    "호세야오리바베큐 군자점",
    "네네치킨 군자송정점",
    "썬더치킨 세종대점",
    "곱창하우스",
    "손수제치킨",
    "채움솥뚜껑생삼겹살",
    "꼬꼬누리 세종대점",
    "BBQ 군자점",
    "무한정수제돈까스 군자점",
    "장수마을정육식당",
    "곱창골",
    "연이네식당",
    "장수왕족발",
    "아랫목식당",
    "KFC 세종대"]


client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
restaurant_collection = db["restaurant_table"] # "restaurant_table"이라는 새 컬렉션을 생성합니다.
user_rating_collection = db["user_rating_table"] # "user_rating_table"이라는 새 컬렉션을 생성합니다.


selected_stores = random.sample(store_list, 40)
print(selected_stores)

restaurant_ids = []

# 랜덤 음식점 이름과 name 칼럼을 비교하고, restaurantId를 얻어내기
for store in selected_stores:
    query = {"name": store}
    result = restaurant_collection.find_one(query)
    if result:
        restaurant_ids.append(result["restaurantId"])

print(restaurant_ids)


# 지정한 userId(0~4)
specified_userId = "0"

# restaurant_ids를 사용하여 rating 값을 5로 설정
for restaurant_id in restaurant_ids:
    query = {"userId": specified_userId, "restaurantId": restaurant_id}
    new_values = {"$set": {"rating": 5}}
    user_rating_collection.update_one(query, new_values)
