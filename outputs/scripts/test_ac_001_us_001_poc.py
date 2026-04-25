import re
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage

# AC_001: AC_001
@pytest.mark.asyncio
async def test_tc_001_003():
    """
    Verify failed login with invalid password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password("wrongpassword")
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        await expect(page.locator('div.error')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_001_004():
    """
    Verify failed login with empty username
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("")
        await login_page.fill_password("admin123")
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        await expect(page.locator('div.error')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_001_006():
    """
    Verify failed login with empty password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password("")
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        await expect(page.locator('div.error')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_001_007():
    """
    Verify failed login with whitespace password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password(" ")
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        await expect(page.locator('div.error')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_001_001():
    """
    Verify successful login with valid credentials
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password("admin123")
        await login_page.click_login_button()
        await expect(page).to_have_url(re.compile(r'/dashboard'))
        await expect(page.locator('userNameNav')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_001_002():
    """
    Verify failed login with invalid username
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("invaliduser")
        await login_page.fill_password("admin123")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_contain_text('Invalid credentials')

@pytest.mark.asyncio
async def test_tc_001_005():
    """
    Verify failed login with empty password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_contain_text('Invalid credentials')