"""
Trackr Automation using Chrome Profile (with persistent authentication)
This script uses your existing Chrome profile so you're already logged in
"""

from trackr_automation import TrackrAutomation
import os
from pathlib import Path


def get_default_chrome_path():
    """Get the QA Orca Chrome profile path for macOS"""
    # Profile 8 is the QA Orca profile
    chrome_path = Path.home() / "Library/Application Support/Google/Chrome/Profile 8"
    return str(chrome_path)


def main():
    """Main execution using Chrome profile"""
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)

    # Get Chrome profile path
    chrome_profile_path = get_default_chrome_path()

    print("=" * 60)
    print("Trackr Automation with Chrome Profile")
    print("=" * 60)
    print(f"\nUsing Chrome profile: {chrome_profile_path}")
    print("\nNOTE: Close all Chrome windows before running this script!")
    print("Playwright needs exclusive access to the profile.")
    print("=" * 60)

    # Check if path exists
    if not Path(chrome_profile_path).exists():
        print(f"\n✗ Chrome profile not found at: {chrome_profile_path}")
        print("\nRun 'python find_chrome_profile.py' to find your Chrome profile path")
        return

    input("\nPress Enter to continue (make sure Chrome is closed)...")

    # Initialize automation with Chrome profile
    automation = TrackrAutomation(
        headless=False,
        slow_mo=500,
        user_data_dir=chrome_profile_path
    )

    try:
        print("\n📂 Opening browser with your Chrome profile...")
        print("   You should already be logged in with your Google account")

        # Setup and navigate
        automation.setup()

        print("\n✓ Page loaded successfully!")
        print("\n" + "=" * 60)

        # Explore the page
        automation.explore_page()

        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("\n1. Check if you're logged in automatically")
        print("2. Review the form elements printed above")
        print("3. Customize fill_quote_form() with actual field names")
        print("4. Add automation steps as needed")
        print("\n" + "=" * 60)

        # Keep browser open for inspection
        input("\nPress Enter to close browser...")

    except Exception as e:
        print(f"\n✗ Error during automation: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure all Chrome windows are closed")
        print("2. Verify the profile path is correct")
        print("3. Try running: python find_chrome_profile.py")
        try:
            automation.take_screenshot("error.png")
        except:
            pass
    finally:
        automation.teardown()


if __name__ == "__main__":
    main()
