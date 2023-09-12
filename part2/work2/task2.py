import shutil
import aioshutil
import asyncio

from task1 import create_file
from utils import print_result

FILENAME = "tmp.txt"


@print_result
def copy_file_sync(source_filename: str, dest_filename: str):
    buffer_size = 1024 * 1024  # 1 Mb

    with (
        open(source_filename, 'rb') as src,
        open(dest_filename, 'wb') as dst,
    ):
        while (buffer := src.read(buffer_size)):
            dst.write(buffer)


@print_result
def copy_file_with_shutil(source_filename: str, dest_filename: str):
    shutil.copy(source_filename, dest_filename)


@print_result
async def copy_file_with_aioshutil(source_filename: str, dest_filename: str):
    await aioshutil.copy(source_filename, dest_filename)


def create_filled_file(filename: str):
    required_file_size_bytes = 100 * 1024 * 1024
    data = "1" * required_file_size_bytes

    return create_file(filename=filename, data=data)


async def main():
    filename = FILENAME

    # create_filled_file(filename=filename)

    await copy_file_sync(source_filename=filename, dest_filename="tmp1.txt")
    # await copy_file_with_shutil(source_filename=filename, dest_filename="tmp2.txt")
    # await copy_file_with_aioshutil(source_filename=filename, dest_filename="tmp3.txt")


if __name__ == "__main__":
    # measure memory peak usage
    # /usr/bin/time --verbose ./venv/bin/python task2.py

    asyncio.run(main())
