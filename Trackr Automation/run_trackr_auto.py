"""
Trackr Automation using Chrome Profile (non-interactive version)
Run directly without user prompts
"""

from trackr_automation import TrackrAutomation
import os
from pathlib import Path
import time


def main():
    """Main execution using Playwright profile"""
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)

    # Use Playwright-specific profile (not Chrome profile)
    playwright_profile_path = str(Path.home() / "playwright-profiles" / "trackr-qa")

    print("=" * 60)
    print("Trackr Automation with Saved Login")
    print("=" * 60)
    print(f"\nUsing profile: {playwright_profile_path}")
    print("=" * 60)

    # Check if path exists
    if not Path(playwright_profile_path).exists():
        print(f"\n✗ Playwright profile not found!")
        print(f"\nYou need to run the one-time setup first:")
        print(f"  python3 setup_playwright_profile.py")
        print(f"\nThis will let you login once, then all future runs will skip login.")
        return

    # Initialize automation with Playwright profile
    automation = TrackrAutomation(
        headless=False,
        slow_mo=500,
        user_data_dir=playwright_profile_path
    )

    try:
        print("\n📂 Opening browser with saved login profile...")
        print("   You should already be logged in to Microsoft")

        # Setup and navigate
        automation.setup()

        print("\n✓ Page loaded successfully!")
        print("\n" + "=" * 60)

        # Explore the page
        automation.explore_page()

        print("\n" + "=" * 60)
        print("AUTOMATION COMPLETE")
        print("=" * 60)
        print("\nCheck the screenshots/ directory for captured images")
        print("Browser will remain open for 30 seconds for inspection...")
        print("\n" + "=" * 60)

        # Keep browser open for inspection
        time.sleep(30)

    except Exception as e:
        print(f"\n✗ Error during automation: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure all Chrome windows are closed")
        print("2. Verify the profile path is correct")
        print("3. Run: python3 find_chrome_profile.py")
        try:
            automation.take_screenshot("error.png")
            print("\nError screenshot saved to: screenshots/error.png")
        except:
            pass
    finally:
        automation.teardown()
        print("\n✓ Automation completed")


if __name__ == "__main__":
    main()
