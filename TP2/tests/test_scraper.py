import pytest
import asyncio
from scraper.async_http import fetch_html

@pytest.mark.asyncio
async def test_fetch_html():
    html = await fetch_html('https://example.com')
    assert '<html' in html
