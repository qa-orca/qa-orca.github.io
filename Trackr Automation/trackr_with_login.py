"""
Trackr Automation with Login Flow
Handles email/password login and waits for 2FA
"""

from trackr_automation import TrackrAutomation
import os
from pathlib import Path
import time


def main():
    """Main execution with login flow"""
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)

    # Credentials
    email = "mcustard@embracepetinsurance.com"
    password = "+>ZT!Su+)B+.l.A0nF1F13h6M#US@s0"

    # Use Profile 8 (QA Orca) for any existing cookies/session
    chrome_profile_path = str(Path.home() / "Library/Application Support/Google/Chrome/Profile 8")

    print("=" * 60)
    print("Trackr Automation with Login")
    print("=" * 60)
    print(f"\nEmail: {email}")
    print(f"Profile: {chrome_profile_path}")
    print("=" * 60)

    # Initialize automation with Chrome profile
    automation = TrackrAutomation(
        headless=False,
        slow_mo=1000,  # Slower for login process
        user_data_dir=chrome_profile_path
    )

    try:
        print("\n📂 Opening browser...")
        automation.setup()

        print("✓ Page loaded")
        automation.take_screenshot("02_login_page.png")

        # Check if we need to login
        print("\n🔍 Checking for login form...")

        # Wait a moment for page to settle
        time.sleep(2)

        # Try to find email input field
        if automation.page.locator('input[type="email"]').count() > 0:
            print("\n📧 Email field found - logging in...")

            # Fill email
            automation.page.locator('input[type="email"]').fill(email)
            print(f"   Filled email: {email}")
            automation.take_screenshot("03_email_filled.png")

            # Look for Next/Continue button and click it
            time.sleep(1)

            # Try various button selectors
            if automation.page.locator('button:has-text("Next")').count() > 0:
                automation.page.locator('button:has-text("Next")').click()
                print("   Clicked 'Next' button")
            elif automation.page.locator('button:has-text("Continue")').count() > 0:
                automation.page.locator('button:has-text("Continue")').click()
                print("   Clicked 'Continue' button")
            elif automation.page.locator('button[type="submit"]').count() > 0:
                automation.page.locator('button[type="submit"]').first.click()
                print("   Clicked submit button")

            time.sleep(2)
            automation.take_screenshot("04_after_email.png")

            # Wait for password field
            print("\n🔐 Waiting for password field...")
            automation.page.wait_for_selector('input[type="password"]', timeout=10000)

            # Fill password
            automation.page.locator('input[type="password"]').fill(password)
            print("   Filled password")
            automation.take_screenshot("05_password_filled.png")

            time.sleep(1)

            # Click submit/login button
            if automation.page.locator('button:has-text("Sign in")').count() > 0:
                automation.page.locator('button:has-text("Sign in")').click()
                print("   Clicked 'Sign in' button")
            elif automation.page.locator('button:has-text("Login")').count() > 0:
                automation.page.locator('button:has-text("Login")').click()
                print("   Clicked 'Login' button")
            elif automation.page.locator('button[type="submit"]').count() > 0:
                automation.page.locator('button[type="submit"]').first.click()
                print("   Clicked submit button")

            time.sleep(3)
            automation.take_screenshot("06_after_password.png")

            # Wait for 2FA
            print("\n🔒 Waiting for 2FA...")
            print("   Please complete 2FA manually in the browser")
            print("   The script will wait up to 2 minutes...")

            # Wait for navigation or 2FA completion
            # We'll wait for the URL to change to the quoting page
            try:
                automation.page.wait_for_url("**/quoting/**", timeout=120000)
                print("\n✓ Login successful!")
            except:
                print("\n⚠️  Timeout waiting for login - may need manual intervention")

            automation.take_screenshot("07_after_2fa.png")

        else:
            print("✓ Already logged in!")

        print("\n" + "=" * 60)
        print("Current URL:", automation.page.url)
        print("=" * 60)

        # Explore the page after login
        print("\n🔍 Exploring page elements...")
        automation.explore_page()

        automation.take_screenshot("08_final_page.png")

        print("\n" + "=" * 60)
        print("AUTOMATION COMPLETE")
        print("=" * 60)
        print("\nBrowser will remain open for 60 seconds...")
        print("Check screenshots/ directory for captured images")
        print("=" * 60)

        time.sleep(60)

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        try:
            automation.take_screenshot("error.png")
            print("Error screenshot saved")
        except:
            pass
    finally:
        automation.teardown()
        print("\n✓ Done")


if __name__ == "__main__":
    main()
