import pymongo

client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
user_rating_collection = db["user_rating_table"] # "user_rating_table"이라는 새 컬렉션을 생성합니다.



# 특정 restaurantId 선택
specified_userId = "0"


query = {"userId": specified_userId}

# rating 칼럼 값을 0으로 설정
new_values = {"$set": {"rating": 0}}

# update_many()를 사용하여 해당 restaurantId를 가지는 모든 문서의 rating 값을 0으로 설정
user_rating_collection.update_many(query, new_values)
