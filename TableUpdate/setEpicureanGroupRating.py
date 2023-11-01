import pymongo
import random

store_list = ["래빗홀버거컴퍼니", "백쉐프초밥가게", "the개미 건대본점", "미가", "밀플랜비 서울건국대점", "길이식당 건대본점", "진성가야지", "시홍쓰", "뱃놈", "알고",
              "주꾸미 신", "빠오즈푸", "깍뚝", "내담 세종대점", "시멘트서울", "순샐러드", "봉쉐프참치포차", "녹원양꼬치", "가네초밥", "망향비빔국수 화양점",
              "버텍스 건대점", "초월식당", "모다미육", "본토고기구이", "미식반점", "화양리정육식당", "본래순대 화양점", "굴업도막회", "달문식당", "백순대본가새맛 군자점",
              "스시붐", "행복한그릇", "씨즐레스토랑", "구름계란덮밥 건대점", "도로시파스타 연정건대점", "수숯불직화꼬치 세종대점", "마가을고기", "도새기집", "송정국수",
              "아랫목식당", "탱탱보울", "곱창골", "송미당", "삼삼불닭발", "춘선만두", "디델리 세종대점", "마라강호마라탕", "미건테이블", "라뮤즈", "소사면옥", "카레당",
              "진한방삼계탕 군자점", "돈카와치 어린이대공원점", "이이요", "피자컴퍼니 군자점", "정원", "사사로운", "어머이밥상", "참맛옛날통닭", "이화만두",
              "잉글사이드 군자본점", "군자돈까스", "중앙식당", "송정각", "더피자보이즈 광진군자점", "용식당", "행운식당","대명소곱창", "돈수작 능동본점", "천미천훠궈",
              "파쏘", "광나루유황오리주물럭", "LAB41", "피슈마라홍탕 군자역점", "주돈", "가미정", "고메", "스시교센", "영미오리탕 군자점", "기와집 본점", "마리모", "대돈1975",
              "미친곱창", "라운지앤", "차이나유", "마포구이", "유미마라탕", "e참치세상 군자점", "막내막창", "굴마을낙지촌 군자점", "호재래양꼬치", "온미", "버릴게없소", "세종하늘마루",
              "국수사랑채", "수비드김치찜", "삼거리닭발", "신봉닭발", "열봉이 군자점", "천호용궁알탕 광진점"]


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


# 지정한 userId(20~24)
specified_userId = 24

# restaurant_ids를 사용하여 rating 값을 5로 설정
for restaurant_id in restaurant_ids:
    query = {"userId": specified_userId, "restaurantId": restaurant_id}
    new_values = {"$set": {"rating": 5}}
    user_rating_collection.update_one(query, new_values)