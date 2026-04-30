import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.login import Login


# ============================================================================
# AC_001: AC_001
# ============================================================================

@pytest.mark.asyncio
async def test_tc_001_001():
    """
    TEST CASE TC_001_001: Verify successful login with valid credentials
    Type: Positive
    Test Data: {"username": "Admin", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert url_contains — target='' value='/dashboard' — User is redirected to the dashboard
      Assert element_visible — target='username_navbar' value='' — User name is visible in the top navigation bar
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
        
        # Assertion 2: Username is visible in navbar
        await expect(page.locator(login_page.username_navbar)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_002():
    """
    TEST CASE TC_001_002: Verify login fails with invalid username
    Type: Negative
    Test Data: {"username": "invaliduser", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=invaliduser
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert not_url_contains — target='' value='/dashboard' — URL does not contain /dashboard
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
        
        # Assertion 1: URL does not contain /dashboard
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_003():
    """
    TEST CASE TC_001_003: Verify login fails with incorrect password
    Type: Negative
    Test Data: {"username": "Admin", "password": "wrongpassword"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=wrongpassword
      Step 4: click on 'login_button'
    
    Assertions:
      Assert not_url_contains — target='' value='/dashboard' — URL does not contain /dashboard
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
        
        # Assertion 1: URL does not contain /dashboard
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_004():
    """
    TEST CASE TC_001_004: Verify login fails with empty username
    Type: Boundary
    Test Data: {"username": "", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: clear on 'username_input'
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert not_url_contains — target='' value='/dashboard' — URL does not contain /dashboard
      Assert element_visible — target='username_input' value='' — User remains on the login page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = Login(page)
        
        # Step 1: Navigate to target URL
        await login_page.navigate()
        
        # Step 2: Clear username input
        await login_page.clear_username()
        
        # Step 3: Fill password
        await login_page.fill_password("admin123")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL does not contain /dashboard
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_005():
    """
    TEST CASE TC_001_005: Verify login fails with whitespace username
    Type: Boundary
    Test Data: {"username": "(whitespace)", "password": "admin123"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=(whitespace)
      Step 3: fill on 'password_input' value=admin123
      Step 4: click on 'login_button'
    
    Assertions:
      Assert not_url_contains — target='' value='/dashboard' — URL does not contain /dashboard
      Assert element_visible — target='username_input' value='' — User remains on the login page
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
        
        # Assertion 1: URL does not contain /dashboard
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_006():
    """
    TEST CASE TC_001_006: Verify login fails with empty password
    Type: Boundary
    Test Data: {"username": "Admin", "password": ""}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: clear on 'password_input'
      Step 4: click on 'login_button'
    
    Assertions:
      Assert not_url_contains — target='' value='/dashboard' — URL does not contain /dashboard
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
        
        # Step 3: Clear password input
        await login_page.clear_password()
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL does not contain /dashboard
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_007():
    """
    TEST CASE TC_001_007: Verify login fails with whitespace password
    Type: Boundary
    Test Data: {"username": "Admin", "password": "(whitespace)"}
    
    Actions:
      Step 1: navigate on 'target_url'
      Step 2: fill on 'username_input' value=Admin
      Step 3: fill on 'password_input' value=(whitespace)
      Step 4: click on 'login_button'
    
    Assertions:
      Assert not_url_contains — target='' value='/dashboard' — URL does not contain /dashboard
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
        
        # Step 3: Fill password with whitespace
        await login_page.fill_password("   ")
        
        # Step 4: Click login button
        await login_page.click_login_button()
        
        # Assertion 1: URL does not contain /dashboard
        await expect(page).not_to_have_url(re.compile(r'/dashboard'))
        
        # Assertion 2: Username input is visible (user remains on login page)
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        await browser.close()