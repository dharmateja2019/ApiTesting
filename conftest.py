import pytest
from playwright.sync_api import sync_playwright
from ui_tests.pages.login_page import LoginPage
from ui_tests.pages.inventory_page import InventoryPage
from ui_tests.test_data.user_factory import UserFactory

import pytest
import httpx

@pytest.fixture(scope="session")
def api_client():
    with httpx.Client(base_url="https://jsonplaceholder.typicode.com") as client:
        yield client

# session scope — one browser for the entire run
@pytest.fixture(scope="function")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

# function scope — fresh page per test, no shared state
@pytest.fixture(scope="function")
def page(browser_instance):
    page = browser_instance.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def login_page(page):
    lp = LoginPage(page)
    lp.navigate()
    return lp

@pytest.fixture(scope="function")
def inventory_page(page):
    user = UserFactory.standard()
    lp = LoginPage(page)
    lp.navigate()
    lp.login(user.username, user.password)
    return InventoryPage(page)

import allure

@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"{request.node.name}",
            attachment_type=allure.attachment_type.PNG
        )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)