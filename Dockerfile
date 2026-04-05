FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["pytest", "ui_tests/tests/", "-v", "--browser", "chromium", "-n", "auto", "--alluredir=allure-results"]