import asyncio

from task1 import FILENAME


def _get_16bit_checksum(data: bytes, checksum: int = 0) -> int:
    bytes_data = bytearray(data)

    for byte in bytes_data:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum = (checksum + byte) & 0xffff

    return checksum


async def get_file_checksum(filename: str) -> int:
    chunk_size = 1024 * 1024  # 1 Mb
    checksum = 0

    with open(filename, 'rb') as f:
        while (chunk := f.read(chunk_size)):
            checksum = _get_16bit_checksum(data=chunk, checksum=checksum)

    return checksum


async def main():
    result = await get_file_checksum(filename=FILENAME)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
