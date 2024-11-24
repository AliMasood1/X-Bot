
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = file.readlines()
    return [proxy.strip() for proxy in proxies]

def load_auth_tokens(file_path):
    with open(file_path, 'r') as file:
        tokens = file.readlines()
    return [token.strip() for token in tokens]


TARGET_HANDLE = "elonmusk"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Run in headless mode (optional)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def inject_auth_token(driver, auth_token):
    driver.get("https://twitter.com")
    time.sleep(2)
    cookie = {
    "name": "auth_token",
    "value": auth_token,
    "domain": "x.com",
    "path": "/",
    "httpOnly": True,
    "secure": True,
}


    driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(2)

def get_twitter_bio(driver, handle):
    try:
        url = f"https://twitter.com/{handle}"
        driver.get(url)
        time.sleep(3) # Wait for the page to load

        bio_element = driver.find_element(By.XPATH, '//div[@data-testid="UserDescription"]')
        return bio_element.text
    except Exception as e:
        print(f"Error fetching bio: {e}")
    return None

def monitor_bio():
    global current_bio
    last_bio = None
    driver = setup_driver()
    tokens = load_auth_tokens('auth_tokens.txt')

    try:
        for auth_token in tokens:
            print(f"Using auth token: {auth_token}...")
            inject_auth_token(driver, auth_token)
            current_bio = get_twitter_bio(driver, TARGET_HANDLE)
            print(TARGET_HANDLE + ":" +current_bio)

        if current_bio and current_bio != last_bio:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Bio updated: {current_bio}")
            last_bio = current_bio

    except Exception as e:
        print(f"Error during monitoring with token : {e}")

        print("Rotating to next auth token...")
        time.sleep(1)

if __name__ == "__main__":
    monitor_bio()