import re
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage

# AC_003: AC_003
@pytest.mark.asyncio
async def test_tc_003_001():
    """
    Verify username input field is present
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await expect(page.locator('usernameInput')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_003_004():
    """
    Verify OrangeHRM logo is present
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await page.wait_for_timeout(500)
        await expect(page.locator('#divLogo')).to_be_visible()