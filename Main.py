import asyncio
import sys
from Parser.Parsing import download_news
import pymongo


async def AddDateBase(database, queue):
    while True:
        x = await queue.get()
        db = database['news']
        db.insert_many(x)
        queue.task_done()


async def main():
    client = pymongo.MongoClient("localhost", 27017)

    db = client['news_date']

    queue = asyncio.Queue()
    downloader = asyncio.create_task(download_news(queue))
    printer = asyncio.create_task(AddDateBase(db, queue))
    await asyncio.gather(downloader)
    printer.cancel()
    await asyncio.gather(printer, return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())
