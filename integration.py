import requests
import time
from itertools import cycle

def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = file.readlines()
    return [proxy.strip() for proxy in proxies]

def load_auth_tokens(file_path):
    with open(file_path, 'r') as file:
        tokens = file.readlines()
    return [token.strip() for token in tokens]


def get_twitter_bio(username, auth_token, proxy):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    proxy_parts = proxy.split(":")
    if len(proxy_parts) == 4:
        formatted_proxy = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"
    else:
        formatted_proxy = f"http://{proxy}"

    proxy_dict = {
        "http": formatted_proxy,
        "https": formatted_proxy
    }

    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=5)
        response.raise_for_status()
        user_data = response.json()
        return user_data.get("data", {}).get("description", None)
    except Exception as e:
        print(f"Error fetching bio: {e}")
        return None


def monitor_bio(username, proxy_file, auth_file):
    proxies = load_proxies(proxy_file)
    tokens = load_auth_tokens(auth_file)

    proxy_pool = cycle(proxies)
    token_pool = cycle(tokens)

    last_bio = None

    while True:
        proxy = next(proxy_pool)
        token = next(token_pool)

        current_bio = get_twitter_bio(username, token, proxy)

        if current_bio is not None:
            if last_bio is None:
                print(f"Initial bio: {current_bio}")
            elif current_bio != last_bio:
                print(f"Bio changed! New bio: {current_bio}")

            last_bio = current_bio

        time.sleep(0.6)  # Check every 600 ms

if __name__ == "__main__":
    USERNAME = "Apple"  # Replace with the Twitter username you want to monitor
    PROXY_FILE = "proxies.txt"  # Path to the proxy text file
    AUTH_FILE = "auth_tokens.txt"  # Path to the auth token text file

    monitor_bio(USERNAME, PROXY_FILE, AUTH_FILE)
