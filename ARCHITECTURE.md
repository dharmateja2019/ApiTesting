# Architecture Decisions — Why This Framework Was Built This Way

This document explains the key architectural decisions in this test automation framework. Not just _what_ was used, but _why_ each decision was made and what problem it solves.

## Framework at a Glance

- 12 UI tests across 2 page objects, running in parallel in 19s inside Docker
- API tests covering status codes, schema validation, and POST scenarios
- Single command switches between dev, staging, and prod environments
- Every failing test automatically captures a screenshot embedded in Allure report
- Interactive Allure dashboard with feature grouping, severity filtering, and step breakdown
- Fully containerised — identical environment on Mac, Windows, Ubuntu, and CI

---

## 1. Why Playwright Over Selenium?

Playwright eliminates browser driver management entirely. Selenium requires downloading and versioning ChromeDriver separately — when Chrome updates you get version mismatches and test failures from infrastructure, not code. Playwright bundles drivers, so all developers run the same version.

Playwright also has built-in auto-waiting. Locators wait automatically for elements to be ready before clicking. Selenium requires manual waits and sleep calls scattered across test code, making tests slower and more fragile. Tests fail less often, and when they do it's usually a real problem, not a timing issue.

---

## 2. Why Page Object Model?

Without POM, locators scatter everywhere. If you have 15 login tests and the username field selector changes, you update 15 test files and risk missing one. One miss = one broken test that nobody knows about until CI later. With POM, LoginPage owns every login-related locator and action. One selector change = one file update, and all 15 tests automatically use the new selector.

POM also makes tests readable. Instead of:

```python
page.locator("#user-name").fill("standard_user")
page.locator("#password").fill("secret_sauce")
page.locator("#login-button").click()
```

Tests say:

```python
login_page.login("standard_user", "secret_sauce")
```

The test reads like a business scenario, not HTML plumbing. New team members understand the test intent immediately.

---

## 3. Why BasePage?

Without BasePage, each page class duplicates the same code. Every page needs to wait for elements, navigate to URLs, capture screenshots, and check page state. With 5 page objects on a team, you have 5 different wait implementations. Another team builds 7 more pages with 7 different implementations. Waiting logic becomes inconsistent — some pages wait 5 seconds, some 30, some don't wait at all.

BasePage defines waiting, navigation, screenshots, and page info once. Every page inherits it automatically. When you discover a hidden race condition and need to add retry logic to waiting, you fix it in BasePage and it applies instantly to all 12 pages in the framework. New pages written next month get the fixed logic without anyone remembering to add it manually.

At scale with multiple teams, BasePage becomes the shared platform layer. Teams focus on page-specific logic. The core team maintains BasePage. A fix in BasePage propagates to every team's tests.

---

## 4. Why Factory Pattern for Test Data?

Without factories, credentials scatter across tests. Every login test hardcodes:

```python
def test_login_valid():
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
```

Fast forward six months. Your test environment password changes to "new_secret_2026". You search for "secret_sauce" and find it in 23 test files. You update 22 of them. The 23rd? Missed it. Next day that test fails in CI and the team thinks it's a bug, not a credential change.

With factories:

```python
user = UserFactory.standard()
login_page.login(user.username, user.password)
```

Credentials live in one place. The password is "secret_sauce" exactly once, in `user_factory.py`. When it changes, one update fixes all 23 tests. Tests also declare intent — `UserFactory.locked()` tells you immediately this is the locked-user scenario, no reading through magic strings.

---

## 5. Why Function Scope for Browser in Parallel Runs?

Session scope means one browser object created once and reused for every test. This works fine running tests sequentially on one machine. It breaks with parallel execution.

When you run `pytest -n 2`, pytest spawns two separate worker processes. Each worker is an independent Python instance. Session scope doesn't cross process boundaries reliably with xdist — each worker creates its own session, which creates unexpected complications.

Function scope guarantees each test gets its own isolated browser regardless of worker count. Two tests run in parallel, each with their own browser. No sharing issues. No crashes. Parallel execution just works.

---

## 6. Why Parallel Execution?

Running 12 UI tests sequentially took 30 seconds. Running them with `-n 2` dropped to 15 seconds. Running with `-n auto` on a 16-core machine dropped to 13 seconds. In a real suite with 500 tests the difference is 35 minutes versus under 8 minutes.

In CI, feedback speed matters. A developer pushes code and waits for test results. 35 minutes is enough time to start another task, forget about the tests, then context-switch back. 8 minutes is long enough to grab coffee and check Slack.

---

## 7. Why Two Separate CI Jobs?

Initially this looked like it could be one job running all tests. But separate jobs are better.

Imagine a scenario: the UI test for the shopping cart has a flake. It fails once every 10 runs. The CI run fails because of the UI test. Looking at the results, you see:

- API tests: ✅ all passed
- UI tests: ❌ cart test failed

With a single combined job, the entire job failed. Future commits might show "build is broken" even if nothing else failed. With separate jobs, both jobs report independently. Developers see "API tests passing, UI tests sometimes flaky" — much clearer picture of what needs attention.

Also, dependencies are different. API tests need httpx. UI tests need Playwright. Combining them means both deps always install even if you only care about API tests that week. Separate jobs install only what they need.

---

## 8. Why Environment Variables for BASE_URL?

Hardcoding URLs in test code requires code changes to switch environments. Want to test against staging? Change all `https://www.saucedemo.com` to `https://staging.saucedemo.com` across test files, commit, push. Mistakes happen.

With `BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")`, the same test file works everywhere:

- Local development: `BASE_URL` env var isn't set, defaults to public demo site
- CI testing staging: GitHub Actions sets `BASE_URL=https://staging.example.com`
- Docker run: `docker run -e BASE_URL=https://staging.example.com qa-automation`
- Production smoke tests: another job sets `BASE_URL=https://prod.example.com`

Same test code. No commits. Just environment variables. Different teams can run the same tests against their own environments without touching code.

---

## 9. Why Allure Over pytest-html?

pytest-html produces a static HTML file — useful but flat. One page, no filtering, no trend history. Allure produces an interactive dashboard with test grouping by feature and story, severity filtering, step-by-step breakdown inside each test, and screenshots embedded directly in failing tests. In a team standup you can open Allure and filter to CRITICAL failures in 2 clicks. With pytest-html you're scrolling through a flat list.

Allure also separates raw results from the report. CI generates `allure-results/` — raw JSON files. The report is generated separately, meaning you can regenerate the report with historical data across multiple runs, showing trend graphs of pass rate over time. pytest-html shows only the current run.

In CI, `allure serve` is intentionally not run — it starts a local web server and would hang the pipeline with no browser to open it. Instead the Allure CLI generates a static HTML report which is uploaded as an artifact. Team members download and run `allure open allure-report/` locally. Opening `index.html` directly via `file://` protocol blocks the JavaScript Allure needs — always serve via HTTP.

---

## 10. Why Docker?

Without Docker, "works on my machine" is a real problem. The test suite runs on Mac with Python 3.13, on GitHub Actions with Ubuntu and Python 3.13, and on a colleague's Windows machine with whatever Python version they have installed. Browser driver versions, system library versions, and Python package versions all differ. Tests pass locally and fail in CI for infrastructure reasons, not test logic reasons.

Docker packages the entire test environment into a container — Python version, Playwright browser, all dependencies — using Microsoft's official Playwright Python base image. Any machine with Docker installed runs the exact same environment. The same container runs locally and in CI.

### Why pin the image version?

The Dockerfile uses `mcr.microsoft.com/playwright/python:v1.58.0-noble` not `latest`. This was learned the hard way — using `v1.51.0` while pip installed `playwright 1.58.0` caused every test to fail with a cryptic "executable doesn't exist" error. The browser bundled in the image didn't match the version pip installed. Pinning both together and upgrading deliberately prevents this mismatch.

### Why copy requirements.txt before the project code?

Docker builds in layers. Each instruction is a cached layer. If you copy everything first and then run pip install, any source file change invalidates the pip install layer — even if requirements didn't change. Copying `requirements.txt` first means pip install is only re-run when dependencies actually change. Source code changes only invalidate the `COPY . .` layer, keeping rebuilds fast.

---

## Summary

Each decision connects to a real problem encountered either during development or anticipated from scaling experience:

- **Playwright** removes driver maintenance as a source of flakes
- **POM** prevents locator duplication across test files
- **BasePage** standardizes behaviour across all pages automatically
- **Factories** centralize test data so environment changes don't require updating every test file
- **Function scope** makes parallel execution reliable
- **Parallel execution** cuts test time in half or more
- **Separate CI jobs** isolate failures and dependencies
- **Environment variables** make the same tests work in dev, staging, and production
- **Allure** gives teams an interactive dashboard with severity filtering and embedded failure evidence
- **Docker** guarantees identical environments — no "works on my machine" failures

Together they form a framework that scales: new pages inherit behaviour automatically, new environments switch without code changes, new teams use shared infrastructure without reimplementing it, and failures are visible and debuggable without access to the CI machine.
