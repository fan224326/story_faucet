import time

from settings import RETRY
from modules.tools import logger


def retry(module_str: str, retries=RETRY):
    def decorator(f):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return f(*args, **kwargs)

                except Exception as e:
                    error_string = f'[-][{attempt+1}/{retries}] {module_str} | {e}'
                    logger.error(error_string)
                    attempt += 1
                    if attempt == retries:
                        raise ValueError(f'{module_str}: {e}')
                    else:
                        time.sleep(30)
        return newfn
    return decorator
