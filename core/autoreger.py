import time
from concurrent.futures import ThreadPoolExecutor

from core.utils import shift_file, logger
from core.utils.file_to_list import file_to_list
from core.alienswap import AlienSwap

from inputs.config import (
    THREADS, CUSTOM_DELAY, KEYS_FILE_PATH, PROXIES_FILE_PATH
)


class AutoReger:
    def __init__(self):
        self.success = 0
        self.custom_user_delay = None

    @staticmethod
    def get_accounts():
        keys = file_to_list(KEYS_FILE_PATH)
        proxies = file_to_list(PROXIES_FILE_PATH)

        min_accounts_len = len(keys)

        accounts = []

        for i in range(min_accounts_len):
            accounts.append((keys[i], proxies[i] if len(proxies) > i else None))

        return accounts

    # @staticmethod
    # def remove_account():
    #     return shift_file(KEYS_FILE_PATH), shift_file(PROXIES_FILE_PATH)

    def start(self):
        threads = THREADS

        self.custom_user_delay = CUSTOM_DELAY

        accounts = AutoReger.get_accounts()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.register, accounts)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning(f"No accounts registered :(")

    def register(self, account: tuple):
        alien_swap = AlienSwap(*account)
        is_ok = False
        logs_file_name = "fail"
        msg_result = "Failed"

        try:
            time.sleep(self.custom_user_delay)

            if alien_swap.login():
                res_json = alien_swap.get_daily_bonus()

                is_ok = res_json["status"] == 0
                msg_result = res_json["msg"]
        except Exception as e:
            logger.error(f"Error {e}")

        # AutoReger.remove_account()

        if is_ok:
            logs_file_name = "success"
            self.success += 1

        alien_swap.logs(logs_file_name, msg_result.upper())

    @staticmethod
    def is_file_empty(path: str):
        return not open(path).read().strip()
