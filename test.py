import requests
import time

def check_username(username):
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 404:
            return True  # متاح
        else:
            return False  # مأخوذ

    except requests.RequestException:
        return None  # حصل خطأ

# قائمة اليوزرات للتجربة
usernames = [
    '9ltn', 'b04z', 'cbr3', 'yi9o', 'idn', 'k25i', '5tk0', 'ahxm', 'xiaa'
]

for username in usernames:
    available = check_username(username)
    if available is True:
        print(f"Available: {username}")
    elif available is False:
        print(f"Taken: {username}")
    else:
        print(f"Error checking: {username}")
    
    time.sleep(1)  # تأخير لتجنب الحظر
