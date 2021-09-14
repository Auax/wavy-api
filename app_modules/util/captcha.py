import requests
import os
from logger import log


def verify_captcha(token) -> [dict, bool]:
    try:
        data = {"secret": os.environ["captcha_secret"],
                "response": token}
        print(data)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res = requests.post("https://www.google.com/recaptcha/api/siteverify",
                            data=data,
                            headers=headers)
        if res.status_code == 200:
            return res.json()

    except KeyError as e:
        log("ERROR", f"Exception: {e}", 3)

    return False
