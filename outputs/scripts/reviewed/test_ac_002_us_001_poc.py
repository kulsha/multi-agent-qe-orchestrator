import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage

# Define test data
test_data = [
    {"username": "invaliduser", "password": "admin123", "expected_error": "Invalid credentials"},
    {"username": "Admin", "password": "wrongpassword", "expected_error": "Invalid credentials"},
    {"username": "", "password": "admin123", "expected_error": "Invalid credentials"},
    {"username": "Admin", "password": "", "expected_error": "Invalid credentials"},
    {"username": " ", "password": "admin123", "expected_error": "Invalid credentials"},
    {"username": "Admin", "password": " ", "expected_error": "Invalid credentials"},
    {"username": "invaliduser", "password": "wrongpassword", "expected_error": "Invalid credentials"},
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
        await expect(login_page.errorMessage).to_be_visible()
        await expect(login_page.errorMessage).to_contain_text(test_case["expected_error"])
        await expect(page).to_have_url(re.compile(r'/auth/login'))

# Update LoginPage class to include navigate method
class LoginPage:
    # existing code...

    async def navigate(self) -> 'LoginPage':
        """Navigates to the login page."""
        await self.page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        return self