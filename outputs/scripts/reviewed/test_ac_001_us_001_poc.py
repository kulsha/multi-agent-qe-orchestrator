import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage

# Define test data
test_data = [
    {"username": "Admin", "password": "wrongpassword", "expected_error": "Invalid credentials"},
    {"username": "", "password": "admin123", "expected_error": "Username cannot be empty"},
    {"username": "Admin", "password": "", "expected_error": "Password cannot be empty"},
    {"username": "Admin", "password": " ", "expected_error": "Password cannot be empty"},
    {"username": "invaliduser", "password": "admin123", "expected_error": "Invalid credentials"},
    {"username": "Admin", "password": "admin123", "expected_error": None},
]

@pytest.mark.asyncio
async def test_successful_login():
    """Verifies successful login with valid credentials."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login("Admin", "admin123")
        await expect(page).to_have_url(re.compile(r'/dashboard'))
        await expect(login_page.userNameNav).to_be_visible()

@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", test_data)
async def test_failed_login(test_case):
    """Verifies failed login scenarios."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login(test_case["username"], test_case["password"])
        if test_case["expected_error"]:
            await expect(login_page.errorMessage).to_be_visible()
            await expect(login_page.errorMessage).to_contain_text(test_case["expected_error"])
        else:
            await expect(page).to_have_url(re.compile(r'/dashboard'))
            await expect(login_page.userNameNav).to_be_visible()

# Update LoginPage class to include fill_username, fill_password, and click_login_button methods
class LoginPage:
    # existing code...

    async def fill_username(self, username: str) -> 'LoginPage':
        """Fills the username input field."""
        await self.username_input_field.fill(username)
        return self

    async def fill_password(self, password: str) -> 'LoginPage':
        """Fills the password input field."""
        await self.password_input_field.fill(password)
        return self

    async def click_login_button(self) -> 'LoginPage':
        """Clicks the login button."""
        await self.loginButton.click()
        return self

    async def login(self, username: str, password: str) -> 'LoginPage':
        """Performs a login with the given username and password."""
        await self.fill_username(username)
        await self.fill_password(password)
        await self.click_login_button()
        return self

    async def navigate(self) -> 'LoginPage':
        """Navigates to the login page."""
        await self.page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        return self