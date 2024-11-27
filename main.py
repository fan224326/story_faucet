import random
import time

from modules.faucet import Faucet
from modules.tools import load_wallets, load_proxies, logger, request_proxy_format, sleeping
from settings import SHUFFLE_WALLETS, INFINITY_MODE


def main():
    addresses = load_wallets('addresses.txt')
    accounts_proxy = load_proxies('proxies.txt', addresses)

    if SHUFFLE_WALLETS:
        random.seed()
        random.shuffle(addresses)

    for address in addresses:
        try:
            logger.info(f'Account {address} started!')
            account_proxy = request_proxy_format(accounts_proxy[address] if accounts_proxy else None)
            faucet = Faucet(address, account_proxy)
            faucet.claim_tokens()
            sleeping()
        except Exception as e:
            logger.error(f'Account {address} error!\n{e}')


if __name__ == "__main__":
    try:
        while True:
            main()
            if INFINITY_MODE:
                logger.success('Accounts done, waiting 24h')
                time.sleep(3600*24)
    except KeyboardInterrupt:
        logger.warning("Cancelled by the user")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
