import pymongo
from bson.objectid import ObjectId
client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
restaurant_collection = db["groups_table"] # "restaurant_table"이라는 새 컬렉션을 생성합니다.
user_table = db["user_table"]

cursor = restaurant_collection.find()


user_table.update_many(
    {},
    {
        "$set": {
            "profileImage": "None"
        }
    }
)



'''
#특정 칼럼 타입 변경 코드
for document in cursor:
    your_field_value = document['userId']
    restaurant_collection.update_one({'_id': document['_id']}, {'$set': {'userId': str(your_field_value)}})
'''
'''
#restaurantId 필드를 모든 데이터에 추가하는 코드. 칼럼 순서를 지정할 수도 있음

restaurant_id = 0
for document in cursor:
    new_document = {
        "_id": document["_id"],
        "restaurantId": restaurant_id,
        "name": document["name"],
        "xPosition" : document["xPosition"],
        "yPosition": document["yPosition"],
        "cuisineType" : document["cuisineType"],
        "avgPreference" : document["avgPreference"],
        "address" : document["address"],
        "roadAddress" : document["roadAddress"],
        "number" : document["number"],
        "businessHours" : document["businessHours"],
        "tags" : document["tags"],
        "imageFile" : document["imageFile"]

    }

    restaurant_collection.replace_one({'_id': document['_id']}, new_document)
    restaurant_id += 1
'''