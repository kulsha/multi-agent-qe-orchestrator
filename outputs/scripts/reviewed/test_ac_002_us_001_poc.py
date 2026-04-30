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
REQUIRED_ERROR_TEXT = "Required"


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
async def test_tc_002_001(login_page):
    """
    TEST CASE TC_002_001: Verify successful login with valid credentials.
    
    Type: Positive
    Test Data: {"username": "Admin", "password": "admin123"}
    
    Expected Result: URL contains /dashboard after successful login.
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


@pytest.mark.asyncio
async def test_tc_002_002(login_page):
    """
    TEST CASE TC_002_002: Verify login fails with invalid username.
    
    Type: Negative
    Test Data: {"username": "invaliduser", "password": "admin123"}
    
    Expected Result: Error message 'Invalid credentials' displayed and user remains on login page.
    """
    # Step 2: Fill invalid username
    await login_page.username_input_field.fill(INVALID_USERNAME)
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for error
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: Error message text equals 'Invalid credentials'
    await expect(login_page.errorMessage).to_have_text(EXPECTED_ERROR_MESSAGE)
    
    # Assertion 2: Username input is visible (user remains on login page)
    await expect(login_page.username_input_field).to_be_visible()


@pytest.mark.asyncio
async def test_tc_002_003(login_page):
    """
    TEST CASE TC_002_003: Verify login fails with valid username and incorrect password.
    
    Type: Negative
    Test Data: {"username": "Admin", "password": "wrongpassword"}
    
    Expected Result: Error message 'Invalid credentials' displayed and user remains on login page.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Fill incorrect password
    await login_page.password_input_field.fill(INVALID_PASSWORD)
    
    # Step 4: Click login button and wait for error
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: Error message text equals 'Invalid credentials'
    await expect(login_page.errorMessage).to_have_text(EXPECTED_ERROR_MESSAGE)
    
    # Assertion 2: Username input is visible (user remains on login page)
    await expect(login_page.username_input_field).to_be_visible()


@pytest.mark.asyncio
async def test_tc_002_004(login_page):
    """
    TEST CASE TC_002_004: Verify login fails with empty username.
    
    Type: Boundary
    Test Data: {"username": "", "password": "admin123"}
    
    Expected Result: Validation error 'Required' displayed for username field and user remains on login page.
    """
    # Step 2: Click on username input to trigger focus
    await login_page.username_input_field.click()
    
    # Step 3: Click on password input (blur username field)
    await login_page.password_input_field.click()
    
    # Step 4: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 5: Click login button and wait for validation
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Username input is still visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed"


@pytest.mark.asyncio
async def test_tc_002_005(login_page):
    """
    TEST CASE TC_002_005: Verify login fails with whitespace username.
    
    Type: Boundary
    Test Data: {"username": "   ", "password": "admin123"}
    
    Expected Result: Validation error displayed for username field and user remains on login page.
    """
    # Step 2: Fill username with whitespace only
    await login_page.username_input_field.fill(WHITESPACE_INPUT)
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for validation
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Username input is still visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for whitespace username"


@pytest.mark.asyncio
async def test_tc_002_006(login_page):
    """
    TEST CASE TC_002_006: Verify login fails with empty password.
    
    Type: Boundary
    Test Data: {"username": "Admin", "password": ""}
    
    Expected Result: Validation error 'Required' displayed for password field and user remains on login page.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Click on password input (no fill, leave empty)
    await login_page.password_input_field.click()
    
    # Step 4: Click login button and wait for validation
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Password input is still visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for empty password"


@pytest.mark.asyncio
async def test_tc_002_007(login_page):
    """
    TEST CASE TC_002_007: Verify login fails with whitespace password.
    
    Type: Boundary
    Test Data: {"username": "Admin", "password": "   "}
    
    Expected Result: Validation error displayed for password field and user remains on login page.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Fill password with whitespace only
    await login_page.password_input_field.fill(WHITESPACE_INPUT)
    
    # Step 4: Click login button and wait for validation
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Password input is still visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assertion 3: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for whitespace password"


@pytest.mark.asyncio
async def test_tc_002_008(login_page):
    """
    TEST CASE TC_002_008: Verify login fails with empty username and password.
    
    Type: Boundary
    Test Data: {"username": "", "password": ""}
    
    Expected Result: Validation errors displayed for both fields and user remains on login page.
    """
    # Step 2: Click on username input (to trigger focus)
    await login_page.username_input_field.click()
    
    # Step 3: Click on password input (blur username field, leave both empty)
    await login_page.password_input_field.click()
    
    # Step 4: Click login button and wait for validation
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Username input is still visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 3: Password input is still visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assertion 4: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text) > 0, "Validation error should be displayed for empty username and password"