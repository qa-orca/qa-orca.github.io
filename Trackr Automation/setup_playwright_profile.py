"""
One-time setup: Create a Playwright profile with saved Microsoft login
After running this once and logging in manually, future runs will skip login
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
from config import START_QUOTE_URL

def setup_profile():
    """Setup a persistent Playwright profile with Microsoft login"""

    # Create a dedicated profile directory for Playwright
    playwright_profile = Path.home() / "playwright-profiles" / "trackr-qa"
    playwright_profile.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Playwright Profile Setup - ONE-TIME MANUAL LOGIN")
    print("=" * 60)
    print(f"\nProfile will be saved to: {playwright_profile}")
    print("\nINSTRUCTIONS:")
    print("1. Browser will open to the Trackr login page")
    print("2. Manually log in with your Microsoft account")
    print("3. Complete any 2FA if required")
    print("4. Once you see the Trackr application, press Enter in terminal")
    print("5. Your login will be saved for all future automation runs!")
    print("=" * 60)

    input("\nPress Enter to open browser and login manually...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(playwright_profile),
            headless=False,
            viewport={'width': 1920, 'height': 1080},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check'
            ]
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("\n📂 Opening browser...")
        print("🔐 Please login manually...")

        page.goto(START_QUOTE_URL)

        print("\n⏳ Waiting for you to complete login...")
        print("   (The browser will stay open)")

        input("\n✋ Press Enter after you've successfully logged in and see the Trackr app...")

        # Take a screenshot to confirm
        page.screenshot(path="screenshots/logged_in_state.png", full_page=True)
        print("\n✅ Screenshot saved: screenshots/logged_in_state.png")

        current_url = page.url
        print(f"\n📍 Current URL: {current_url}")

        if "login.microsoftonline.com" in current_url:
            print("\n⚠️  WARNING: Still on login page!")
            print("   Make sure you complete the login before pressing Enter")
        else:
            print("\n🎉 SUCCESS! Login state has been saved!")
            print(f"   Profile location: {playwright_profile}")
            print("\n💡 NEXT STEPS:")
            print("   Run 'python3 run_trackr_auto.py' and it will use this saved login")

        print("\nClosing browser in 5 seconds...")
        time.sleep(5)

        context.close()

    print("\n✅ Profile setup complete!")
    print(f"   Saved to: {playwright_profile}")

if __name__ == "__main__":
    setup_profile()
