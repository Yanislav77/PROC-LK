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

TFA_EXISTING_USER_EMAIL = os.getenv("TFA_EXISTING_USER_EMAIL", "")
TFA_EXISTING_USER_PASSWORD = os.getenv("TFA_EXISTING_USER_PASSWORD", "")
TFA_EXISTING_USER_SECRET = os.getenv("TFA_EXISTING_USER_SECRET", "")
TFA_EXISTING_USER_ID = int(os.getenv("TFA_EXISTING_USER_ID", "0"))
TFA_NO_TFA_USER_EMAIL = os.getenv("TFA_NO_TFA_USER_EMAIL", "")
TFA_NO_TFA_USER_PASSWORD = os.getenv("TFA_NO_TFA_USER_PASSWORD", "")

ADMIN_URL = os.getenv("ADMIN_URL", "https://preprodcabinet.payment.center/admin")
ADMIN_USER = os.getenv("ADMIN_USER", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
