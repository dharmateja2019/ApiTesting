import allure

@allure.feature("Inventory")
@allure.story("Page load")
@allure.severity(allure.severity_level.CRITICAL)
def test_inventory_loads_six_products(inventory_page):
    with allure.step("Verify exactly 6 products are displayed"):
        assert inventory_page.get_product_count() == 6

@allure.feature("Inventory")
@allure.story("Page load")
@allure.severity(allure.severity_level.NORMAL)
def test_product_names_are_not_empty(inventory_page):
    with allure.step("Get all product names"):
        names = inventory_page.get_product_names()
    with allure.step("Verify all names are non-empty"):
        assert len(names) == 6
        assert all(len(name) > 0 for name in names)

@allure.feature("Inventory")
@allure.story("Cart")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_to_cart_updates_badge(inventory_page, page):
    with allure.step("Add first product to cart"):
        inventory_page.add_first_product_to_cart()
    with allure.step("Verify cart badge shows 1"):
        cart_badge = page.locator(".shopping_cart_badge")
        assert cart_badge.text_content() == "1"