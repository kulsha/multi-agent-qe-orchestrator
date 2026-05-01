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
async def test_tc_001_008(login_page: LoginPage):
    """
    TC_001_008: Verify successful redirect to dashboard with valid credentials
    
    Positive test case that verifies a user can successfully login with
    valid credentials and is redirected to the dashboard with proper URL
    and visibility of dashboard header, while no error message is shown.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Perform login with valid credentials
    await login_page.login(VALID_USERNAME, VALID_PASSWORD)
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 6: Verify user navigation element is visible (dashboard loaded)
    await expect(login_page.userNameNav).to_be_visible()
    
    # Assertions
    # Assert URL contains /dashboard
    await expect(login_page.page).to_have_url(re.compile(DASHBOARD_URL_PATTERN))
    
    # Assert user navigation header is visible
    await expect(login_page.userNameNav).to_be_visible()
    
    # Assert error message is hidden
    await expect(login_page.errorMessage).to_be_hidden()
    
    # Assert URL does not contain /auth/login
    await expect(login_page.page).not_to_have_url(re.compile(LOGIN_URL_PATTERN))


@pytest.mark.asyncio
async def test_tc_001_009(login_page: LoginPage):
    """
    TC_001_009: Verify 'Invalid credentials' error message with invalid username
    
    Negative test case that verifies login fails with invalid username
    and displays the error message 'Invalid credentials'.
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


@pytest.mark.asyncio
async def test_tc_001_010(login_page: LoginPage):
    """
    TC_001_010: Verify 'Invalid credentials' error message with incorrect password
    
    Negative test case that verifies login fails with incorrect password
    and displays the error message 'Invalid credentials'.
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


@pytest.mark.asyncio
async def test_tc_001_011(login_page: LoginPage):
    """
    TC_001_011: Verify validation feedback with empty username field
    
    Boundary test case that verifies validation error is displayed when
    username field is left empty, indicating the field is required.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3: Fill password only
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
    
    # Assert error message contains Required text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_REQUIRED in error_text


@pytest.mark.asyncio
async def test_tc_001_012(login_page: LoginPage):
    """
    TC_001_012: Verify validation feedback with empty password field
    
    Boundary test case that verifies validation error is displayed when
    password field is left empty, indicating the field is required.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3: Fill username only
    await login_page.username_input_field.fill(VALID_USERNAME)
    
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
    
    # Assert error message contains Required text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_REQUIRED in error_text


@pytest.mark.asyncio
async def test_tc_001_013(login_page: LoginPage):
    """
    TC_001_013: Verify validation feedback with both fields empty
    
    Boundary test case that verifies validation errors are displayed for
    both username and password fields when both are left empty.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3: Click login button without filling any fields
    await login_page.login_button_locator.click()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 4: Wait for error message to be visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assertions
    # Assert URL remains on login page
    await expect(login_page.page).to_have_url(re.compile(LOGIN_URL_PATTERN))
    
    # Assert error message is visible
    await expect(login_page.errorMessage).to_be_visible()
    
    # Assert error message contains Required text
    error_text = await login_page.get_errorMessage_text()
    assert ERROR_REQUIRED in error_text


@pytest.mark.asyncio
async def test_tc_001_014(login_page: LoginPage):
    """
    TC_001_014: Verify validation feedback with whitespace-only username
    
    Boundary test case that verifies error message is displayed when
    username contains only whitespace, indicating invalid credentials.
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
    assert ERROR_INVALID_CREDENTIALS in error_text.strip()


@pytest.mark.asyncio
async def test_tc_001_015(login_page: LoginPage):
    """
    TC_001_015: Verify validation feedback with whitespace-only password
    
    Boundary test case that verifies error message is displayed when
    password contains only whitespace, indicating invalid credentials.
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
    assert ERROR_INVALID_CREDENTIALS in error_text.strip()


@pytest.mark.asyncio
async def test_tc_001_016(login_page: LoginPage):
    """
    TC_001_016: Verify validation feedback with both fields containing whitespace only
    
    Boundary test case that verifies error message is displayed when
    both username and password contain only whitespace.
    """
    # Step 1: Navigate to login page
    await login_page.navigate()
    await login_page.page.wait_for_load_state("networkidle")
    
    # Step 2: Wait for username input to be visible
    await expect(login_page.username_input_field).to_be_visible()
    
    # Step 3-5: Attempt login with both fields containing whitespace
    await login_page.login(WHITESPACE, WHITESPACE)
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