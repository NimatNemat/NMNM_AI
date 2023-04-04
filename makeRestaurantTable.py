import requests
import pymongo
import random
import string
import os
import gridfs
import io
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 음식점 타입을 보여주는 cuisine_categories 정보가 있음. 이거는 기본적으로 음식점 > 한식 > 육류 > 갈비 등등 해당 음식점의 타입을 쭉 나열해서 보여줌.
# 우리는 여기서 한식, 양식, 일식, 중식만 걸러내는 것이 필요하다. 따라서 해당 정보를 문자열 형태로 받고 거기에 한식/양식/일식/중식 이라는 정보가 있다면 바로 그 정보를 반환해줌.
# 한식,양식,일식,중식에 포함되지 않는 음식점 종류의 경우 Other을 반환함
def process_cuisine_type(cuisine_str):
    cuisine_categories = ["분식","피자","치킨","한식", "양식", "일식", "중식","아시아음식","퓨전요리"]
    for category in cuisine_categories:
        if category in cuisine_str:
            return category
    return "Other"

# 사용자 평가를 생성하는 함수입니다. 각 사용자-음식점 쌍에 대해 무작위 평가를 생성합니다.
def generate_individual_user_ratings(num_users, num_restaurants):
    ratings = []
    for user_id in range(num_users):
        for restaurant_id in range(num_restaurants):
            rating = {
                "userId": user_id,
                "restaurantId": restaurant_id,
                "rating" : 0
                #"rating": random.choice([0, 1, 2, 3, 4, 5])
            }
            ratings.append(rating)
    return ratings

# 사용자 평가를 기반으로 평균 선호도를 계산하는 함수입니다.
def calculate_avg_preference(user_ratings_collection, restaurant_id):
    # restaurant_id에 대한 모든 사용자 평가를 찾습니다.
    user_ratings = user_ratings_collection.find({"restaurant_id": restaurant_id})

    total_ratings = 0
    num_scored_ratings = 0

    for user_rating in user_ratings:
        if user_rating["rating"] > 0:
            total_ratings += user_rating["rating"]
            num_scored_ratings += 1

    if num_scored_ratings == 0:
        return 0

    return total_ratings / num_scored_ratings


# 지정된 길이의 무작위 문자열을 생성하는 함수입니다. 사용자 정보 중 암호를 만들 때 사용
def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


# get_business_hours 함수는 주어진 place_id에 대한 영업 시간을 반환합니다.
def get_business_hours(place_id):
    # place_id를 사용하여 카카오 맵 페이지 URL을 생성합니다.
    url = f"https://place.map.kakao.com/{place_id}"

    # 크롬 드라이버를 headless 모드로 설정합니다.
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        # 페이지에서 'txt_operation' 클래스 이름을 가진 요소가 나타날 때까지 최대 10초 동안 기다립니다.
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'txt_operation')))
        # 해당 요소의 텍스트를 가져와 공백을 제거합니다.
        business_hours = driver.find_element(By.CLASS_NAME, 'txt_operation').text.strip()
    except Exception:
        # 요소를 찾지 못하면 영업 시간을 "None"으로 설정합니다.
        business_hours = "None"
    finally:
        # 크롬 드라이버를 종료합니다.
        driver.quit()

    return business_hours



# get_tags 함수는 주어진 place_id에 대한 태그 목록을 반환합니다.
def get_tags(place_id):
    # place_id를 사용하여 카카오 맵 페이지 URL을 생성합니다.
    url = f"https://place.map.kakao.com/{place_id}"

    # 크롬 드라이버를 headless 모드로 설정합니다.
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        # 페이지에서 'link_tag' 클래스 이름을 가진 요소가 나타날 때까지 최대 10초 동안 기다립니다.
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'link_tag')))
        # 해당 요소들을 찾고, tags 리스트에 텍스트를 추가합니다.
        tag_elements = driver.find_elements(By.CLASS_NAME, 'link_tag')
        tags = []
        for tag_element in tag_elements:
            if not tag_element.get_attribute('data-category'):
                tags.append(tag_element.text.strip())
    except Exception as e:
        # 요소를 찾지 못하면 태그 목록을 "None"으로 설정합니다.
        tags = ["None"]
    finally:
        # 크롬 드라이버를 종료합니다.
        driver.quit()

    tags = ",".join(tags)

    return tags



def get_image_url(place_id):
    # place_id를 사용해 URL 생성
    url = f"https://place.map.kakao.com/{place_id}"

    # Chrome 브라우저의 headless 모드를 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Chrome 드라이버를 사용해 웹 드라이버 객체 생성
    driver = webdriver.Chrome(options=chrome_options)

    # URL에 접속
    driver.get(url)

    try:
        # 'bg_present' 클래스를 가진 요소를 찾기 위한 대기
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'bg_present')))
        bg_present = driver.find_element(By.CLASS_NAME, 'bg_present')  # find_elements -> find_element

        # 'style' 속성에서 이미지 URL을 추출
        style = bg_present.get_attribute('style')
        image_url = "https:" + re.search(r"url\(['\"]?(.*?)['\"]?\)", style).group(1)  # 정규식을 사용하여 따옴표 처리

    except Exception as e:
        # 이미지 URL을 찾지 못할 경우, 리스트에 "None"을 저장
        image_url = "None"
    finally:
        # 웹 드라이버 종료
        driver.quit()

    return image_url


def get_image_id(image_url):
    try:
        # 이미지를 바이너리 형태로 다운로드
        image_binary = requests.get(image_url).content

        # 이미지 파일 이름 추출
        image_name = os.path.basename(image_url)

        # 이미지를 GridFS에 저장하고 파일 ID를 반환
        image_id = fs.put(io.BytesIO(image_binary), filename=image_name)
        print(f"Image saved in MongoDB with ID: {image_id}")

        return image_id
    except Exception as e:
        print(f"Error saving image to MongoDB: {e}")


'''
image_id를 얻어서 DB에 저장된 이미지를 역으로 다운로드 할 수 있도록 하는 코드. 사용할 때는 id 정보를 변환해서 쓰면 될듯
def retrieve_image_from_mongodb(image_id, save_path):
    try:
        # GridFS에서 이미지 검색
        image = fs.get(image_id)
        image_name = image.filename

        # 이미지를 지정된 경로에 저장
        file_path = os.path.join(save_path, image_name)
        with open(file_path, 'wb') as f:
            f.write(image.read())

        print(f"Image retrieved from MongoDB and saved at {file_path}")
    except Exception as e:
        print(f"Error retrieving image from MongoDB: {e}")

# 이미지 URL을 사용하여 MongoDB에 이미지 저장
image_id = save_image_to_mongodb(image_url)

# 이미지 ID를 사용하여 MongoDB에서 이미지 검색 및 저장
if image_id is not None:
    save_path = "your_save_path_here"  # 이미지를 저장할 경로를 지정해주세요.
    retrieve_image_from_mongodb(image_id, save_path)
'''


# MongoDB 연결 설정
#client = pymongo.MongoClient("mongodb://localhost:27017/")
client = pymongo.MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db"]
restaurant_collection = db["restaurant_table"] # "restaurant_table"이라는 새 컬렉션을 생성합니다.
user_rating_collection = db["user_rating_table"] # "user_rating_table"이라는 새 컬렉션을 생성합니다.
user_collection = db["user_table"]  # "user_table"이라는 새 컬렉션을 생성합니다.
fs = gridfs.GridFS(db)

num_users = 25
num_restaurants = 304

# user_rating_table과 user_table이 비어있다면 40명의 사용자 정보와 평가를 생성하고 MongoDB에 저장합니다.
if user_rating_collection.count_documents({}) == 0 and user_collection.count_documents({}) == 0:
    # 사용자 정보를 생성하여 user_info_list에 추가합니다.
    user_info_list = []
    for i in range(num_users):
        user_info = {
            "userId": str(i),
            "userName": f"user_{i}",
            "age": random.randint(18, 65),
            "gender": random.choice(["M", "F"]),
            "password": random_string(10),
            "nickName": f"nickname_{i}",
            "phoneNumber": f"phone_{i}",
            "eMail": f"e_mail_{i}"
        }
        user_info_list.append(user_info)

    # 사용자 정보를 user_table에 저장합니다.
    for user_info in user_info_list:
        user_collection.insert_one(user_info)

     # 사용자들의 식당 평가를 생성합니다.
    individual_user_ratings = generate_individual_user_ratings(num_users, num_restaurants)

    # 생성한 사용자 평가를 user_rating_table에 저장합니다.
    for individual_user_rating in individual_user_ratings:
        user_rating_collection.insert_one(individual_user_rating)

# Kakao Map API 요청 파라미터를 설정합니다.
params = {
    "query": "",
    "radius": "120",  # 1km 반경
    "size": "15",  # 페이지당 반환할 결과 수
}

# 검색할 키워드 다중 설정
keywords = ["세종대 식당"]


xs = ["127.081583","127.079021","127.076450","127.076339","127.074955","127.074932","127.073411","127.073187","127.071116","127.070361","127.069236","127.067900",
"127.070384","127.072272","127.074236","127.075116","127.073195","127.071060","127.069091","127.067487","127.069252","127.067799","127.069601","127.071538",
"127.072859","127.071550","127.074079","127.076423","127.077243","127.079453","127.079956","127.078059","127.078734","127.076565","127.076375","127.074812",
"127.074622","127.072824","127.071588","127.069684"]
ys = ["37.550048","37.549554","37.546951","37.54553","37.546824","37.545564","37.545889","37.547351","37.547366","37.546427","37.547982","37.548773","37.548948",
"37.548710","37.548488","37.550113","37.550003","37.550585","37.550011","37.550738","37.551576","37.552546","37.553532","37.552383","37.553383","37.554297",
"37.551520","37.551592","37.553138","37.552544","37.554679","37.554721","37.556039","37.556760","37.555449","37.554361","37.556754","37.556802","37.555642","37.555112"]

# 세종대학교 좌표
sejong_univ_coord = (37.550017, 127.074043)


if restaurant_collection.count_documents({}) == 0:
# 페이지네이션과 함께 API 요청을 보냅니다.
    # 검색할 키워드 별로 카카오맵 API를 활용한 검색을 진행 후 식당 테이블에 데이터 저장
    for x,y in zip(xs,ys):
        params["x"] = x;
        params["y"] = y;

        for keyword in keywords:
            params["query"] = keyword

            for page in range(1, 4):  # 최대 3페이지까지 (페이지 당 15개의 음식점)
                params["page"] = page
                headers = {"Authorization": "KakaoAK 4b92414016836f196362ef142f1686dd"}
                response = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json", headers=headers, params=params)
                data = response.json()
                for i, item in enumerate(data["documents"]):

                    if restaurant_collection.count_documents({"name": item["place_name"]}) > 0:
                        continue

                    # 음식점 타입이 Other인 경우, 즉 한식,양식,중식,일식이 아닌 가게는 음식점 테이블에 추가하지 않음
                    if (process_cuisine_type(item["category_name"]) == "Other"):
                        continue

                    place_id = item["id"]
                    business_hours = get_business_hours(place_id)
                    tags = get_tags(place_id)

                    # get_image_url 함수를 사용하여 이미지 URL을 가져옵니다.
                    image_url = get_image_url(place_id)

                    # 이미지 URL이 유효한 경우 이미지를 저장합니다.
                    if image_url != "None":
                        image_id = get_image_id(image_url)
                    else:
                        image_id = "None"

                    if(item["phone"]!=""):
                        phone = item["phone"]
                    else:
                        phone = "None"


                    # API 응답에서 음식점 정보를 추출합니다.
                    restaurant = {
                        "name": item["place_name"],
                        "xPosition" : item["x"],
                        "yPosition" : item["y"],
                        "cuisineType": process_cuisine_type(item["category_name"]),  # "category_name" 필드를 처리합니다.
                        "avgPreference": round(calculate_avg_preference(user_rating_collection, j), 1),
                        # 사용자 평가에서 평균 선호도를 계산합니다.
                        "address": item["address_name"],
                        "roadAddress": item["road_address_name"],
                        "number": phone,
                        "businessHours": business_hours,
                        "tags": tags,
                        "imageFile": image_id
                    }
                    # MongoDB에 음식점 정보를 삽입합니다.
                    j+=1
                    restaurant_collection.insert_one(restaurant)
                    print(restaurant)

# 음식점 테이블을 출력합니다.
for restaurant in restaurant_collection.find():
    print(restaurant)
