import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.login import LoginPage


# Test data constants
VALID_USERNAME = "Admin"
VALID_PASSWORD = "admin123"
INVALID_USERNAME = "invaliduser"
INVALID_PASSWORD = "wrongpassword"
TEST_USERNAME = "testusername"
TEST_PASSWORD = "testpassword"
DASHBOARD_URL_PATTERN = re.compile(r'/dashboard')
LOGIN_PAGE_URL_PATTERN = re.compile(r'/auth/login')


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
async def test_tc_003_001(login_page):
    """
    TEST CASE TC_003_001: Verify login page elements visibility.
    
    Type: UI
    
    Expected Result: All login page elements (username input, password input, login button, logo) are visible.
    """
    # Assertion 1: Username input field is visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 2: Password input field is visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assertion 3: Login button is visible
    await expect(login_page.loginButton).to_be_visible()
    
    # Assertion 4: OrangeHRM logo is visible
    await expect(login_page.logo).to_be_visible()


@pytest.mark.asyncio
async def test_tc_003_002(login_page):
    """
    TEST CASE TC_003_002: Verify username input field functionality.
    
    Type: UI
    Test Data: {"username": "testusername"}
    
    Expected Result: Username input field accepts and displays entered text.
    """
    # Step 2: Fill username input
    await login_page.username_input_field.fill(TEST_USERNAME)
    
    # Assertion 1: Username input field is visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assertion 2: Username input field contains the entered text
    await expect(login_page.username_input_field).to_have_value(TEST_USERNAME)


@pytest.mark.asyncio
async def test_tc_003_003(login_page):
    """
    TEST CASE TC_003_003: Verify password input field masking.
    
    Type: UI
    Test Data: {"password": "testpassword"}
    
    Expected Result: Password input field has type='password' for character masking and accepts input.
    """
    # Step 2: Fill password input
    await login_page.password_input_field.fill(TEST_PASSWORD)
    
    # Assertion 1: Password input field is visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assertion 2: Password input field has type attribute set to 'password'
    await expect(login_page.password_input_field).to_have_attribute("type", "password")


@pytest.mark.asyncio
async def test_tc_003_004(login_page):
    """
    TEST CASE TC_003_004: Verify Login button functionality with valid credentials.
    
    Type: Positive
    Test Data: {"username": "Admin", "password": "admin123"}
    
    Expected Result: User is redirected to dashboard and no longer on login page.
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
    
    # Assertion 2: URL does not contain /auth/login
    await expect(login_page.page).not_to_have_url(LOGIN_PAGE_URL_PATTERN)


@pytest.mark.asyncio
async def test_tc_003_005(login_page):
    """
    TEST CASE TC_003_005: Verify error handling for invalid username.
    
    Type: Negative
    Test Data: {"username": "invaliduser", "password": "admin123"}
    
    Expected Result: User remains on login page and error message indicating invalid credentials is displayed.
    """
    # Step 2: Fill invalid username
    await login_page.username_input_field.fill(INVALID_USERNAME)
    
    # Step 3: Fill password
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button and wait for error
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertion 3: Error message contains 'Invalid'
    await expect(login_page.errorMessage).to_contain_text("Invalid")
    
    # Additional assertion: Verify error message text content
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and "Invalid" in error_text, "Error message should contain 'Invalid' text"


@pytest.mark.asyncio
async def test_tc_003_006(login_page):
    """
    TEST CASE TC_003_006: Verify error handling for incorrect password.
    
    Type: Negative
    Test Data: {"username": "Admin", "password": "wrongpassword"}
    
    Expected Result: User remains on login page and error message indicating invalid credentials is displayed.
    """
    # Step 2: Fill username
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Step 3: Fill incorrect password
    await login_page.password_input_field.fill(INVALID_PASSWORD)
    
    # Step 4: Click login button and wait for error
    await login_page.loginButton.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Assertion 1: URL contains /auth/login
    await expect(login_page.page).to_have_url(LOGIN_PAGE_URL_PATTERN)
    
    # Assertion 2: Error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertion 3: Error message contains 'Invalid'
    await expect(login_page.errorMessage).to_contain_text("Invalid")
    
    # Additional assertion: Verify error message text content
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and "Invalid" in error_text, "Error message should contain 'Invalid' text"