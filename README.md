# QA Automation Portfolio — Pytest + httpx + Playwright + Allure + GitHub Actions

A production-style test automation framework built with Python, demonstrating real-world patterns used in SDET roles at MNCs. Built progressively across 7 modules — API testing, UI automation with POM, fixture scopes, factory pattern, parallel execution, BasePage inheritance, and Allure reporting.

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
- Screenshot on failure — embedded directly in Allure report
- Allure reporting — interactive dashboard with steps, severity, feature grouping
- Automated CI pipeline with GitHub Actions — two parallel jobs
- Allure results and report uploaded as CI artifacts

## Tech stack

| Tool              | Purpose                                         |
| ----------------- | ----------------------------------------------- |
| Python 3.13       | Language                                        |
| httpx             | HTTP client for API tests                       |
| pytest            | Test runner and assertion framework             |
| pytest-playwright | Playwright integration for UI tests             |
| pytest-xdist      | Parallel test execution across multiple workers |
| allure-pytest     | Allure reporting integration                    |
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
│   ├── screenshots/                  # auto-populated on test failure (local)
│   └── tests/
│       ├── conftest.py               # fixtures + screenshot_on_failure hook
│       ├── login_test.py             # login scenarios with Allure steps
│       ├── test_inventory.py         # inventory scenarios with Allure severity
│       └── test_scope_experiments.py # fixture scope + parallel demos
│
└── .github/
    └── workflows/
        └── tests.yml                 # CI pipeline — parallel jobs, allure artifacts
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

**6. Run with Allure reporting**

```bash
pytest pom_project/tests/ -v --browser chromium -n 2 --alluredir=allure-results
allure serve allure-results
```

**7. Run by marker**

```bash
# skip slow tests, run in parallel
pytest pom_project/tests/ -v --browser chromium -n auto -m "not slow"

# slow tests only, sequential
pytest pom_project/tests/ -v --browser chromium -m "slow"
```

**8. Run against a different environment**

```bash
BASE_URL=https://staging.saucedemo.com pytest pom_project/tests/ -v --browser chromium
```

---

## Viewing Allure reports from CI

After a CI run completes:

1. Go to **Actions** → select the run → scroll to **Artifacts**
2. Download the `allure-report` artifact
3. Unzip the downloaded file
4. Run in terminal:

```bash
allure open allure-report/
```

5. Full interactive Allure dashboard opens automatically in your browser

**Important:** do not open `index.html` directly from the file system. Browsers block the JavaScript required by Allure when loaded via `file://` protocol — the report will show "Loading..." forever. Always use `allure open` or serve with `python3 -m http.server`.

The raw `allure-results` artifact is also available if you want to regenerate the report locally with historical trend data.

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

**Page chaining** — the same `page` object passes through multiple page objects, reflecting the real browser session.

---

## Module 3 — Fixture scopes

### The four scopes

| Scope      | Created          | Destroyed                | Use for                            |
| ---------- | ---------------- | ------------------------ | ---------------------------------- |
| `function` | Before each test | After each test          | Browser, page, anything with state |
| `module`   | Once per file    | After last test in file  | File-level shared resources        |
| `session`  | Once per run     | After all tests finish   | Stateless HTTP clients             |
| `class`    | Once per class   | After last test in class | OOP-heavy suites                   |

### Critical rule for parallel execution

Session scope does not cross xdist worker process boundaries. Always use function scope for browser and page in parallel runs — guarantees each test gets its own isolated browser regardless of worker count.

---

## Module 4 — Factory pattern for test data

### The problem

Hardcoded credentials scattered across test files. One environment change = every test file to update.

### The solution

```python
UserFactory.standard()               # default valid user
UserFactory.locked()                 # locked out user
UserFactory.slow()                   # performance glitch user
UserFactory.build(password="wrong")  # override only what matters
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

Markers registered in `pytest.ini` to avoid warnings across parallel workers.

---

## Module 6 — BasePage inheritance and framework design

### Core layer

```python
class BasePage:
    def wait_for_element(self, locator): ...   # consistent waits
    def navigate_to(self, url: str): ...       # navigation + load state
    def take_screenshot(self, name: str): ...  # manual screenshot
    def get_page_title(self) -> str: ...       # page title
    def get_current_url(self) -> str: ...      # current URL

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # login-specific locators only
```

### Config — environment switching without code changes

```python
class Config:
    BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
```

### Screenshot on failure — embedded in Allure

```python
@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        screenshot = page.screenshot()
        allure.attach(screenshot, name=request.node.name,
                      attachment_type=allure.attachment_type.PNG)
```

### Why this scales to multiple teams

- Core layer owns shared behaviour — teams don't reimplement waits or navigation
- Page layer is team-specific — teams only write what's unique to their pages
- Config is centralised — environment changes happen in one place
- BasePage changes propagate automatically to all page objects across all teams

---

## Module 7 — Allure reporting

### Allure vs pytest-html

| Feature          | pytest-html      | Allure                              |
| ---------------- | ---------------- | ----------------------------------- |
| Report type      | Static HTML file | Interactive dashboard               |
| Test grouping    | None             | By feature, story, severity         |
| Step breakdown   | No               | Yes — per test                      |
| Screenshot embed | Separate folder  | Inline in failing test              |
| Trend history    | No               | Yes — across runs                   |
| Severity filter  | No               | BLOCKER / CRITICAL / NORMAL / MINOR |

### Annotations

```python
@allure.feature("Login")
@allure.story("Valid login")
@allure.severity(allure.severity_level.CRITICAL)
def test_valid_login(login_page, page):
    with allure.step("Login with valid credentials"):
        login_page.login(user.username, user.password)
    with allure.step("Verify redirect to inventory"):
        assert page.url == "..."
```

### Dashboard views to explore

- **Overview** — pass/fail summary, severity breakdown
- **Behaviors** — tests grouped by `@allure.feature` and `@allure.story`
- **Suites** — tests grouped by file and class
- **Timeline** — parallel execution visualised across workers
- **Graphs** — trend history across multiple runs

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
3. Install UI dependencies including `allure-pytest` and `pytest-xdist`
4. Install Playwright Chromium with system dependencies (`--with-deps`)
5. Run UI tests in parallel with `-n auto`
6. Upload `allure-results/` as artifact (raw JSON)
7. Install Allure CLI
8. Generate static `allure-report/`
9. Upload `allure-report/` as artifact (interactive HTML)

### Viewing CI reports

Download `allure-report` artifact → unzip → run `allure open allure-report/`

Do not open `index.html` directly — use `allure open` or `python3 -m http.server`.

### Important lessons learned

- `allure serve` must not be run in CI — hangs the pipeline with no browser to open it
- Allure static report must be served via HTTP — `file://` protocol blocks JavaScript
- `pytest.ini` addopts must not contain Playwright flags — breaks non-Playwright jobs
- `playwright install chromium --with-deps` required on Ubuntu CI
- All packages must be in `requirements.txt` — CI starts clean every run
- Register custom markers in `pytest.ini` — warns across all parallel workers otherwise
- `-n auto` adapts to environment — 16 workers locally, 4 on GitHub Actions 2-core runners

---

## Testing strategy applied

- **Test pyramid** — API tests at integration layer, UI tests only for critical E2E flows
- **Shift-left** — CI runs on every PR, not just before release
- **Risk-based** — login and cart flows automated first as highest business impact
- **POM separation of concerns** — page layer owns locators and actions, test layer owns assertions
- **BasePage inheritance** — shared behaviour defined once, inherited everywhere
- **Factory pattern** — test data centralised, tests declare intent not setup
- **Parallel execution** — xdist with function-scoped browsers, markers for fast vs slow
- **Environment config** — BASE_URL driven by env vars, no hardcoded URLs in test code
- **Allure reporting** — interactive dashboard with severity filtering and embedded screenshots

---

## Author

Dharmateja Valluri — [LinkedIn](https://linkedin.com/in/) | [GitHub](https://github.com/)
