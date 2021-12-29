# use this script just for initial scrape on new db
# loads products from unpacked database files and scrapes pages for any extra content that's not present in products db (i.e. images)

from dbfread import DBF
import ProductsFileLoader
from selenium import webdriver
import time, requests, os, sys

products_loader = ProductsFileLoader.ProductsFileLoader()
products_loader.initalize()
repository = products_loader.get_repository()

print("Got "+str(len(products_loader.products))+" products")
print("Error on "+str(len(products_loader.exceptions))+" products")
# print(products_loader.products)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"')


driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window() # max
driver.set_window_position(0, 0)
driver.set_window_size(1920, 1060)
driver.get("https://sso.techdata.com/as/authorization.oauth2?client_id=shop_ca_client&response_type=code&redirect_uri=https://shop.techdata.ca/oauth&pfidpadapterid=ShieldBaseAuthnAdaptor")
driver.find_element('username').send_keys('785112')
driver.find_element('password').send_keys('LeoLeo611!')
driver.find_element('submitButton').click()
time.sleep(5)
time.sleep(5)
print("done waiting for login")

def scrape_me(product_key, product_data):
    product_data_copy = product_data
    product_code = product_data.get('part_number')
    original_url = "https://shop.techdata.ca/products/"+product_code+"/?P="+product_code
    print('getting '+original_url)
    driver.get(original_url)
    product_title = driver.find_element('productTitle').get_attribute('textContent')
    product_description = driver.find_element('prodDescription').get_attribute('textContent').strip()
    driver.find_element('specsTab').click()
    time.sleep(3)

    try:
        os.makedirs("data/" + product_data.get('part_number'))
    except:
        print("dir already exists")

    specs = driver.find_elements('.extSpecsTable-detail tr')
    specs_to_add = {}
    for spec_element in specs:
        spec_cells = spec_element.find_elements_by_css_selector('td')
        spec_key = spec_cells[0].get_attribute('textContent').strip()
        spec_value = spec_cells[1].get_attribute('textContent').strip()
        specs_to_add.update({
            spec_key: spec_value
        })
    time.sleep(1)

    features = driver.find_elements('.ccs-cc-inline-feature')
    features_to_add = {}
    feature_number = 0
    print("getting features")
    for feature_element in features:
        try:
            feature_image_save_path = "data/" + product_data.get('part_number')
            feature_image_element = feature_element.find_element_by_css_selector('.ccs-cc-inline-thumbnail a')
            feature_thumb_element = feature_element.find_element_by_css_selector('.ccs-cc-inline-thumbnail img')

            feature_name = feature_image_element.get_attribute('data-caption')
            feature_image_url = feature_thumb_element.get_attribute('data-large')
            feature_thumb_url = feature_thumb_element.get_attribute('src')
            feature_text = feature_element.find_element_by_css_selector('.ccs-cc-inline-feature-description').get_attribute('textContent').strip()

            response = requests.get(feature_image_url)
            if response.status_code == 200:
                with open(feature_image_save_path+"/feature_"+str(feature_number)+".jpg", 'wb') as f:
                    f.write(response.content)

            response = requests.get(feature_thumb_url)
            if response.status_code == 200:
                with open(feature_image_save_path+"/feature_thumb_"+str(feature_number)+".jpg", 'wb') as f:
                    f.write(response.content)

            features_to_add.update({
                'text': feature_text,
                'image': "feature_"+str(feature_number)+".jpg",
                'thumb': "feature_thumb_"+str(feature_number)+".jpg"
            })
        except:
            #no features present
            pass
        print('found feature...')
    image_elements = driver.find_elements('.bxslider img')

    images = []
    for image in image_elements:
        image_url = image.get_attribute('src')
        if "?timestamp=" in image_url:
            image_url = image_url.split("?timestamp=")[0]

        image_file = os.path.basename(image_url)

        if image_file in images:
            continue

        image_save_path = "data/" + product_data.get('part_number') + "/" + image_file
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_save_path, 'wb') as f:
                f.write(response.content)
                images.append(image_file)

    product_data_copy.update({
        "title": product_title,
        "original_url": original_url,
        "description": product_description
            .replace("Tech Data Description:","Description:")
            .replace("\n\t\tDescription\n\t\t\tDescription","").strip(),
        "images": images,
        'specs': specs_to_add,
        'features': features_to_add
    })

    repository.save_product(product_data_copy)
    print(50*"*")
    print(50*"*")

for product_key, product_data in products_loader.products.items():
    try:
        scrape_me(product_key, product_data)
    except:
        # sleep and retry
        try:
            os.rmdir("data/" + product_data.get('part_number'))
            time.sleep(5)
            scrape_me(product_key, product_data)
        except:
            print('failed 2 times, skipping '+ product_data.get('part_number'))