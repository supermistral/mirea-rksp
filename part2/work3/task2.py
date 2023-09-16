import random

import reactivex
from reactivex import operators as ops


def generate_random_nums(min_value: int = 0, max_value = 1000, count: int = 1000) -> list[int]:
    return [random.randint(min_value, max_value) for _ in range(count)]


def get_stream_with_count():
    sequence = generate_random_nums(count=random.randint(100, 1000))
    source = reactivex.from_iterable(sequence).pipe(ops.count())
    return source


def get_stream_with_zip_of_streams():
    sequence_1 = generate_random_nums(count=5)
    sequence_2 = generate_random_nums(count=5)
    source_1 = reactivex.from_iterable(sequence_1)
    source_2 = reactivex.from_iterable(sequence_2)
    source = reactivex.zip(source_1, source_2).pipe(
        ops.flat_map(lambda num: num)
    )
    return source


def get_stream_with_last_number():
    sequence = generate_random_nums(count=random.randint(10, 100))
    source = reactivex.from_iterable(sequence).pipe(ops.last())
    return source


def main():
    print_sequence = lambda num: print(num)

    stream_getters = [
        get_stream_with_count,
        get_stream_with_zip_of_streams,
        get_stream_with_last_number,
    ]

    for stream_getter in stream_getters:
        stream = stream_getter()
        stream.subscribe(print_sequence)


if __name__ == "__main__":
    main()
