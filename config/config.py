import os

class Config:
    BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"