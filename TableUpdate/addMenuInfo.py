
from pymongo import MongoClient
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_menuInfo(place_id):
    url = f"https://place.map.kakao.com/{place_id}"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    menus = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'loss_word')))

        menu_info_element = driver.find_elements(By.XPATH, "//div[@data-viewid='menuInfo']")
        if not menu_info_element:
            menus.append((None, None))
            return menus

        try:
            more_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link_more")))
            driver.execute_script("arguments[0].click();", more_button)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='menu']/div[@class='list_menu']")))
        except:
            pass

        menu_elements = driver.find_elements(By.CLASS_NAME, 'loss_word')
        price_elements = driver.find_elements(By.CLASS_NAME, 'price_menu')

        if not menu_elements:
            menus.append((None, None))
            return menus

        for menu_element, price_element in zip(menu_elements, price_elements):
            try:
                if not menu_element.get_attribute('data-category'):
                    menu_name = menu_element.text.strip()
                    if '\n' in menu_name:
                        menu_name = menu_name.split('\n')[-1]
                    menu_price = price_element.text.strip() if price_element else None
                else:
                    menu_name = None
                    menu_price = None
            except:
                menu_name = None
                menu_price = None

            if menu_name:
                menus.append((menu_name, menu_price))
            elif not menus:
                menus.append((None, None))

        # 메뉴 이름 정보만 있는 경우 처리
        if not menus:
            for menu_element in menu_elements:
                menu_name = menu_element.text.strip()
                if '\n' in menu_name:
                    menu_name = menu_name.split('\n')[-1]
                menus.append((menu_name, None))

    except Exception as e:
        menus.append((None, None))

    finally:
        driver.quit()

    return menus




client = MongoClient("mongodb+srv://dongun3m:13792346asd@seondongun.cvaxniv.mongodb.net/test")
db = client["restaurant_db2"]
restaurant_table = db['restaurant_table']

restaurant_names_and_addresses = []

for restaurant in restaurant_table.find():
    restaurant_name = restaurant["name"]
    restaurant_address = restaurant["roadAddress"]
    restaurant_names_and_addresses.append((restaurant_name, restaurant_address))

'''
restaurant_name = "소문난 닭칼국수닭곰탕"
restaurant_address = "서울 광진구 능동로16길 48"
restaurant_names_and_addresses.append((restaurant_name, restaurant_address))
'''
params = {}
for keyword, road_address in restaurant_names_and_addresses:
    print(keyword)
    params["query"] = keyword
    headers = {"Authorization": "KakaoAK 4b92414016836f196362ef142f1686dd"}
    response = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json", headers=headers, params=params)
    data = response.json()
    for item in data["documents"]:
        place_id = item["id"]
        search_address = item["road_address_name"]
        rname = item["place_name"]
        if keyword == rname and search_address == road_address:
            menus = get_menuInfo(place_id)
            print(menus)
            restaurant_table.update_one(
                {"name": rname},
                {'$set': {'menu': menus}}
            )
            print("complete\n")
