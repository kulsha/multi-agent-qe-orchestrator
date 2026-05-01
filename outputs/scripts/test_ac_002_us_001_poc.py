import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage


# ============================================================================
# AC_002 - AC_002
# ============================================================================

@pytest.mark.asyncio
async def test_tc_001_008():
    """
    TC_001_008: Verify successful redirect to dashboard with valid credentials
    
    Positive test case that verifies a user can successfully login with
    valid credentials and is redirected to the dashboard with proper URL
    and visibility of dashboard header, while no error message is shown.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=Admin
        await login_page.fill_username("Admin")
        
        # Step 4: fill on password_input value=admin123
        await login_page.fill_password("admin123")
        
        # Step 5: click on login_button
        await login_page.click_login_button()
        
        # Step 6: wait on dashboard_header value=visible
        await expect(page.locator(login_page.dashboard_header)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/dashboard'
        await expect(page).to_have_url(re.compile(r'/dashboard'))
        
        # Assert element_visible — target='dashboard_header' value=''
        await expect(page.locator(login_page.dashboard_header)).to_be_visible()
        
        # Assert element_hidden — target='error_message' value=''
        await expect(page.locator(login_page.error_message)).to_be_hidden()
        
        # Assert not_url_contains — target='current_url' value='/auth/login'
        await expect(page).not_to_have_url(re.compile(r'/auth/login'))
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_009():
    """
    TC_001_009: Verify 'Invalid credentials' error message with invalid username
    
    Negative test case that verifies login fails with invalid username
    and displays the exact error message 'Invalid credentials'.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=invaliduser
        await login_page.fill_username("invaliduser")
        
        # Step 4: fill on password_input value=admin123
        await login_page.fill_password("admin123")
        
        # Step 5: click on login_button
        await login_page.click_login_button()
        
        # Step 6: wait on error_message value=visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='error_message' value=''
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assert text_equals — target='error_message' value='Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_have_text("Invalid credentials")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_010():
    """
    TC_001_010: Verify 'Invalid credentials' error message with incorrect password
    
    Negative test case that verifies login fails with incorrect password
    and displays the exact error message 'Invalid credentials'.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=Admin
        await login_page.fill_username("Admin")
        
        # Step 4: fill on password_input value=wrongpassword
        await login_page.fill_password("wrongpassword")
        
        # Step 5: click on login_button
        await login_page.click_login_button()
        
        # Step 6: wait on error_message value=visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='error_message' value=''
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assert text_equals — target='error_message' value='Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_have_text("Invalid credentials")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_011():
    """
    TC_001_011: Verify validation feedback with empty username field
    
    Boundary test case that verifies validation error is displayed when
    username field is left empty, indicating the field is required.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on password_input value=admin123
        await login_page.fill_password("admin123")
        
        # Step 4: click on login_button
        await login_page.click_login_button()
        
        # Step 5: wait on username_validation_error value=visible
        await expect(page.locator(login_page.username_validation_error)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='username_validation_error' value=''
        await expect(page.locator(login_page.username_validation_error)).to_be_visible()
        
        # Assert text_contains — target='username_validation_error' value='Required'
        await expect(page.locator(login_page.username_validation_error)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_012():
    """
    TC_001_012: Verify validation feedback with empty password field
    
    Boundary test case that verifies validation error is displayed when
    password field is left empty, indicating the field is required.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=Admin
        await login_page.fill_username("Admin")
        
        # Step 4: click on login_button
        await login_page.click_login_button()
        
        # Step 5: wait on password_validation_error value=visible
        await expect(page.locator(login_page.password_validation_error)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='password_validation_error' value=''
        await expect(page.locator(login_page.password_validation_error)).to_be_visible()
        
        # Assert text_contains — target='password_validation_error' value='Required'
        await expect(page.locator(login_page.password_validation_error)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_013():
    """
    TC_001_013: Verify validation feedback with both fields empty
    
    Boundary test case that verifies validation errors are displayed for
    both username and password fields when both are left empty.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: click on login_button
        await login_page.click_login_button()
        
        # Step 4: wait on username_validation_error value=visible
        await expect(page.locator(login_page.username_validation_error)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='username_validation_error' value=''
        await expect(page.locator(login_page.username_validation_error)).to_be_visible()
        
        # Assert element_visible — target='password_validation_error' value=''
        await expect(page.locator(login_page.password_validation_error)).to_be_visible()
        
        # Assert text_contains — target='username_validation_error' value='Required'
        await expect(page.locator(login_page.username_validation_error)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_014():
    """
    TC_001_014: Verify validation feedback with whitespace-only username
    
    Boundary test case that verifies error message is displayed when
    username contains only whitespace, indicating invalid credentials.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=(whitespace)
        await login_page.fill_username("   ")
        
        # Step 4: fill on password_input value=admin123
        await login_page.fill_password("admin123")
        
        # Step 5: click on login_button
        await login_page.click_login_button()
        
        # Step 6: wait on error_message value=visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='error_message' value=''
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assert text_contains — target='error_message' value='Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_contain_text("Invalid credentials")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_015():
    """
    TC_001_015: Verify validation feedback with whitespace-only password
    
    Boundary test case that verifies error message is displayed when
    password contains only whitespace, indicating invalid credentials.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=Admin
        await login_page.fill_username("Admin")
        
        # Step 4: fill on password_input value=(whitespace)
        await login_page.fill_password("   ")
        
        # Step 5: click on login_button
        await login_page.click_login_button()
        
        # Step 6: wait on error_message value=visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='error_message' value=''
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assert text_contains — target='error_message' value='Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_contain_text("Invalid credentials")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_016():
    """
    TC_001_016: Verify validation feedback with both fields containing whitespace only
    
    Boundary test case that verifies error message is displayed when
    both username and password contain only whitespace.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 3: fill on username_input value=(whitespace)
        await login_page.fill_username("   ")
        
        # Step 4: fill on password_input value=(whitespace)
        await login_page.fill_password("   ")
        
        # Step 5: click on login_button
        await login_page.click_login_button()
        
        # Step 6: wait on error_message value=visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_