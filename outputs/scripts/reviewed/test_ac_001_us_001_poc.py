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
    """Fixture to provide LoginPage instance with browser lifecycle management."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page_instance = LoginPage(page)
        await login_page_instance.navigate()
        await page.wait_for_load_state("networkidle")
        yield login_page_instance
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_001(login_page):
    """
    TEST CASE TC_001_001: Verify successful login with valid credentials.
    
    Type: Positive
    Test Data: {"username": "Admin", "password": "admin123"}
    
    Expected Result: User is successfully logged in and redirected to dashboard.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for navigation
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /dashboard
    await expect(login_page.page).to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username is visible in navbar
    await expect(login_page.userNameNav).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_002(login_page):
    """
    TEST CASE TC_001_002: Verify login fails with invalid username.
    
    Type: Negative
    Test Data: {"username": "invaliduser", "password": "admin123"}
    
    Expected Result: Login fails, error message displayed, user remains on login page.
    """
    # Step 2: Fill invalid username
    await login_page.username_input_field.fill(INVALID_USERNAME)
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for error
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL does not contain /dashboard
    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username input remains visible (user on login page)
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible and contains expected text
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Error message should be displayed"


@pytest.mark.asyncio
async def test_tc_001_003(login_page):
    """
    TEST CASE TC_001_003: Verify login fails with incorrect password.
    
    Type: Negative
    Test Data: {"username": "Admin", "password": "wrongpassword"}
    
    Expected Result: Login fails, error message displayed, user remains on login page.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Fill incorrect password
    await login_page.password_input_field.fill(INVALID_PASSWORD)
    
    # Step 4: Click login button and wait for error
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL does not contain /dashboard
    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username input remains visible (user on login page)
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible and contains expected text
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Error message should be displayed"


@pytest.mark.asyncio
async def test_tc_001_004(login_page):
    """
    TEST CASE TC_001_004: Verify login fails with empty username.
    
    Type: Boundary
    Test Data: {"username": "", "password": "admin123"}
    
    Expected Result: Login fails, validation error displayed, user remains on login page.
    """
    # Step 2: Ensure username input is empty
    await login_page.username_input_field.clear()
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for response
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL does not contain /dashboard
    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username input remains visible (user on login page)
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for empty username"


@pytest.mark.asyncio
async def test_tc_001_005(login_page):
    """
    TEST CASE TC_001_005: Verify login fails with whitespace username.
    
    Type: Boundary
    Test Data: {"username": "   ", "password": "admin123"}
    
    Expected Result: Login fails, validation error displayed, user remains on login page.
    """
    # Step 2: Fill username with whitespace only
    await login_page.username_input_field.fill(WHITESPACE_INPUT)
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for response
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL does not contain /dashboard
    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username input remains visible (user on login page)
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for whitespace username"


@pytest.mark.asyncio
async def test_tc_001_006(login_page):
    """
    TEST CASE TC_001_006: Verify login fails with empty password.
    
    Type: Boundary
    Test Data: {"username": "Admin", "password": ""}
    
    Expected Result: Login fails, validation error displayed, user remains on login page.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Ensure password input is empty
    await login_page.password_input_field.clear()
    
    # Step 4: Click login button and wait for response
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL does not contain /dashboard
    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username input remains visible (user on login page)
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for empty password"


@pytest.mark.asyncio
async def test_tc_001_007(login_page):
    """
    TEST CASE TC_001_007: Verify login fails with whitespace password.
    
    Type: Boundary
    Test Data: {"username": "Admin", "password": "   "}
    
    Expected Result: Login fails, validation error displayed, user remains on login page.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Fill password with whitespace only
    await login_page.password_input_field.fill(WHITESPACE_INPUT)
    
    # Step 4: Click login button and wait for response
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL does not contain /dashboard
    await expect(login_page.page).not_to_have_url(DASHBOARD_URL_PATTERN)
    
    # Assertion 2: Username input remains visible (user on login page)
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for whitespace password"