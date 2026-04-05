import allure
from ..test_data.user_factory import UserFactory

@allure.feature("Login")
@allure.story("Valid login")
def test_valid_login(login_page, page):
    with allure.step("Login with valid credentials"):
        user = UserFactory.standard()
        login_page.login(user.username, user.password)
    with allure.step("Verify redirect to inventory page"):
        assert page.url == "https://www.saucedemo.com/inventory.html"

@allure.feature("Login")
@allure.story("Invalid login")
def test_invalid_password(login_page):
    with allure.step("Login with wrong password"):
        user = UserFactory.build(password="wrong_password")
        login_page.login(user.username, user.password)
    with allure.step("Verify error message appears"):
        assert "do not match" in login_page.get_error_message()

@allure.feature("Login")
@allure.story("Invalid login")
def test_empty_username(login_page):
    with allure.step("Login with empty username"):
        user = UserFactory.build(username="")
        login_page.login(user.username, user.password)
    with allure.step("Verify username required error"):
        assert "Username is required" in login_page.get_error_message()

@allure.feature("Login")
@allure.story("Locked user")
def test_locked_user(login_page):
    with allure.step("Login with locked out user"):
        user = UserFactory.locked()
        login_page.login(user.username, user.password)
    with allure.step("Verify locked out error"):
        assert "locked out" in login_page.get_error_message()