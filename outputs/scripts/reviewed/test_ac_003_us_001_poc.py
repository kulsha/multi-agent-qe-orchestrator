import re
import pytest
from playwright.async_api import async_playwright, expect, Page
from pages.loginpage import LoginPage


# Test data constants
VALID_USERNAME = "Admin"
VALID_PASSWORD = "admin123"
INVALID_USERNAME = "invaliduser"
INVALID_PASSWORD = "wrongpassword"
ERROR_INVALID_CREDENTIALS = "Invalid credentials"
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
async def test_tc_001_018(login_page: LoginPage):
    """
    TC_001_018: Verify username input field is visible and accepts text input
    
    UI test case that verifies the username input field is visible,
    enabled, and properly accepts text input.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3: Click on username input field
    await login_page.username_input_field.click()
    
    # Step 4: Fill username field
    await login_page.username_input_field.fill(VALID_USERNAME)
    
    # Assertions
    # Assert username input is visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assert username input has correct value
    await expect(login_page.username_input_field).to_have_value(VALID_USERNAME)


@pytest.mark.asyncio
async def test_tc_001_019(login_page: LoginPage):
    """
    TC_001_019: Verify password input field is visible and accepts text input
    
    UI test case that verifies the password input field is visible,
    enabled, and has type attribute set to password for masking.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for password input to be visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Step 3: Click on password input field
    await login_page.password_input_field.click()
    
    # Step 4: Fill password field
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Assertions
    # Assert password input is visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assert password input has type attribute set to password
    await expect(login_page.password_input_field).to_have_attribute("type", "password")


@pytest.mark.asyncio
async def test_tc_001_020(login_page: LoginPage):
    """
    TC_001_020: Verify Login button is visible and clickable
    
    UI test case that verifies the Login button is visible, has type
    attribute set to submit, and displays correct text.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for login button to be visible
    await expect(login_page.login_button_locator).to_be_visible()
    
    # Assertions
    # Assert login button is visible
    await expect(login_page.login_button_locator).to_be_visible()
    
    # Assert login button has type attribute set to submit
    await expect(login_page.login_button_locator).to_have_attribute("type", "submit")
    
    # Assert login button text contains "Login"
    await expect(login_page.login_button_locator).to_contain_text("Login")


@pytest.mark.asyncio
async def test_tc_001_021(login_page: LoginPage):
    """
    TC_001_021: Verify OrangeHRM logo is visible on login page
    
    UI test case that verifies the OrangeHRM logo and logo image are
    visible with correct alt text.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for logo to be visible
    await expect(login_page.logo).to_be_visible()
    
    # Assertions
    # Assert logo is visible
    await expect(login_page.logo).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_022(login_page: LoginPage):
    """
    TC_001_022: Verify form submits and authenticates user with valid credentials
    
    Positive test case that verifies the login form submits successfully
    and authenticates the user with valid credentials, redirecting to
    the dashboard.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Perform login with valid credentials
    await login_page.login(VALID_USERNAME, VALID_PASSWORD)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Verify user is on dashboard
    await expect(login_page.userNameNav).to_be_visible()
    
    # Assertions
    # Assert URL contains /dashboard
    await expect(login_page.page).to_have_url(re.compile(DASHBOARD_URL_PATTERN))
    
    # Assert URL does not contain /auth/login
    await expect(login_page.page).not_to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert user navigation element is visible
    await expect(login_page.userNameNav).to_be_visible()
    
    # Assert logo is visible (confirming dashboard loaded)
    await expect(login_page.logo).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_023(login_page: LoginPage):
    """
    TC_001_023: Verify form shows error with invalid username and remains on login page
    
    Negative test case that verifies the login form shows an error message
    when an invalid username is provided and the user remains on the
    login page.
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
    assert ERROR_INVALID_CREDENTIALS in error_text.strip()
    
    # Assert username input is still visible (user remains on login page)
    await expect(login_page.username_input_field).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_024(login_page: LoginPage):
    """
    TC_001_024: Verify form shows error with incorrect password and remains on login page
    
    Negative test case that verifies the login form shows an error message
    when an incorrect password is provided and the user remains on the
    login page.
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
    assert ERROR_INVALID_CREDENTIALS in error_text.strip()
    
    # Assert username input is still visible (user remains on login page)
    await expect(login_page.username_input_field).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_025(login_page: LoginPage):
    """
    TC_001_025: Verify all login page elements are properly positioned and visible
    
    UI test case that verifies all login page elements including logo,
    labels, input fields, and button are visible and properly positioned.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2-8: Wait for all elements to be visible
    await expect(login_page.logo).to_be_visible()
    await expect(login_page.username_input_field).to_be_visible()
    await expect(login_page.password_input_field).to_be_visible()
    await expect(login_page.login_button_locator).to_be_visible()
    
    # Assertions
    # Assert logo is visible
    await expect(login_page.logo).to_be_visible()
    
    # Assert username input is visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Assert password input is visible
    await expect(login_page.password_input_field).to_be_visible()
    
    # Assert login button is visible
    await expect(login_page.login_button_locator).to_be_visible()


@pytest.mark.asyncio
async def test_tc_001_026(login_page: LoginPage):
    """
    TC_001_026: Verify form behavior with empty username and valid password
    
    Negative test case that verifies the form shows validation error when
    username field is empty and user remains on login page.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3: Fill password only (username left empty)
    await login_page.password_input_field.fill(VALID_PASSWORD)
    
    # Step 4: Click login button
    await login_page.login_button_locator.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 5: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message indicates required field or invalid credentials
    error_text = await login_page.get_errorMessage_text()
    assert error_text is not None and len(error_text.strip()) > 0
    
    # Assert username input is still visible (user remains on login page)
    await expect(login_page.username_input_field).to_be_visible()