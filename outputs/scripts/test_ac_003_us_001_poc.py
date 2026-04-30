import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.login import Login


# ============================================================================
# AC_003: AC_003
# ============================================================================

@pytest.mark.asyncio
async def test_tc_003_001():
    """
    TEST CASE TC_003_001: Verify login page elements visibility
    Type: UI
    Test Data: {}
    
    Actions:
      Step 1: navigate on 'target_url'
    
    Assertions:
      Assert element_visible — target='username_input' value='' — Username input field is visible on the login page
      Assert element_visible — target='password_input' value='' — Password input field is visible on the login page
      Assert element_visible — target='login_button' value='' — Login button is visible on the login page
      Assert element_visible — target='orangehrm_logo' value='' — OrangeHRM logo is visible on the login page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Assertion 1: Username input field is visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Assertion 2: Password input field is visible
        await expect(page.locator(login_page.password_input)).to_be_visible()
        
        # Assertion 3: Login button is visible
        await expect(page.locator(login_page.login_button)).to_be_visible()
        
        # Assertion 4: OrangeHRM logo is visible
        await expect(page.locator(login_page.orangehrm_logo)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_003_002():
    """
    TEST CASE TC_003_002: Verify username input field functionality
    Type: UI
    Test Data: {"username": "testusername"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=testusername
      Step 3: get_attr on 'username_input' value=value
    
    Assertions:
      Assert element_visible — target='username_input' value='' — Username input field is visible on the login page
      Assert attr_equals — target='username_input' value='testusername' — Username input field contains the entered text 'testusername'
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill username input
        await login_page.fill_username("testusername")
        
        # Step 3: Get attribute (value) from username input
        # (This is implicitly checked in the assertion)
        
        # Assertion 1: Username input field is visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Assertion 2: Username input field contains the entered text
        await expect(page.locator(login_page.username_input)).to_have_attribute("value", "testusername")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_003_003():
    """
    TEST CASE TC_003_003: Verify password input field masking
    Type: UI
    Test Data: {"password": "testpassword"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'password_input' value=testpassword
      Step 3: get_attr on 'password_input' value=type
    
    Assertions:
      Assert element_visible — target='password_input' value='' — Password input field is visible on the login page
      Assert attr_equals — target='password_input' value='password' — Password input field has type attribute set to 'password' for character masking
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Fill password input
        await login_page.fill_password("testpassword")
        
        # Step 3: Get attribute (type) from password input
        # (This is implicitly checked in the assertion)
        
        # Assertion 1: Password input field is visible
        await expect(page.locator(login_page.password_input)).to_be_visible()
        
        # Assertion 2: Password input field has type attribute set to 'password'
        await expect(page.locator(login_page.password_input)).to_have_attribute("type", "password")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_003_004():
    """
    TEST CASE TC_003_004: Verify Login button functionality
    Type: Positive
    Test Data: {"username": "Admin", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/dashboard' — User is redirected to the dashboard after successful login
      Assert not_url_contains — target='current_url' value='/auth/login' — User is no longer on the login page
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
        
        # Assertion 2: URL does not contain /auth/login
        await expect(page).not_to_have_url(re.compile(r'/auth/login'))
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_003_005():
    """
    TEST CASE TC_003_005: Verify error handling for invalid credentials
    Type: Negative
    Test Data: {"username": "invaliduser", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=invaliduser
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on the login page after failed login
      Assert element_visible — target='error_message' value='' — Error message is displayed for invalid credentials
      Assert text_contains — target='error_message' value='Invalid' — Error message indicates invalid credentials
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
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Error message is visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertion 3: Error message contains 'Invalid'
        await expect(page.locator(login_page.error_message)).to_contain_text("Invalid")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_003_006():
    """
    TEST CASE TC_003_006: Verify error handling for valid username and incorrect password
    Type: Negative
    Test Data: {"username": "Admin", "password": "wrongpassword"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=wrongpassword
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='current_url' value='/auth/login' — User remains on the login page after failed login
      Assert element_visible — target='error_message' value='' — Error message is displayed for incorrect password
      Assert text_contains — target='error_message' value='Invalid' — Error message indicates invalid credentials or authentication failure
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
        
        # Assertion 1: URL contains /auth/login
        await expect(page).to_have_url(re.compile(r'/auth/login'))
        
        # Assertion 2: Error message is visible
        await expect(page.locator(login_page.error_message)).to_be_visible()
        
        # Assertion 3: Error message contains 'Invalid'
        await expect(page.locator(login_page.error_message)).to_contain_text("Invalid")
        
        await browser.close()