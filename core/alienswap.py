from random import choice

import requests
import tls_client
from fake_useragent import UserAgent  # pip install fake-useragent
# from bs4 import BeautifulSoup

from core.utils import str_to_file, logger
from string import ascii_lowercase, digits

from core.utils import (
    Web3Utils
)

from inputs.config import (
    MOBILE_PROXY,
    MOBILE_PROXY_CHANGE_IP_LINK
)


class AlienSwap(Web3Utils):
    referral = None

    def __init__(self, private_key: str, proxy: str = None):
        Web3Utils.__init__(self, key=private_key)

        self.proxy = AlienSwap.get_proxy(proxy)

        self.headers = {
            'authority': 'alienswap.xyz',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'uk-UA,uk;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://alienswap.xyz',
            'referer': 'https://alienswap.xyz/rewards',
            'user-agent': UserAgent().random,
        }

        self.session = tls_client.Session(
            client_identifier="chrome_112",
            random_tls_extension_order=True
        )

        self.session.headers.update(self.headers)
        self.session.proxies.update({'https': self.proxy, 'http': self.proxy})

    @staticmethod
    def get_proxy(proxy: str):
        if MOBILE_PROXY:
            AlienSwap.change_ip()
            proxy = MOBILE_PROXY

        if proxy is not None:
            return f"http://{proxy}"

    @staticmethod
    def change_ip():
        requests.get(MOBILE_PROXY_CHANGE_IP_LINK)

    def login(self):
        resp_json = self.__sign_in()

        if resp_json.get("status") == 0:
            auth_code = resp_json.get("data", {}).get("access_token")
            self.session.headers["authorization"] = f"Bearer {auth_code}"

            return True

    def __sign_in(self):
        url = 'https://alienswap.xyz/alien-api/api/v1/public/user/signin'

        params = {
            'network': 'eth',
        }

        msg = 'Welcome to AlienSwap!\nClick to sign in and accept the AlienSwap Terms of Service.\nThis request will not trigger a blockchain transaction or cost any gas fees.'

        json_data = {
            'address': self.acct.address.lower(),
            'signature': self.get_signed_code(msg),
            'nonce': msg,
            'src': 4,
            'network': 'eth',
        }

        response = self.session.post(
            url,
            params=params,
            json=json_data,
        )

        return response.json()

    def get_daily_bonus(self):
        url = 'https://alienswap.xyz/alien-api/api/v1/private/points/account/checkin/claim'

        params = {
            'network': 'eth',
        }

        json_data = {
            'address': self.acct.address.lower(),
            'network': 'eth',
        }

        response = self.session.post(
            url,
            params=params,
            json=json_data,
        )

        return response.json()

    def logs(self, file_name: str, msg_result: str):
        file_msg = f"{self.acct.address}|{self.acct.key}|{self.proxy}"
        str_to_file(f"./logs/{file_name}.txt", file_msg)
        if file_name == "success":
            logger.success(f"{self.acct.address} | {msg_result}")
        else:
            logger.error(f"{self.acct.address} | {msg_result}")

    @staticmethod
    def generate_password(k=10):
        return ''.join([choice(ascii_lowercase + digits) for _ in range(k)])
