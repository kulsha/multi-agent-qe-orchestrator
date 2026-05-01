import re
import pytest
from playwright.async_api import async_playwright, expect, Page
from pages.loginpage import LoginPage


# Test data constants
VALID_USERNAME = "Admin"
VALID_PASSWORD = "admin123"
INVALID_USERNAME = "invaliduser"
INVALID_PASSWORD = "wrongpassword"
WHITESPACE = "   "
ERROR_INVALID_CREDENTIALS = "Invalid credentials"
ERROR_REQUIRED = "Required"
LOGIN_URL_PATTERN = r'/auth/login'
DASHBOARD_URL_PATTERN = r'/dashboard'


@pytest.fixture
async def browser_context():
    """Fixture to provide browser context with proper cleanup."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()


@pytest.fixture
async def login_page(browser_context: Page) -> LoginPage:
    """Fixture to provide initialized LoginPage instance."""
    return LoginPage(browser_context)


@pytest.mark.asyncio
async def test_tc_001_001(login_page: LoginPage):
    """
    TC_001_001: Verify successful login with valid credentials
    
    Positive test case that verifies a user can successfully login with
    valid credentials (username: Admin, password: admin123) and is redirected
    to the dashboard with the dashboard header visible.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Perform login with valid credentials
    await login_page.login(VALID_USERNAME, VALID_PASSWORD)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Verify dashboard header is visible
    await expect(login_page.userNameNav).to_be_visible()
    
    # Assertions
    # Assert URL contains /dashboard
    await expect(login_page.page).to_have_url(re.compile(DASHBOARD_URL_PATTERN))
    
    # Assert username navigation element is visible
    await expect(login_page.userNameNav).to_be_visible()
    
    # Assert logo is visible (confirming dashboard loaded)
    await expect(login_page.logo).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_002(login_page: LoginPage):
    """
    TC_001_002: Verify login fails with invalid username
    
    Negative test case that verifies login fails when an invalid username
    is provided (invaliduser) with correct password, and user remains on
    login page with error message displayed.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Attempt login with invalid username
    await login_page.login(INVALID_USERNAME, VALID_PASSWORD)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message contains correct text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_INVALID_CREDENTIALS in error_text


@pytest.mark.asyncio
async def test_tc_001_003(login_page: LoginPage):
    """
    TC_001_003: Verify login fails with incorrect password
    
    Negative test case that verifies login fails when correct username
    (Admin) is provided with incorrect password (wrongpassword), and user
    remains on login page with error message displayed.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Attempt login with incorrect password
    await login_page.login(VALID_USERNAME, INVALID_PASSWORD)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message contains correct text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_INVALID_CREDENTIALS in error_text


@pytest.mark.asyncio
async def test_tc_001_004(login_page: LoginPage):
    """
    TC_001_004: Verify login fails with empty username field
    
    Boundary test case that verifies login fails when username field is
    left empty, and a validation error message is displayed indicating
    the field is required.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-4: Fill password and attempt login without username
    await login_page.password_input_field.fill(VALID_PASSWORD)
    await login_page.login_button_locator.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 5: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message indicates required field
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_REQUIRED in error_text


@pytest.mark.asyncio
async def test_tc_001_005(login_page: LoginPage):
    """
    TC_001_005: Verify login fails with empty password field
    
    Boundary test case that verifies login fails when password field is
    left empty, and a validation error message is displayed indicating
    the field is required.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-4: Fill username and attempt login without password
    await login_page.username_input_field.fill(VALID_USERNAME)
    await login_page.login_button_locator.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 5: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message indicates required field
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_REQUIRED in error_text


@pytest.mark.asyncio
async def test_tc_001_006(login_page: LoginPage):
    """
    TC_001_006: Verify login fails with whitespace-only username
    
    Boundary test case that verifies login fails when username contains
    only whitespace characters, and error message is displayed indicating
    invalid credentials.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Attempt login with whitespace-only username
    await login_page.login(WHITESPACE, VALID_PASSWORD)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message contains correct text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_INVALID_CREDENTIALS in error_text


@pytest.mark.asyncio
async def test_tc_001_007(login_page: LoginPage):
    """
    TC_001_007: Verify login fails with whitespace-only password
    
    Boundary test case that verifies login fails when password contains
    only whitespace characters, and error message is displayed indicating
    invalid credentials.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Attempt login with whitespace-only password
    await login_page.login(VALID_USERNAME, WHITESPACE)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message contains correct text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_INVALID_CREDENTIALS in error_text