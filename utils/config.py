import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://preprodcabinet-alt.payment.center/new")
API_V4_URL = os.getenv("API_BASE_URL", "https://preprodcabinet-alt.payment.center/api/v4")
API_V1_URL = API_V4_URL.replace("/v4", "/v1")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
VIDEO = os.getenv("VIDEO", "false").lower() == "true"
