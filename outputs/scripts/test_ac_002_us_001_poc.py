import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.login import Login


# ============================================================================
# AC_002: AC_002
# ============================================================================

@pytest.mark.asyncio
async def test_tc_002_001():
    """
    TEST CASE TC_002_001: Verify successful login with valid credentials
    Type: Positive
    Test Data: {"username": "Admin", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='' value='/dashboard' — URL contains /dashboard
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill username
        await login_page.fill_username("Admin")
        
        # Step 3: Fill password
        await login_page.fill_password("admin123")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL contains /dashboard
        await expect(page).to_have_url(re.compile(r'/dashboard'))
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_002():
    """
    TEST CASE TC_002_002: Verify login fails with invalid username
    Type: Negative
    Test Data: {"username": "invaliduser", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=invaliduser
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert text_equals — target='error_message' value='Invalid credentials' — Error message 'Invalid credentials' is displayed
      Assert element_visible — target='username_input' value='' — User remains on the login page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill invalid username
        await login_page.fill_username("invaliduser")
        
        # Step 3: Fill password
        await login_page.fill_password("admin123")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: Error message text equals 'Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_have_text("Invalid credentials")
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_003():
    """
    TEST CASE TC_002_003: Verify login fails with valid username and incorrect password
    Type: Negative
    Test Data: {"username": "Admin", "password": "wrongpassword"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=wrongpassword
      Step 4: click on 'login_button'
    
    Assertions:
      Assert text_equals — target='error_message' value='Invalid credentials' — Error message 'Invalid credentials' is displayed
      Assert element_visible — target='username_input' value='' — User remains on the login page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill username
        await login_page.fill_username("Admin")
        
        # Step 3: Fill incorrect password
        await login_page.fill_password("wrongpassword")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: Error message text equals 'Invalid credentials'
        await expect(page.locator(login_page.error_message)).to_have_text("Invalid credentials")
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_004():
    """
    TEST CASE TC_002_004: Verify login fails with empty username
    Type: Boundary
    Test Data: {"username": "", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: click on 'username_input'
      Step 3: click on 'password_input'
      Step 4: fill on 'password_input' value=admin123
      Step 5: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on login page after failed login attempt
      Assert element_visible — target='username_error_message' value='' — Validation error message is displayed for empty username field
      Assert text_contains — target='username_error_message' value='Required' — Error message contains 'Required' text indicating mandatory field validation
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Click on username input
        await page.locator(login_page.username_input).click()
        
        # Step 3: Click on password input
        await page.locator(login_page.password_input).click()
        
        # Step 4: Fill password
        await login_page.fill_password("admin123")
        
        # Step 5: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Username error message is visible
        await expect(page.locator(login_page.username_error_message)).to_be_visible()
        
        # Assertion 3: Username error message contains 'Required'
        await expect(page.locator(login_page.username_error_message)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_005():
    """
    TEST CASE TC_002_005: Verify login fails with whitespace username
    Type: Boundary
    Test Data: {"username": "(whitespace)", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=(whitespace)
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on login page after failed login attempt
      Assert element_visible — target='username_error_message' value='' — Validation error message is displayed for invalid username
      Assert text_contains — target='username_error_message' value='Required' — Error message indicates validation failure for whitespace username
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill username with whitespace
        await login_page.fill_username("   ")
        
        # Step 3: Fill password
        await login_page.fill_password("admin123")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Username error message is visible
        await expect(page.locator(login_page.username_error_message)).to_be_visible()
        
        # Assertion 3: Username error message contains 'Required'
        await expect(page.locator(login_page.username_error_message)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_006():
    """
    TEST CASE TC_002_006: Verify login fails with empty password
    Type: Boundary
    Test Data: {"username": "Admin", "password": ""}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: click on 'password_input'
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on login page after failed login attempt
      Assert element_visible — target='password_error_message' value='' — Validation error message is displayed for empty password field
      Assert text_contains — target='password_error_message' value='Required' — Error message contains 'Required' text indicating mandatory field validation
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill username
        await login_page.fill_username("Admin")
        
        # Step 3: Click on password input
        await page.locator(login_page.password_input).click()
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Password error message is visible
        await expect(page.locator(login_page.password_error_message)).to_be_visible()
        
        # Assertion 3: Password error message contains 'Required'
        await expect(page.locator(login_page.password_error_message)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_007():
    """
    TEST CASE TC_002_007: Verify login fails with whitespace password
    Type: Boundary
    Test Data: {"username": "Admin", "password": "(whitespace)"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=(whitespace)
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on login page after failed login attempt
      Assert element_visible — target='password_error_message' value='' — Validation error message is displayed for invalid password
      Assert text_contains — target='password_error_message' value='Required' — Error message indicates validation failure for whitespace password
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill username
        await login_page.fill_username("Admin")
        
        # Step 3: Fill password with whitespace
        await login_page.fill_password("   ")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Password error message is visible
        await expect(page.locator(login_page.password_error_message)).to_be_visible()
        
        # Assertion 3: Password error message contains 'Required'
        await expect(page.locator(login_page.password_error_message)).to_contain_text("Required")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_002_008():
    """
    TEST CASE TC_002_008: Verify login fails with empty username and password
    Type: Boundary
    Test Data: {"username": "", "password": ""}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: click on 'username_input'
      Step 3: click on 'password_input'
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on login page after failed login attempt
      Assert element_visible — target='username_error_message' value='' — Validation error message is displayed for empty username field
      Assert element_visible — target='password_error_message' value='' — Validation error message is displayed for empty password field
      Assert text_contains — target='username_error_message' value='Required' — Username error message contains 'Required' text
      Assert text_contains — target='password_error_message' value='Required' — Password error message contains 'Required' text
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Click on username input
        await page.locator(login_page.username_input).click()
        
        # Step 3: Click on password input
        await page.locator(login_page.password_input).click()
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Username error message is visible
        await expect(page.locator(login_page.username_error_message)).to_be_visible()
        
        # Assertion 3: Password error message is visible
        await expect(page.locator(login_page.password_error_message)).to_be_visible()
        
        # Assertion 4: Username error message contains 'Required'
        await expect(page.locator(login_page.username_error_message)).to_contain_text("Required")
        
        # Assertion 5: Password error message contains 'Required'
        await expect(page.locator(login_page.password_error_message)).to_contain_text("Required")
        
        await browser.close()