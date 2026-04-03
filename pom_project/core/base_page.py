from playwright.sync_api import Page, expect
from core.config import Config

class BasePage:

    def __init__(self, page: Page):
        self.page = page
        self.timeout = Config.DEFAULT_TIMEOUT

    # shared wait behaviour — all pages use this
    def wait_for_element(self, locator):
        locator.wait_for(timeout=self.timeout)
        return locator

    # shared navigation — all pages can go to any URL
    def navigate_to(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    # shared screenshot — call this in any page on failure
    def take_screenshot(self, name: str):
        self.page.screenshot(path=f"screenshots/{name}.png")

    # shared title check — any page can verify its own title
    def get_page_title(self) -> str:
        return self.page.title()

    # shared URL check
    def get_current_url(self) -> str:
        return self.page.url