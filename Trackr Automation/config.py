"""
Configuration file for Trackr automation
"""

# Application URLs
BASE_URL = "https://trakr-rc.embracepetinsurance.com/"
START_QUOTE_URL = f"{BASE_URL}/quoting/start-quote"

# Browser Configuration
BROWSER_CONFIG = {
    "headless": False,
    "slow_mo": 250,  # Milliseconds to slow down operations
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Timeout Configuration (in milliseconds)
TIMEOUT = {
    "default": 30000,
    "navigation": 60000,
    "element": 10000
}

# Screenshot Configuration
SCREENSHOT_DIR = "screenshots"
SCREENSHOT_FULL_PAGE = True

# Test Data (customize based on your needs)
TEST_DATA = {
    "sample_quote": {
        # Add your test data here
        # "firstName": "John",
        # "lastName": "Doe",
        # "email": "john.doe@example.com"
    }
}

# Logging Configuration
LOG_BROWSER_CONSOLE = True
LOG_NETWORK_REQUESTS = False
