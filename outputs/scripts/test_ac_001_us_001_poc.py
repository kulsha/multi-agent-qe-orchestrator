import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage


# ============================================================================
# AC_001 - AC_001
# ============================================================================

@pytest.mark.asyncio
async def test_tc_001_001():
    """
    TC_001_001: Verify successful login with valid credentials
    
    Positive test case that verifies a user can successfully login with
    valid credentials (username: Admin, password: admin123) and is redirected
    to the dashboard with the dashboard header visible.
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
        
        # Assert text_contains — target='dashboard_header' value='Dashboard'
        await expect(page.locator(login_page.dashboard_header)).to_contain_text("Dashboard")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_002():
    """
    TC_001_002: Verify login fails with invalid username
    
    Negative test case that verifies login fails when an invalid username
    is provided (invaliduser) with correct password, and user remains on
    login page with error message displayed.
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
        
        # Assert text_contains — target='error_message' value='Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_contain_text("Invalid credentials")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_003():
    """
    TC_001_003: Verify login fails with incorrect password
    
    Negative test case that verifies login fails when correct username
    (Admin) is provided with incorrect password (wrongpassword), and user
    remains on login page with error message displayed.
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
        
        # Assert text_contains — target='error_message' value='Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_contain_text("Invalid credentials")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_004():
    """
    TC_001_004: Verify login fails with empty username field
    
    Boundary test case that verifies login fails when username field is
    left empty, and a validation error message is displayed indicating
    the field is required.
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
        
        # Step 5: wait on username_error value=visible
        await expect(page.locator(login_page.username_error)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='username_error' value=''
        await expect(page.locator(login_page.username_error)).to_be_visible()
        
        # Assert text_contains — target='username_error' value='Required'
        await expect(page.locator(login_page.username_error)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_005():
    """
    TC_001_005: Verify login fails with empty password field
    
    Boundary test case that verifies login fails when password field is
    left empty, and a validation error message is displayed indicating
    the field is required.
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
        
        # Step 5: wait on password_error value=visible
        await expect(page.locator(login_page.password_error)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/auth/login'
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='password_error' value=''
        await expect(page.locator(login_page.password_error)).to_be_visible()
        
        # Assert text_contains — target='password_error' value='Required'
        await expect(page.locator(login_page.password_error)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_006():
    """
    TC_001_006: Verify login fails with whitespace-only username
    
    Boundary test case that verifies login fails when username contains
    only whitespace characters, and error message is displayed indicating
    invalid credentials.
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
async def test_tc_001_007():
    """
    TC_001_007: Verify login fails with whitespace-only password
    
    Boundary test case that verifies login fails when password contains
    only whitespace characters, and error message is displayed indicating
    invalid credentials.
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