from playwright.async_api import Page, expect


class Login:
    """Page Object Model for Orange HRM Login page."""

    def __init__(self, page: Page):
        """Initialize Login page with Playwright page instance.
        
        Args:
            page: Playwright Page object
        """
        self.page = page
        self.url = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

    @property
    def username_input(self):
        """Locator for username input field."""
        return self.page.locator("[name='username']")

    @property
    def password_input(self):
        """Locator for password input field."""
        return self.page.locator("[name='password']")

    @property
    def login_button(self):
        """Locator for login submit button."""
        return self.page.locator("button[type='submit']")

    @property
    def username_navbar(self):
        """Locator for username in top navigation bar."""
        return self.page.locator("div[class='oxd-userdropdown']")

    @property
    def error_message(self):
        """Locator for error message container."""
        return self.page.locator("p[class='oxd-text oxd-text--p oxd-alert-content-text']")

    async def navigate(self) -> "Login":
        """Navigate to the login page.
        
        Returns:
            Login: self for method chaining
        """
        await self.page.goto(self.url)
        return self

    async def get_current_url(self) -> str:
        """Get the current URL of the page.
        
        Returns:
            str: Current page URL
        """
        return self.page.url

    async def get_error_message_text(self) -> str:
        """Get the error message text from the page.
        
        Returns:
            str: Error message text or empty string if not present
        """
        try:
            await expect(self.error_message).to_be_visible(timeout=5000)
            return await self.error_message.text_content()
        except Exception:
            return ""

    async def is_username_input_visible(self) -> bool:
        """Check if username input field is visible.
        
        Returns:
            bool: True if visible, False otherwise
        """
        try:
            await expect(self.username_input).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False

    async def is_username_navbar_visible(self) -> bool:
        """Check if username navbar element is visible.
        
        Returns:
            bool: True if visible, False otherwise
        """
        try:
            await expect(self.username_navbar).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False

    async def login(self, username: str, password: str) -> "Login":
        """Perform login with provided credentials.
        
        Args:
            username: Username to enter in username field
            password: Password to enter in password field
            
        Returns:
            Login: self for method chaining
        """
        await self.username_input.fill(username)
        await self.password_input.fill(password)
        await self.login_button.click()
        await self.page.wait_for_load_state("networkidle")
        return self