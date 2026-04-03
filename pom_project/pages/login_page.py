from playwright.sync_api import Page
from core.base_page import BasePage
from core.config import Config

class LoginPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)  # BasePage gets initialised first

        self.username_input = page.locator("#user-name")
        self.password_input = page.locator("#password")
        self.login_button   = page.locator("#login-button")
        self.error_message  = page.locator("[data-test='error']")

    def navigate(self):
        self.navigate_to(Config.BASE_URL)  # using BasePage method

    def login(self, username: str, password: str):
        self.wait_for_element(self.username_input).fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_message(self) -> str:
        return self.error_message.text_content() # type: ignore