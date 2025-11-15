import aiohttp
import asyncio

async def fetch_html(url: str, timeout: int = 30) -> str:
    """
    Descarga el HTML de una URL de forma asíncrona usando aiohttp.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
