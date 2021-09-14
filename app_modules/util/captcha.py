import requests
import os


def verify_captcha(token) -> [dict, bool]:
    data = {"secret": os.environ["captcha_secret"],
            "response": token}
    print(data)
    headers = {'Content-type': 'application/json'}
    res = requests.post("https://www.google.com/recaptcha/api/siteverify",
                        data=data,
                        headers=headers)
    if res.status_code == 200:
        return res.json()
    return False
