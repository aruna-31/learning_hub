import asyncio
import httpx
from app.services.aggregator import AggregatorService
import logging
from app.config import settings

logging.basicConfig(level=logging.WARNING)

async def main():
    async with httpx.AsyncClient() as client:
        print("GitHub TOKEN:", bool(settings.GITHUB_TOKEN))
        print("GitHub:", await AggregatorService.fetch_github(client, "fastapi"))
        print("Books:", await AggregatorService.fetch_google_books(client, "fastapi"))

asyncio.run(main())
