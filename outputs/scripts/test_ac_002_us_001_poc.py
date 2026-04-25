import re
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage

# AC_002: AC_002
@pytest.mark.asyncio
async def test_tc_001_008():
    """
    Verify login fails with incorrect password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password("wrongpassword")
        await expect(page.locator('div.error')).to_be_visible()
        await expect(page.locator('input[name="username"]')).to_have_value("Admin")
        await expect(page.locator('#login-form')).to_be_visible()

@pytest.mark.asyncio
async def test_tc_002_001():
    """
    Verify login fails with invalid username
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
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))

@pytest.mark.asyncio
async def test_tc_002_002():
    """
    Verify login fails with incorrect password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password("wrongpassword")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))

@pytest.mark.asyncio
async def test_tc_002_003():
    """
    Verify login fails with empty username
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_password("admin123")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))

@pytest.mark.asyncio
async def test_tc_002_004():
    """
    Verify login fails with empty password
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
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))

@pytest.mark.asyncio
async def test_tc_002_005():
    """
    Verify login fails with whitespace username
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username(" ")
        await login_page.fill_password("admin123")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))

@pytest.mark.asyncio
async def test_tc_002_006():
    """
    Verify login fails with whitespace password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("Admin")
        await login_page.fill_password(" ")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))

@pytest.mark.asyncio
async def test_tc_002_007():
    """
    Verify login fails with both invalid username and password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("invaliduser")
        await login_page.fill_password("wrongpassword")
        await login_page.click_login_button()
        await expect(page.locator('errorMessage')).to_be_visible()
        await expect(page.locator('errorMessage')).to_have_text('Invalid credentials')
        await expect(page).to_have_url(re.compile(r'/auth/login'))