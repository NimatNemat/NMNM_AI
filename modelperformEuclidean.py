import pandas as pd
from pymongo import MongoClient
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error


def get_user_rating_table():
    client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
    db = client["restaurant_db2"]
    user_rating_table = db["user_rating_table"]
    data = []
    for row in user_rating_table.find():
        data.append(row)
    return data


def split_data(data):
    df = pd.DataFrame(data)
    train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)
    return train_data, test_data


def euclidean_similarity(a, b):
    distance = np.linalg.norm(a - b)
    return 1 / (1 + distance)  # 유클리드 거리 기반 유사도: 1 / (1 + distance)

def predict_user_ratings(user_id, train_data):
    ratings_df = pd.DataFrame(train_data)
    user_restaurant_matrix = ratings_df.pivot_table(index='userId', columns='restaurantId', values='rating',
                                                    fill_value=0)

    # 유사도 행렬 계산
    similarity_matrix = user_restaurant_matrix.apply(
        lambda row: euclidean_similarity(row, user_restaurant_matrix.loc[user_id]), axis=1)

    similarity_matrix.drop(user_id, inplace=True)

    weighted_sum = np.dot(similarity_matrix, user_restaurant_matrix.loc[similarity_matrix.index])
    sum_of_weights = np.abs(similarity_matrix).sum()

    # 예측된 평점 계산
    predicted_ratings = weighted_sum / sum_of_weights
    predicted_ratings_df = pd.DataFrame(predicted_ratings, index=user_restaurant_matrix.columns, columns=["rating"])

    # 사용자가 이미 평가한 레스토랑 제외
    already_rated = user_restaurant_matrix.loc[user_id] != 0
    predicted_ratings_df = predicted_ratings_df[~already_rated]

    return predicted_ratings_df


def evaluate_model(test_data, your_user_id):
    actual_ratings = test_data[test_data["userId"] == your_user_id][["restaurantId", "rating"]].set_index(
        "restaurantId")
    predicted_ratings = predict_user_ratings(your_user_id, train_data)

    merged_ratings = actual_ratings.merge(predicted_ratings, left_index=True, right_index=True,
                                          suffixes=("_actual", "_predicted")).dropna()

    mae = mean_absolute_error(merged_ratings["rating_actual"], merged_ratings["rating_predicted"])
    mse = mean_squared_error(merged_ratings["rating_actual"], merged_ratings["rating_predicted"])

    return mae, mse


pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
pd.set_option('display.max_rows', None)

user_rating_data = get_user_rating_table()
train_data, test_data = split_data(user_rating_data)

your_user_id = "10"
predicted_ratings = predict_user_ratings(your_user_id, train_data)
sorted_predicted_ratings = predicted_ratings.sort_values(by='rating', ascending=False)
print(sorted_predicted_ratings)

mae, mse = evaluate_model(test_data, your_user_id)
print("Mean Absolute Error (MAE):", mae)
print("Mean Squared Error (MSE):", mse)

