import pymongo
import random
from datetime import datetime, timedelta
client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db2"]
restaurant_table = db["restaurant_table"]

fields_to_check = ["address", "roadAddress", "number", "businessHours", "tags", "imageFile"]

# 모든 레스토랑 문서를 순회하며 필드 값을 확인하고 필요한 경우 업데이트합니다.
for restaurant in restaurant_table.find():
    update_fields = {}

    for field in fields_to_check:
        if restaurant[field] == "None":
            update_fields[field] = None

    if update_fields:
        restaurant_table.update_one(
            {'_id': restaurant["_id"]},
            {'$set': update_fields}
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