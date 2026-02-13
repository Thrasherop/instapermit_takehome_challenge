from pprint import pprint

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from llms import get_gemini_response

def _try_fetch_amazon_data():

    URL = "https://www.amazon.com/s?k=laptops"
    # URL = "https://www.thrasherop.dev"

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    # Attempt to grab the data
    failed_fetch_attempts = 0
    while True:

        try:

            driver.get(URL) 

            # Wait until it loads
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            print("Title: ", driver.title)
            print("Title:", driver.title)
            print("URL:", driver.current_url)

            if not "Sorry" in driver.title:
                return driver
            else:
                failed_fetch_attempts += 1

        except:
            failed_fetch_attempts += 1

        if failed_fetch_attempts > 2:
            # cleanup and return
            driver.quit()
            return None

    
    

def process_amazon_data():

    # Try to get amazon data
    result = _try_fetch_amazon_data()

    if result != None:
        # I don't have the scraping code unfortunately. 
        # All my selenium requests were blocked by amazon, and I didn't have enough time to
        # try and defeat amazons scrape protection. 
        # As such, I wasn't able to actually iterate or test any code for getting
        # data out of a working page.

        

        pass
    else:
        return None
        

    

def get_data(skip_to_fallback : bool = False) -> list[dict]:


    

    final_data = []

    if not skip_to_fallback:
        amazon_attempt = process_amazon_data()
        if amazon_attempt:
            # again, never got this working so I couldn't
            # iterate on extraction code
            pass

    if skip_to_fallback or amazon_attempt == None:

        print("Failed to scrape amazon after 2 attempts; falling back to fakestore")

        # amazon blocked selenium; time to use fallback
        import requests

        URL = "https://fakestoreapi.com/products"

        data = requests.get(URL).json()

        # isolate title, price, rating, and url
        for product in data:

            this_product = {
                "title" : product['title'],
                "price" : product['price'],
                "rating" : product['rating']['rate'],
                "description" : product['description'],
                "url" : f"{URL}/{product['id']}"
            }

            final_data.append(this_product)


    return final_data

def enhance_data(data : list[dict]) -> list[dict]:

    # load generic prompt
    with open("./prompts/fair_price_prompt.txt", "r") as f:
        prompt_template = f.read()

    # Have AI determine if it is a fair price.
    enhanced_data = []
    for product in data:

        # generate the prompt and response
        this_prompt = prompt_template.replace("$${title}", f"{product['title']}").replace("$${description}", f"{product['description']}").replace("$${price}", f"{product['price']}").replace("$${rating}", f"{product['rating']}")
        response = get_gemini_response(this_prompt, skip_remote_call=True)

        # create new product dict with new information
        new_product_info = product.copy()
        new_product_info['ai_recommendation'] = response

        # append to collector
        enhanced_data.append(new_product_info)


    return enhanced_data



processed_data = get_data(skip_to_fallback=True)
pprint(processed_data) # print as per requirements

# enhance
enhanced_data = enhance_data(processed_data)
pprint(enhanced_data)

