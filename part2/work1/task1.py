import concurrent.futures
import random
import time
from typing import Iterable
from typing import Optional

from constants import MILLISECONDS
from utils import print_result

ARRAY_SIZE = 10**5


@print_result
def find_min(
    nums: Iterable[int],
    start: int = 0,
    end: Optional[int] = None,
) -> int:
    if len(nums) == 0:
        return -1

    if end is None:
        end = len(nums)

    m = nums[start]

    for idx in range(start + 1, end):
        if nums[idx] < m:
            m = nums[idx]

        time.sleep(1 * MILLISECONDS)

    return m


@print_result
def multithreading_find_min(nums: Iterable[int], thread_count: int) -> int:
    nums_part_size = len(nums) // thread_count

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []

        for i in range(thread_count):
            start = i * nums_part_size
            end = (start + nums_part_size) if (i < thread_count - 1) else len(nums)

            future = executor.submit(find_min, nums=nums, start=start, end=end)
            futures.append(future)

        calculated_mins: list[int] = []

        for future in concurrent.futures.as_completed(futures):
            calculated_mins.append(future.result())

    return find_min(calculated_mins)


def build_nums(size: int, minimum: int = 0, maximum: int = 10**5) -> list[int]:
    return [random.randint(minimum, maximum) for _ in range(size)]


def main():
    size = ARRAY_SIZE
    nums = build_nums(size=size)

    find_min(nums)
    multithreading_find_min(nums, thread_count=4)


if __name__ == "__main__":
    main()
