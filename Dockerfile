FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["pytest", "pom_project/tests/", "-v", "--browser", "chromium", "-n", "auto", "--alluredir=allure-results"]