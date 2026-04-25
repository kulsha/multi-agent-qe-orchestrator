import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage

# AC_003: AC_003
@pytest.mark.asyncio
async def test_username_input_field_is_visible():
    """
    Verify username input field is present
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.navigate()
        await expect(login_page.username_input_field).to_be_visible()

@pytest.mark.asyncio
async def test_orangehrm_logo_is_visible():
    """
    Verify OrangeHRM logo is present
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.navigate()
        await expect(login_page.logo).to_be_visible()

# Update LoginPage class to remove duplicate locator attributes
class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.login_button_locator = page.locator("[name='submit']")
        self.username_input_field = page.locator("[name='username']")
        self.password_input_field = page.locator("[name='password']")
        self.loginButton = page.locator("[name='submit']")
        self.userNameNav = page.locator("div.orangehrm-header-container>nav>ul>li>span")
        self.errorMessage = page.locator("div.orangehrmLoginContainer>form>div>span")
        self.logo = page.locator("#orb-global-header > div > div:nth-child(1) > a")

    # existing code...