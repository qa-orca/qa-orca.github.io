"""
Test script to verify Chrome profile is loading correctly
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
from config import START_QUOTE_URL

def test_profile():
    """Test if Chrome profile loads with saved authentication"""

    chrome_profile_path = str(Path.home() / "Library/Application Support/Google/Chrome/Profile 8")

    print("=" * 60)
    print("Testing Chrome Profile Load")
    print("=" * 60)
    print(f"Profile path: {chrome_profile_path}")
    print()
    print("If the profile loads correctly, you should:")
    print("  1. See Chromium browser (this is normal)")
    print("  2. Be automatically logged into Microsoft")
    print("  3. NOT see the login screen")
    print("=" * 60)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_path,
            headless=False,
            slow_mo=1000,
            args=['--no-first-run', '--no-default-browser-check']
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("\nNavigating to Azure site...")
        page.goto(START_QUOTE_URL)

        print("\nWaiting 5 seconds to see if login is required...")
        time.sleep(5)

        # Check if we're on login page
        current_url = page.url
        print(f"\nCurrent URL: {current_url}")

        if "login.microsoftonline.com" in current_url:
            print("\n❌ PROBLEM: Still on Microsoft login page")
            print("   Profile authentication is NOT working")
        else:
            print("\n✅ SUCCESS: Bypassed login!")
            print("   Profile authentication is working")

        print("\nBrowser will stay open for 30 seconds for inspection...")
        time.sleep(30)

        context.close()

if __name__ == "__main__":
    test_profile()
