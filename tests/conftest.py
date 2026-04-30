# tests/conftest.py
# Shared pytest fixtures for all Playwright tests

import pytest
from playwright.async_api import async_playwright


@pytest.fixture(scope="session")
def base_url():
    return (
        "https://opensource-demo.orangehrmlive.com"
        "/web/index.php/auth/login"
    )


@pytest.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page    = await context.new_page()
        yield page
        await context.close()
        await browser.close()