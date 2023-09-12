import asyncio
import aiofiles

FILENAME = "somefile.txt"


def create_file(filename: str, data: str):
    with open(filename, 'w') as f:
        f.write(data)


async def read_file(filename: str) -> str:
    async with aiofiles.open(filename, mode='r') as f:
        content = await f.read()

    return content


async def main():
    data = (
        "Lorem ipsum dolor sit amet"
        "\nconsectetur adipiscing elit, sed do eiusmod tempor incididunt"
        "\labore et dolore magna aliqua"
    )

    create_file(filename=FILENAME, data=data)

    result = await read_file(filename=FILENAME)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
