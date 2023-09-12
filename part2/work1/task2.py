import time
import random
import uuid
import logging
import concurrent.futures

from utils import print_result

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


@print_result
def raise_to_power(num: int, uid: str, power: int = 2):
    time.sleep(random.randint(1, 5))

    result = num**power
    print(f"{uid} = {result}")

    return result


def request_number():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        while True:
            num = int(input())
            uid = str(uuid.uuid4())
            LOG.info(f"Request was accepted with id = {uid}")

            executor.submit(raise_to_power, num=num, uid=uid)


def main():
    request_number()


if __name__ == "__main__":
    main()
