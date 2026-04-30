import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.login import LoginPage


# Test data constants
VALID_USERNAME = "Admin"
VALID_PASSWORD = "admin123"
INVALID_USERNAME = "invaliduser"
INVALID_PASSWORD = "wrongpassword"
WHITESPACE_INPUT = "   "
DASHBOARD_URL_PATTERN = re.compile(r'/dashboard')
LOGIN_PAGE_URL_PATTERN = re.compile(r'/auth/login')
EXPECTED_ERROR_MESSAGE = "Invalid credentials"


@pytest.fixture
async def login_page():
    """Fixture to provide LoginPage instance with browser lifecycle."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page    = await browser.new_page()
        lp      = LoginPage(page)
        await lp.navigate()
        await page.wait_for_load_state("networkidle")
        yield lp
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_001(login_page):
    """TC_001_001 — Verify successful login with valid credentials."""
    await login_page.username_input.fill(VALID_USERNAME)
    await login_page.password_input.fill(VALID_PASSWORD)
    await login_page.login_button.click()
    await login_page.page.wait_for_load_state("networkidle")

    await expect(login_page.page).to_have_url(DASHBOARD_URL_PATTERN)
    await expect(login_page.username_navbar).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_002(login_page):
    """TC_001_002 — Verify login fails with invalid username."""
    await login_page.username_input.fill(INVALID_USERNAME)
    await login_page.password_input.fill(VALID_PASSWORD)
    await login_page.login_button.click()
    await login_page.page.wait_for_load_state("networkidle")

    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    await expect(login_page.username_input).to_be_visible()