# QA Automation Portfolio — Pytest + httpx + Playwright + GitHub Actions

A production-style test automation framework built with Python, demonstrating real-world patterns used in SDET roles at MNCs. Built progressively across 5 modules — API testing, UI automation with POM, fixture scopes, factory pattern, parallel execution, and multi-team framework design with BasePage inheritance.

## What this project covers

- API testing with `httpx` and `pytest`
- Parametrized test scenarios (happy path, negative cases, schema validation)
- UI automation with Playwright and Page Object Model (POM)
- BasePage inheritance — shared behaviour across all page objects
- Centralised config with environment variable support
- Multi-page object chaining (login → inventory flow)
- Fixture scopes — function scope for browser and page in parallel runs
- Factory pattern for centralised test data management
- Parallel test execution with `pytest-xdist`
- Custom markers for selective test execution
- Screenshot on failure — automatic evidence capture
- Automated CI pipeline with GitHub Actions — two parallel jobs
- HTML test reports and failure screenshots uploaded as artifacts

## Tech stack

| Tool              | Purpose                                         |
| ----------------- | ----------------------------------------------- |
| Python 3.13       | Language                                        |
| httpx             | HTTP client for API tests                       |
| pytest            | Test runner and assertion framework             |
| pytest-playwright | Playwright integration for UI tests             |
| pytest-xdist      | Parallel test execution across multiple workers |
| pytest-html       | HTML report generation                          |
| GitHub Actions    | CI pipeline — runs on every push and PR         |

## Project structure

```
ApiTesting/
├── requirements.txt                  # all UI test dependencies
├── pytest.ini                        # pytest config — registered markers
│
├── my-api-tests/
│   ├── conftest.py                   # session-scoped API client fixture
│   ├── requirements.txt              # API test dependencies
│   └── test_api.py                   # API test cases
│
├── pom_project/
│   ├── core/
│   │   ├── base_page.py              # shared behaviour — wait, navigate, screenshot, title
│   │   └── config.py                 # centralised config — BASE_URL, timeout, headless
│   ├── pages/
│   │   ├── login_page.py             # inherits BasePage
│   │   └── inventory_page.py         # inherits BasePage
│   ├── test_data/
│   │   ├── user_factory.py           # User dataclass + UserFactory
│   │   └── product_factory.py        # Product dataclass + ProductFactory
│   ├── screenshots/                  # auto-populated on test failure
│   └── tests/
│       ├── conftest.py               # fixtures + screenshot_on_failure hook
│       ├── login_test.py             # login scenarios
│       ├── test_inventory.py         # inventory scenarios
│       └── test_scope_experiments.py # fixture scope + parallel demos
│
└── .github/
    └── workflows/
        └── tests.yml                 # CI pipeline — parallel jobs, artifacts
```

## How to run locally

**1. Clone the repo**

```bash
git clone https://github.com/dharmateja2019/ApiTesting.git
cd ApiTesting
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
pip install -r my-api-tests/requirements.txt
playwright install chromium
```

**3. Run API tests**

```bash
pytest my-api-tests/test_api.py -v
```

**4. Run UI tests — sequential**

```bash
pytest pom_project/tests/ -v --browser chromium
```

**5. Run UI tests — parallel**

```bash
pytest pom_project/tests/ -v --browser chromium -n 2
pytest pom_project/tests/ -v --browser chromium -n auto
```

**6. Run by marker**

```bash
pytest pom_project/tests/ -v --browser chromium -n auto -m "not slow"
pytest pom_project/tests/ -v --browser chromium -m "slow"
```

**7. Run against a different environment**

```bash
BASE_URL=https://staging.saucedemo.com pytest pom_project/tests/ -v --browser chromium
```

**8. Run with HTML report**

```bash
pytest pom_project/tests/ -v --browser chromium -n auto --html=ui-report.html --self-contained-html
```

---

## Module 1 — API testing

Tests run against [JSONPlaceholder](https://jsonplaceholder.typicode.com) — a public fake REST API.

### What is tested

**Status code tests**

- Valid post IDs return `200`
- Non-existent post IDs return `404`
- Parametrized across multiple IDs in one test function

**Schema validation tests**

- Every field (`id`, `title`, `body`, `userId`) is present
- Field types are correct — not just values
- Response `id` matches the requested `id`

**POST tests**

- Creating a post returns `201`
- Response body reflects the submitted payload
- Multiple payload variations tested using parametrize

### Key patterns

**Session-scoped fixture** — one HTTP client shared across all tests:

```python
@pytest.fixture(scope="session")
def api_client():
    with httpx.Client(base_url="...") as client:
        yield client
```

**Parametrize** — one test function covers multiple scenarios:

```python
@pytest.mark.parametrize("post_id, expected_status", [
    (1, 200),
    (99999, 404),
])
def test_get_post_status(post_id, expected_status):
    ...
```

**Schema validation** — checking response shape, not just status code:

```python
assert isinstance(data["id"], int)
assert isinstance(data["title"], str)
assert len(data["title"]) > 0
```

---

## Module 2 — UI automation with Page Object Model

Tests run against [SauceDemo](https://www.saucedemo.com) — a demo e-commerce site built for automation practice.

### What is tested

**Login scenarios**

- Valid credentials redirect to inventory page
- Invalid password shows correct error message
- Empty username shows validation error
- Locked-out user cannot log in

**Inventory scenarios**

- Page loads exactly 6 products
- All product names are non-empty strings
- Adding first product updates cart badge to 1
- Page title is correct (via BasePage)
- Current URL contains "inventory" (via BasePage)
- Performance glitch user eventually lands on inventory (marked `slow`)

### POM design decisions

**No assertions in page classes** — page objects describe what a page _can do_, not what _should be true_. Assertions live exclusively in test files.

**Locators defined once** — all selectors live in the page class constructor. UI changes require updating one place, not every test.

**Fixture handles navigation** — tests don't call `navigate()` or `login()` manually:

```python
@pytest.fixture(scope="function")
def inventory_page(page):
    user = UserFactory.standard()
    lp = LoginPage(page)
    lp.navigate()
    lp.login(user.username, user.password)
    return InventoryPage(page)
```

---

## Module 3 — Fixture scopes

### The four scopes

| Scope      | Created          | Destroyed                | Use for                           |
| ---------- | ---------------- | ------------------------ | --------------------------------- |
| `function` | Before each test | After each test          | Page objects, anything with state |
| `module`   | Once per file    | After last test in file  | File-level shared resources       |
| `session`  | Once per run     | After all tests finish   | Stateless HTTP clients            |
| `class`    | Once per class   | After last test in class | OOP-heavy suites                  |

### Critical rule for parallel execution

Session scope does not cross xdist worker process boundaries. Always use function scope for stateful resources like browser and page in parallel runs.

---

## Module 4 — Factory pattern for test data

### The problem

Hardcoded credentials scattered across test files. One environment change = every test file to update.

### The solution

```python
user = UserFactory.standard()              # default valid user
user = UserFactory.locked()                # locked out user
user = UserFactory.build(password="wrong") # override only what matters
```

Credentials defined in one place. Tests declare intent, not setup.

---

## Module 5 — Parallel execution with pytest-xdist

### Observed timing (15 tests)

| Mode            | Workers | Time |
| --------------- | ------- | ---- |
| Sequential      | 1       | ~30s |
| `-n 2`          | 2       | ~15s |
| `-n auto` local | 16      | ~13s |
| `-n auto` CI    | 4       | ~12s |

### Custom markers

```python
@pytest.mark.slow
def test_performance_glitch_user(inventory_page, page):
    ...
```

```bash
pytest -n auto -m "not slow"   # fast tests in parallel
pytest -m "slow"               # slow tests sequentially
```

---

## Module 6 — BasePage inheritance and framework design

### Core layer structure

```
core/
├── base_page.py    # shared behaviour every page inherits
└── config.py       # centralised environment config
```

### BasePage — shared behaviour

Every page object inherits from `BasePage` and gets these for free:

```python
class BasePage:
    def wait_for_element(self, locator): ...   # consistent waits
    def navigate_to(self, url: str): ...       # navigation + load state
    def take_screenshot(self, name: str): ...  # manual screenshot
    def get_page_title(self) -> str: ...       # page title
    def get_current_url(self) -> str: ...      # current URL
```

### Page objects inherit cleanly

```python
class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)   # BasePage initialised first
        # only login-specific locators here
```

### Config — environment switching without code changes

```python
class Config:
    BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
```

Switch environments by changing one env variable:

```bash
BASE_URL=https://staging.example.com pytest pom_project/tests/
```

### Screenshot on failure

Every failing test automatically captures a screenshot named after the test:

```python
@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        page.screenshot(path=f"pom_project/screenshots/{request.node.name}.png")
```

No manual call needed in tests. Screenshots uploaded as CI artifacts for remote debugging.

### Why this design scales to multiple teams

- Core layer owns shared behaviour — teams don't reimplement waits or navigation
- Page layer is team-specific — teams only write what's unique to their pages
- Config is centralised — environment changes happen in one place
- BasePage changes automatically apply to all page objects across all teams
- Core can be versioned separately — teams pull updates without rewriting their pages

---

## CI pipeline

Two jobs run in parallel on every push to `main` and every pull request.

### api-tests job

1. Checkout code
2. Set up Python 3.13
3. Install API dependencies
4. Run API tests
5. Upload `api-report.html` as artifact

### ui-tests job

1. Checkout code
2. Set up Python 3.13
3. Install UI dependencies including `pytest-xdist`
4. Install Playwright Chromium with system dependencies (`--with-deps`)
5. Run UI tests in parallel with `-n auto`
6. Upload `ui-report.html` as artifact
7. Upload `failure-screenshots/` as artifact

### Important lessons learned

- `pytest.ini` addopts must not contain Playwright flags — breaks non-Playwright jobs
- `playwright install chromium --with-deps` required on Ubuntu — system deps not pre-installed
- All packages must be in `requirements.txt` — CI starts clean every run
- Register custom markers in `pytest.ini` — unregistered marks warn across all parallel workers
- `-n auto` adapts to environment — 16 workers locally, 4 workers on 2-core CI runners

---

## Testing strategy applied

- **Test pyramid** — API tests at integration layer, UI tests only for critical E2E flows
- **Shift-left** — CI runs on every PR, not just before release
- **Risk-based** — login and cart flows automated first as highest business impact
- **POM separation of concerns** — page layer owns locators and actions, test layer owns assertions
- **BasePage inheritance** — shared behaviour defined once, inherited everywhere
- **Factory pattern** — test data centralised, tests declare intent not setup
- **Parallel execution** — xdist with function-scoped browsers, markers to separate fast and slow
- **Environment config** — BASE_URL driven by env vars, no hardcoded URLs in test code

---

## Author

Dharmateja Valluri — [LinkedIn](https://linkedin.com/in/) | [GitHub](https://github.com/)
