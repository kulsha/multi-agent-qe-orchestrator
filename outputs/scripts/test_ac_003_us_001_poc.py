import re
import pytest
from playwright.async_api import async_playwright, expect
from pages.loginpage import LoginPage


# ============================================================================
# AC_003 - AC_003
# ============================================================================

@pytest.mark.asyncio
async def test_tc_001_018():
    """
    TC_001_018: Verify username input field is visible and accepts text input
    
    UI test case that verifies the username input field is visible,
    enabled, and properly accepts text input.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_title value=visible
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
        # Step 3: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 4: click on username_input
        await page.locator(login_page.username_input).click()
        
        # Step 5: fill on username_input value=Admin
        await login_page.fill_username("Admin")
        
        # Assertions
        # Assert element_visible — target='username_input' value=''
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Assert attr_equals — target='username_input' value='Admin'
        await expect(page.locator(login_page.username_input)).to_have_attribute("value", "Admin")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_019():
    """
    TC_001_019: Verify password input field is visible and accepts text input
    
    UI test case that verifies the password input field is visible,
    enabled, and has type attribute set to password for masking.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_title value=visible
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
        # Step 3: wait on password_input value=visible
        await expect(page.locator(login_page.password_input)).to_be_visible()
        
        # Step 4: click on password_input
        await page.locator(login_page.password_input).click()
        
        # Step 5: fill on password_input value=admin123
        await login_page.fill_password("admin123")
        
        # Assertions
        # Assert element_visible — target='password_input' value=''
        await expect(page.locator(login_page.password_input)).to_be_visible()
        
        # Assert attr_equals — target='password_input' value='password'
        await expect(page.locator(login_page.password_input)).to_have_attribute("type", "password")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_020():
    """
    TC_001_020: Verify Login button is visible and clickable
    
    UI test case that verifies the Login button is visible, has type
    attribute set to submit, and displays correct text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_title value=visible
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
        # Step 3: wait on login_button value=visible
        await expect(page.locator(login_page.login_button)).to_be_visible()
        
        # Assertions
        # Assert element_visible — target='login_button' value=''
        await expect(page.locator(login_page.login_button)).to_be_visible()
        
        # Assert attr_equals — target='login_button' value='submit'
        await expect(page.locator(login_page.login_button)).to_have_attribute("type", "submit")
        
        # Assert text_contains — target='login_button' value='Login'
        await expect(page.locator(login_page.login_button)).to_contain_text("Login")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_021():
    """
    TC_001_021: Verify OrangeHRM logo is visible on login page
    
    UI test case that verifies the OrangeHRM logo and logo image are
    visible with correct alt text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_container value=visible
        await expect(page.locator(login_page.login_page_container)).to_be_visible()
        
        # Step 3: wait on orangehrm_logo value=visible
        await expect(page.locator(login_page.orangehrm_logo)).to_be_visible()
        
        # Assertions
        # Assert element_visible — target='orangehrm_logo' value=''
        await expect(page.locator(login_page.orangehrm_logo)).to_be_visible()
        
        # Assert element_visible — target='logo_image' value=''
        await expect(page.locator(login_page.logo_image)).to_be_visible()
        
        # Assert attr_equals — target='logo_image' value='orangehrm'
        await expect(page.locator(login_page.logo_image)).to_have_attribute("alt", "orangehrm")
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_022():
    """
    TC_001_022: Verify form submits and authenticates user with valid credentials
    
    Positive test case that verifies the login form submits successfully
    and authenticates the user with valid credentials, redirecting to
    the dashboard.
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
        
        # Step 6: wait on dashboard_container value=visible
        await expect(page.locator(login_page.dashboard_container)).to_be_visible()
        
        # Assertions
        # Assert url_contains — target='current_url' value='/dashboard'
        await expect(page).to_have_url(re.compile(r'/dashboard'))
        
        # Assert not_url_contains — target='current_url' value='/auth/login'
        await expect(page).not_to_have_url(re.compile(r'/auth/login'))
        
        # Assert element_visible — target='dashboard_container' value=''
        await expect(page.locator(login_page.dashboard_container)).to_be_visible()
        
        # Assert element_visible — target='dashboard_header' value=''
        await expect(page.locator(login_page.dashboard_header)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_023():
    """
    TC_001_023: Verify form shows error with invalid username and remains on login page
    
    Negative test case that verifies the login form shows an error message
    when an invalid username is provided and the user remains on the
    login page.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_title value=visible
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
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
        
        # Assert element_visible — target='login_page_title' value=''
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_024():
    """
    TC_001_024: Verify form shows error with incorrect password and remains on login page
    
    Negative test case that verifies the login form shows an error message
    when an incorrect password is provided and the user remains on the
    login page.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_title value=visible
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
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
        
        # Assert element_visible — target='login_page_title' value=''
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_025():
    """
    TC_001_025: Verify all login page elements are properly positioned and visible
    
    UI test case that verifies all login page elements including logo,
    labels, input fields, and button are visible and properly positioned.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_container value=visible
        await expect(page.locator(login_page.login_page_container)).to_be_visible()
        
        # Step 3: wait on orangehrm_logo value=visible
        await expect(page.locator(login_page.orangehrm_logo)).to_be_visible()
        
        # Step 4: wait on username_label value=visible
        await expect(page.locator(login_page.username_label)).to_be_visible()
        
        # Step 5: wait on username_input value=visible
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Step 6: wait on password_label value=visible
        await expect(page.locator(login_page.password_label)).to_be_visible()
        
        # Step 7: wait on password_input value=visible
        await expect(page.locator(login_page.password_input)).to_be_visible()
        
        # Step 8: wait on login_button value=visible
        await expect(page.locator(login_page.login_button)).to_be_visible()
        
        # Assertions
        # Assert element_visible — target='orangehrm_logo' value=''
        await expect(page.locator(login_page.orangehrm_logo)).to_be_visible()
        
        # Assert element_visible — target='username_label' value=''
        await expect(page.locator(login_page.username_label)).to_be_visible()
        
        # Assert element_visible — target='username_input' value=''
        await expect(page.locator(login_page.username_input)).to_be_visible()
        
        # Assert element_visible — target='password_label' value=''
        await expect(page.locator(login_page.password_label)).to_be_visible()
        
        # Assert element_visible — target='password_input' value=''
        await expect(page.locator(login_page.password_input)).to_be_visible()
        
        # Assert element_visible — target='login_button' value=''
        await expect(page.locator(login_page.login_button)).to_be_visible()
        
        await browser.close()


@pytest.mark.asyncio
async def test_tc_001_026():
    """
    TC_001_026: Verify form behavior with empty username and valid password
    
    Negative test case that verifies the form shows validation error when
    username field is empty and user remains on login page.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        login_page = LoginPage(page)
        
        # Step 1: navigate on target_url
        await login_page.navigate()
        
        # Step 2: wait on login_page_title value=visible
        await expect(page.locator(login_page.login_page_title)).to_be_visible()
        
        # Step 3: fill on password_input value=admin123
        await login_page.fill_