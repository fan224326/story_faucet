import json
import requests
from time import sleep
from fake_useragent import UserAgent
from web3 import Web3

from modules.retry import retry
from modules.tools import logger
from settings import CAPTCHA_KEY


class Faucet:
    def __init__(self, address, proxy=None):
        self.address = Web3.to_checksum_address(address)
        self.proxy = proxy
        self.headers = {
            "accept": "text/x-component",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "es-ES,es;q=0.9",
            "content-length": "969",
            "content-type": "text/plain;charset=UTF-8",
            "next-action": "4bb3c690c4758b1deb49ab27129bac517ea77d04",
            "next-router-state-tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2F%22%2C%22refresh%22%5D%7D%2Cnull%2Cnull%2Ctrue%5D",
            "origin": "https://faucet.story.foundation",
            "priority": "u=1, i",
            "referer": "https://faucet.story.foundation/",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": UserAgent(browsers=['chrome'], platforms=['pc']).random,
        }
        self.url = 'https://faucet.story.foundation/'

    def claim_tokens(self):
        captcha_token = self.solve_2captcha()
        json_response = self.request_tokens(captcha_token)
        if json_response['result']:
            logger.success(f'[+] Faucet | {json_response["message"]}')
        else:
            logger.warning(f'[-] Faucet | {json_response["message"]}')

    def request_tokens(self, captcha_token):
        json_data = [
           {
              "address": self.address,
              "token": captcha_token,
              "id": "",
              "provider": "Gitcoin",
              "score": 7
           }
        ]

        response = self.request(headers=self.headers, json=json_data).text

        json_format = json.loads(response.split('\n')[1].replace('1:', ''))
        return json_format

    def solve_2captcha(self):
        def create_task():
            if not self.proxy:
                payload_kwargs = {"type": "TurnstileTaskProxyless"}
            else:
                proxy_type, user, psw, ip, port = self.proxy['http'].replace('://', ':').replace('@', ':').split(':')
                payload_kwargs = {
                    "type": "TurnstileTask",
                    "proxyType": proxy_type,
                    "proxyAddress": ip,
                    "proxyPort": port,
                    "proxyLogin": user,
                    "proxyPassword": psw,
                }
            payload = {
                "clientKey": CAPTCHA_KEY,
                "task": {
                    "websiteURL": "https://faucet.story.foundation/",
                    "websiteKey": "0x4AAAAAAAgnLZFPXbTlsiiE",
                    **payload_kwargs
                }
            }

            r = self.request(f'https://{api_url}/createTask', json=payload)
            if r.json().get('taskId'):
                return r.json()['taskId']
            else:
                raise Exception(f'Faucet Captcha error: {r.text}')

        def get_task_result(task_id: str):
            payload = {
                "clientKey": CAPTCHA_KEY,
                "taskId": task_id
            }
            r = self.request(f'https://{api_url}/getTaskResult', json=payload)

            if r.json().get('status') in ['pending', 'processing']:
                sleep(3)
                return get_task_result(task_id=task_id)
            elif r.json().get('status') == 'ready':
                logger.info(f'[+] Faucet | Captcha solved')
                return r.json()['solution']['token']
            else:
                raise Exception(f"Couldn't solve captcha for Faucet: {r.text}")

        api_url = 'api.2captcha.com'
        task_id = create_task()
        logger.info(f'[•] Faucet | Waiting for solve captcha')
        return get_task_result(task_id=task_id)

    @retry('Request')
    def request(self, url='https://faucet.story.foundation/', method='post', **kwargs):
        response = requests.request(method=method, url=url, proxies=self.proxy, **kwargs)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f'Request failed, {response}\n{kwargs}')
