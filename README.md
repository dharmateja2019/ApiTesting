# QA Automation Portfolio

![CI](https://github.com/dharmateja2019/ApiTesting/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Playwright](https://img.shields.io/badge/playwright-1.58.0-green)
![K6](https://img.shields.io/badge/k6-performance-orange)
![Docker](https://img.shields.io/badge/docker-containerised-blue)
![Allure](https://img.shields.io/badge/allure-reporting-yellow)

A production-style test automation framework built with Python and JavaScript. Covers API testing, UI automation, performance testing, Docker containerisation, and CI/CD — demonstrating real-world patterns used in SDET roles at MNCs.

---

## Architecture overview

```
┌─────────────────────────────────────────────┐
│               Core layer                    │
│   base_page.py  │  config.py  │ conftest.py │
└────────────────────┬────────────────────────┘
                     │ inherits / uses
┌────────────────────▼────────────────────────┐
│               Page layer                    │
│      login_page.py  │  inventory_page.py    │
└────────────────────┬────────────────────────┘
                     │ uses
┌────────────────────▼────────────────────────┐
│            Test data layer                  │
│    user_factory.py  │  product_factory.py   │
└────────────────────┬────────────────────────┘
                     │ consumed by
┌────────────────────▼────────────────────────┐
│               Test layer                    │
│  login_test.py │ test_inventory.py │ k6 js  │
└─────────────────────────────────────────────┘
```

For full architecture diagrams (component view, CI flow, class inheritance, Docker flow, K6 flow) see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Tech stack

| Tool              | Purpose                      |
| ----------------- | ---------------------------- |
| Python 3.12       | Language (pinned via Docker) |
| httpx             | HTTP client for API tests    |
| pytest            | Test runner                  |
| pytest-playwright | UI test integration          |
| pytest-xdist      | Parallel execution           |
| allure-pytest     | Interactive reporting        |
| Docker            | Containerised environment    |
| K6                | Performance and load testing |
| GitHub Actions    | CI/CD pipeline               |

---

## Project structure

```
ApiTesting/
├── Dockerfile                        # Playwright base image v1.58.0
├── .dockerignore
├── requirements.txt
├── pytest.ini                        # pythonpath + markers
│
├── my-api-tests/
│   ├── conftest.py
│   ├── requirements.txt
│   └── test_api.py
│
├── performance/
│   └── api_load_test.js              # K6 — mirrors functional API tests
│
├── pom_project/
│   ├── core/
│   │   ├── base_page.py
│   │   └── config.py
│   ├── pages/
│   │   ├── login_page.py
│   │   └── inventory_page.py
│   ├── test_data/
│   │   ├── user_factory.py
│   │   └── product_factory.py
│   ├── screenshots/
│   └── tests/
│       ├── conftest.py
│       ├── login_test.py
│       ├── test_inventory.py
│       └── test_scope_experiments.py
│
└── .github/
    └── workflows/
        └── tests.yml
```

---

## Quick start

```bash
git clone https://github.com/dharmateja2019/ApiTesting.git
cd ApiTesting
pip install -r requirements.txt
pip install -r my-api-tests/requirements.txt
playwright install chromium
```

---

## How to run

### API tests

```bash
pytest my-api-tests/test_api.py -v
```

### UI tests

```bash
# sequential
pytest pom_project/tests/ -v --browser chromium

# parallel
pytest pom_project/tests/ -v --browser chromium -n auto

# with Allure
pytest pom_project/tests/ -v --browser chromium -n 2 --alluredir=allure-results
allure serve allure-results
```

### Performance tests

```bash
k6 run performance/api_load_test.js
```

### Docker

```bash
docker build -t qa-automation .
docker run qa-automation
docker run -v $(pwd)/allure-results:/app/allure-results qa-automation
```

### Different environment

```bash
BASE_URL=https://staging.example.com pytest pom_project/tests/ -v --browser chromium
docker run -e BASE_URL=https://staging.example.com qa-automation
```

### By marker

```bash
pytest -n auto -m "not slow"   # fast tests in parallel
pytest -m "slow"               # slow tests sequentially
```

---

## Viewing Allure reports from CI

1. **Actions** → select run → **Artifacts** → download `allure-report`
2. Unzip
3. `allure open allure-report/`

Do not open `index.html` directly — `file://` protocol blocks Allure's JavaScript. Always use `allure open` or `python3 -m http.server`.

---

## CI pipeline

Three parallel jobs on every push and PR:

```
git push
    │
    ├── api-tests ──────► api-report.html artifact
    │   httpx + pytest
    │
    ├── ui-tests ───────► allure-report/ artifact
    │   Playwright + xdist + Allure
    │
    └── performance-tests ► pass / fail
        K6 + thresholds
```

---

## What is tested

### API (JSONPlaceholder)

- Status codes — valid and invalid IDs parametrized
- Schema validation — field presence and types, not just status
- POST — response body matches payload, multiple variations

### UI (SauceDemo)

- Login — valid, invalid password, empty username, locked user
- Inventory — product count, names, cart badge, page title, URL
- Performance glitch user (marked `slow`)

### Performance (JSONPlaceholder)

- GET single post — `p(95) < 400ms`
- POST create — `p(95) < 600ms`
- Failure rate — `< 1%`
- 10 VUs, ramp-up stages, 40s total duration

---

## Performance results

| Endpoint     | p(95) | Threshold | Status |
| ------------ | ----- | --------- | ------ |
| GET /posts/1 | 41ms  | < 400ms   | ✓      |
| POST /posts  | 45ms  | < 600ms   | ✓      |
| Failure rate | 0.00% | < 1%      | ✓      |

---

## Parallel execution timing

| Mode       | Workers | Time | Environment    |
| ---------- | ------- | ---- | -------------- |
| Sequential | 1       | ~30s | Local Mac      |
| `-n 2`     | 2       | ~15s | Local Mac      |
| `-n auto`  | 16      | ~13s | Local Mac      |
| `-n auto`  | 4       | ~12s | GitHub Actions |
| `-n auto`  | 4       | ~19s | Docker         |

---

## Key lessons learned

- Pin Docker image versions — `latest` causes silent Playwright/browser mismatches
- `pytest.ini` addopts must not contain Playwright flags — breaks non-Playwright jobs
- `playwright install chromium --with-deps` required on Ubuntu CI
- `allure serve` must not run in CI — hangs with no browser
- Session scope does not cross xdist worker boundaries — use function scope for browser
- All packages in `requirements.txt` — CI starts clean every run
- `-n auto` adapts to environment — 16 workers locally, 4 in CI and Docker

---

## Testing strategy

| Principle          | Applied as                                                   |
| ------------------ | ------------------------------------------------------------ |
| Test pyramid       | API at integration layer, UI only for critical E2E flows     |
| Shift-left         | CI runs on every PR, not just before release                 |
| Risk-based         | Login and cart flows first — highest business impact         |
| POM                | Page layer owns locators, test layer owns assertions         |
| BasePage           | Shared behaviour inherited everywhere automatically          |
| Factory pattern    | Test data centralised, tests declare intent not setup        |
| Parallel execution | xdist with function-scoped browsers                          |
| Environment config | BASE_URL via env vars — same code for all environments       |
| Allure             | Interactive reporting with severity and embedded screenshots |
| Docker             | Pinned image — identical environment on every machine        |
| K6 thresholds      | Performance regressions caught automatically in CI           |

---

## Author

Dharmateja Valluri — [LinkedIn](https://linkedin.com/in/) | [GitHub](https://github.com/dharmateja2019)
