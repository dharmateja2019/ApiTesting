import pytest

@pytest.fixture(scope="function")
def function_fixture():
    print("\n  [function fixture] created")
    yield "function"
    print("\n  [function fixture] destroyed")

@pytest.fixture(scope="module")
def module_fixture():
    print("\n  [module fixture] created")
    yield "module"
    print("\n  [module fixture] destroyed")

@pytest.fixture(scope="session")
def session_fixture():
    print("\n  [session fixture] created")
    yield "session"
    print("\n  [session fixture] destroyed")

def test_one(function_fixture, module_fixture, session_fixture):
    print(f"\n  running test_one")

def test_two(function_fixture, module_fixture, session_fixture):
    print(f"\n  running test_two")

def test_three(function_fixture, module_fixture, session_fixture):
    print(f"\n  running test_three")

def test_adds_item_to_cart(inventory_page):
    inventory_page.add_first_product_to_cart()

def test_cart_is_empty_at_start(inventory_page, page):
    # this should pass — fresh page means empty cart
    # with session scope on page, the cart from previous test bleeds in
    cart_badge = page.locator(".shopping_cart_badge")
    assert cart_badge.count() == 0  # expects no badge = empty cart