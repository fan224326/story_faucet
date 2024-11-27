import re
import time
import random
from datetime import datetime
from sys import stderr, exit
from loguru import logger

import settings


logger.remove()
logger.add(stderr, format="<white>{time:DD-MM HH:mm:ss}</white> | <level>{level: <3}</level> | <level>{message}</level>")


def sleeping(sleep_from=settings.TO_SLEEP_ACCOUNT[0], sleep_to=settings.TO_SLEEP_ACCOUNT[1]):
    if isinstance(sleep_from, list):
        sleep_from, sleep_to = sleep_from
    time_sleep = round(random.uniform(sleep_from, sleep_to), 2)
    # logger.info(f'Sleeping {time_sleep}s...')
    time.sleep(time_sleep)


def load_wallets(file_path):
    with open(file_path) as keys_file:
        accounts = [line.strip() for line in keys_file.readlines()]
        logger.info(f'{len(accounts)} wallets was loaded')
        return accounts


def load_proxies(file_path, accounts):
    if settings.USE_PROXY:
        with open(file_path) as proxy_file:
            proxies = []
            for proxy in proxy_file.readlines():
                if proxy == 'ip:port:login:pass': return None
                if re.match(r'^.+:.+:.+:.+$', proxy):
                    proxies.append(proxy.strip())
                else:
                    exit('Incorrect format of proxies! The correct one is: ip:port:login:pass')
        accounts_proxy = {}
        if len(proxies) != len(accounts):
            exit('Proxies and privates numbers are different, I am ending! Set USE_PROXY = False or add additional proxies')
        else:
            wal_data = list(zip(proxies, accounts))
            for proxy, account in wal_data:
                accounts_proxy[account] = proxy
        return accounts_proxy
    else:
        return None


def request_proxy_format(proxy):
    if not proxy: return None
    proxy_list = proxy.split(':')
    return {
        'http': f'http://{proxy_list[2]}:{proxy_list[3]}@{proxy_list[0]}:{proxy_list[1]}',
        'https': f'http://{proxy_list[2]}:{proxy_list[3]}@{proxy_list[0]}:{proxy_list[1]}',
    }
