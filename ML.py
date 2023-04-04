import pandas as pd
import matplotlib.pyplot as plt
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from surprise import accuracy
from sklearn.cluster import KMeans
import pymongo

# 사용자별로 음식점 평가 데이터를 가져옵니다.
def get_user_rating_table():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["restaurant_db"]
    user_rating_table = db["user_rating_table"]
    data = []
    for row in user_rating_table.find():
        data.append(row)
    return data

# 사용자별로 평가하지 않은 음식점 목록을 가져옵니다.
def get_zero_rated_restaurants(user_rating_data, user_id, restaurants):
    zero_rated_restaurants = set(row["restaurant_id"] for row in user_rating_data if row["user_id"] == user_id and row["rating"] == 0)
    return zero_rated_restaurants

# 사용자별로 평가하지 않은 음식점에 대한 예측 평점을 계산합니다.
def predict_unrated_restaurants(algo, user_zero_rated_restaurants):
    predictions = []
    for user, zero_rated_restaurants in user_zero_rated_restaurants.items():
        for restaurant in zero_rated_restaurants:
            pred = algo.predict(user, restaurant)
            predictions.append([user, restaurant, pred.est])
    return pd.DataFrame(predictions, columns=["user_id", "restaurant_id", "predicted_rating"])

# 데이터 로드
user_rating_data = get_user_rating_table()
users = list(set(row["user_id"] for row in user_rating_data))
restaurants = list(set(row["restaurant_id"] for row in user_rating_data))

# 사용자별로 0점으로 설정된 음식점 목록을 가져옵니다.
user_zero_rated_restaurants = {user: get_zero_rated_restaurants(user_rating_data, user, restaurants) for user in users}

# 데이터를 Surprise 라이브러리에서 사용할 수 있는 형태로 변환합니다.
ratings_df = pd.DataFrame(user_rating_data)
# ratings_df['user_id'] = ratings_df['user_id'].astype(str)  # user_id를 문자열로 변환합니다. 추후 문자열 id로 실제 입력받을 때 추가해야하는 코드

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'restaurant_id', 'rating']], reader)

# 데이터를 학습 및 테스트셋으로 분할합니다.
trainset, testset = train_test_split(data, test_size=0.2)

# 사용자 기반 협업 필터링 알고리즘을 사용해 모델을 학습합니다.
algo = KNNBasic(sim_options={'user_based': True})
# algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': True}) # 추후 문자열 id로 실제 입력받을 때 추가해야하는 코드
algo.fit(trainset)

# 테스트셋에 대한 예측을 수행하고 정확도를 계산합니다.
test_pred = algo.test(testset)
print("Test RMSE: ", accuracy.rmse(test_pred))

# 0점으로 설정된 음식점에 대해 평점을 예측합니다.
predicted_zero_rated_restaurants = predict_unrated_restaurants(algo, user_zero_rated_restaurants)

# 클러스터링을 위한 사용자별 예측 평점 평균을 계산합니다.
user_predicted_ratings = predicted_zero_rated_restaurants.groupby("user_id")["predicted_rating"].mean().reset_index()

# 사용자를 클러스터로 분류합니다.
kmeans = KMeans(n_clusters=3,n_init=10)
user_predicted_ratings["cluster"] = kmeans.fit_predict(user_predicted_ratings[["predicted_rating"]])


# 새로운 클러스터링 결과 시각화 코드를 추가합니다.
plt.figure(figsize=(12, 8))
plt.scatter(user_predicted_ratings["user_id"], user_predicted_ratings["predicted_rating"], c=user_predicted_ratings["cluster"], cmap='viridis')

# 각 점에 user_id와 그룹 번호를 표시합니다.
for index, row in user_predicted_ratings.iterrows():
    user_id = row["user_id"]
    cluster_id = int(row["cluster"])
    plt.annotate(f"{user_id} (Group {cluster_id})", (row["user_id"], row["predicted_rating"]), fontsize=9)

plt.title('User Clustering Based on Predicted Ratings')
plt.xlabel('User ID')
plt.ylabel('Predicted Rating')
plt.show()


# MongoDB에 연결합니다.
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["restaurant_db"]

# groups와 group_members 테이블을 생성합니다.
groups = db["groups"]
group_members = db["group_members"]

# 클러스터링된 사용자들을 그룹 테이블에 추가합니다.
group_ids = []

# 그룹 테이블이 비어 있는지 확인합니다.
if groups.count_documents({}) == 0:
    for cluster_id in range(3):
        group_name = f"Group {cluster_id}"
        group_info = f"Group {cluster_id} information"
        group_data = {"group_id": cluster_id, "group_name": group_name, "group_info": group_info}
        groups.insert_one(group_data)

# group_ids 리스트를 채웁니다.
for cluster_id in range(3):
    group_ids.append(cluster_id)

# 클러스터링된 사용자들을 그룹 멤버 테이블에 추가합니다.
group_member_id = 0

# 그룹 멤버 테이블이 비어 있는지 확인합니다.
if group_members.count_documents({}) == 0:
    for index, row in user_predicted_ratings.iterrows():
        user_id = row["user_id"]
        cluster_id = int(row["cluster"])
        group_id = group_ids[cluster_id]
        group_member_data = {"group_member_id": group_member_id, "group_id": group_id, "user_id": user_id}
        group_members.insert_one(group_member_data)
        group_member_id += 1


# groups 테이블의 내용을 출력합니다.
print("Groups Table:")
groups_data = groups.find()
for group_data in groups_data:
    print(group_data)

# group_members 테이블의 내용을 출력합니다.
print("Group Members Table:")
group_members_data = group_members.find()
for gm_data in group_members_data:
    print(gm_data)
