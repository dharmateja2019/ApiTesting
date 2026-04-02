# API Test Suite — Pytest + httpx + GitHub Actions

A production-style API test framework built with Python, demonstrating real-world testing patterns used in SDET roles at MNCs.

## What this project covers

- API testing with `httpx` and `pytest`
- Parametrized test scenarios (happy path, negative cases, schema validation)
- Session-scoped client fixture via `conftest.py`
- Automated CI pipeline with GitHub Actions
- HTML test reports uploaded as pipeline artifacts

## Tech stack

| Tool           | Purpose                                 |
| -------------- | --------------------------------------- |
| Python 3.11    | Language                                |
| httpx          | HTTP client for API requests            |
| pytest         | Test runner and assertion framework     |
| pytest-html    | HTML report generation                  |
| GitHub Actions | CI pipeline — runs on every push and PR |

## Project structure

```
ApiTesting/
├── my-api-tests/
      ├── conftest.py          # shared fixtures (session-scoped API client)
      ├── test_api.py          # all test cases
      ├── requirements.txt     # dependencies
└── .github/
    └── workflows/
        └── tests.yml    # CI pipeline definition
```

## How to run locally

**1. Clone the repo**

```bash
git clone https://github.com/YOUR_USERNAME/my-api-tests.git
cd ApiTesting/my-api-tests
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run tests**

```bash
pytest test_api.py -v
```

**4. Run with HTML report**

```bash
pytest test_api.py -v --html=report.html --self-contained-html
```

Open `report.html` in your browser to view results.

## What is tested

Tests run against [JSONPlaceholder](https://jsonplaceholder.typicode.com) — a public fake REST API.

### Status code tests

- Valid post IDs return `200`
- Non-existent post IDs return `404`
- Parametrized across multiple IDs in one test function

### Schema validation tests

- Every field (`id`, `title`, `body`, `userId`) is present in the response
- Field types are correct — not just values
- Response `id` matches the requested `id`

### POST tests

- Creating a post returns `201`
- Response body reflects the submitted payload
- Tested with multiple payload variations using parametrize

## CI pipeline

The GitHub Actions workflow runs automatically on every push to `main` and every pull request.

**Pipeline steps:**

1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run all tests with verbose output
5. Upload HTML report as a downloadable artifact (runs even if tests fail)

To view a test report: go to **Actions** → select a run → scroll to **Artifacts** → download `test-report`.

## Key patterns used

**Session-scoped fixture** — one HTTP client shared across all tests, not recreated per test:

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

## Testing strategy applied

- **Test pyramid** — API tests sit in the integration layer; fast and reliable without a browser
- **Shift-left** — CI runs on every PR, not just before release
- **Risk-based** — parametrized schema tests cover the most critical contract assertions first

## Author

Dharmateja Valluri — [LinkedIn](https://linkedin.com/in/) | [GitHub](https://github.com/)
