from playwright.async_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.login_button_locator = page.locator("[name='submit']")
        self.username_input_field = page.locator("[name='username']")
        self.password_input_field = page.locator("[name='password']")
        self.usernameInput = page.locator("[name='username']")
        self.passwordInput = page.locator("[name='password']")
        self.loginButton = page.locator("[name='submit']")
        self.userNameNav = page.locator("div.orangehrm-header-container>nav>ul>li>span")
        self.errorMessage = page.locator("div.orangehrmLoginContainer>form>div>span")
        self.logo = page.locator("#orb-global-header > div > div:nth-child(1) > a")

    async def get_current_url(self) -> str:
        """Returns the current URL of the page."""
        return self.page.url

    async def get_errorMessage_text(self) -> str:
        """Returns the text of the error message."""
        return await self.errorMessage.text_content()

    async def is_error_div_visible(self) -> bool:
        """Checks if the error div is visible."""
        return await self.page.locator("div.error").is_visible()

    async def is_errorMessage_visible(self) -> bool:
        """Checks if the error message is visible."""
        return await self.errorMessage.is_visible()

    async def is_logo_visible(self) -> bool:
        """Checks if the logo is visible."""
        return await self.logo.is_visible()

    async def is_userNameNav_visible(self) -> bool:
        """Checks if the user name navigation is visible."""
        return await self.userNameNav.is_visible()

    async def is_usernameInput_visible(self) -> bool:
        """Checks if the username input field is visible."""
        return await self.username_input_field.is_visible()

    async def login(self, username: str, password: str) -> 'LoginPage':
        """Performs a login with the given username and password."""
        await self.username_input_field.fill(username)
        await self.password_input_field.fill(password)
        await self.loginButton.click()
        return self

    async def navigate(self) -> 'LoginPage':
        """Navigates to the login page."""
        await self.page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        return self