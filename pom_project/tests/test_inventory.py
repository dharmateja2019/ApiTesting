# from pages.login_page import LoginPage
# from pages.inventory_page import InventoryPage
import pytest

from test_data.user_factory import UserFactory

def test_inventory_loads_six_products(inventory_page,page):
    
    assert inventory_page.get_product_count() == 6

def test_product_names_are_not_empty(inventory_page,page):
    
    names = inventory_page.get_product_names()
    assert len(names) == 6
    assert all(len(name) > 0 for name in names)

def test_add_to_cart_updates_badge(inventory_page,page):
    inventory_page.add_first_product_to_cart()

    cart_badge = page.locator(".shopping_cart_badge")
    assert cart_badge.text_content() == "1"

@pytest.mark.slow
def test_performance_glitch_user(inventory_page,login_page, page):
    user = UserFactory.slow()
    login_page.login(user.username, user.password)
    assert page.url == f"{inventory_page.get_current_url()}"

def test_page_title_is_correct(inventory_page):
    # get_page_title() comes from BasePage — InventoryPage didn't define it
    title = inventory_page.get_page_title()
    assert title == "Swag Labs"

def test_current_url_after_login(inventory_page):
    # get_current_url() also from BasePage
    url = inventory_page.get_current_url()
    assert "inventory" in url