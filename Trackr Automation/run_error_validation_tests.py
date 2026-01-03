"""
Error and Validation Test Scenarios
Tests error messages and quote lookup functionality
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import os
from datetime import datetime
from config import BASE_URL, START_QUOTE_URL


def test_1_start_quote_validation_errors(page, output_folder):
    """
    Test 1: Click Next on start-quote page without filling any fields
    Should show validation error messages
    """
    print("\n" + "=" * 60)
    print("TEST 1: Start Quote Validation Errors")
    print("=" * 60)

    page.goto(START_QUOTE_URL)
    page.wait_for_load_state("networkidle")
    print("✓ On start-quote page")

    # Click Embrace button
    page.click('button:has-text("Embrace")')
    time.sleep(1)

    # Click Next without filling any fields
    print("\n📝 Clicking Next without filling required fields...")
    page.click('button:has-text("Next")')
    time.sleep(2)

    # Take screenshot of error messages
    screenshot_path = os.path.join(output_folder, "screenshots", "test1_start_quote_validation_errors.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"✓ Screenshot saved: {screenshot_path}")
    print("✓ Test 1 completed")


def test_2_billing_validation_errors(page, output_folder):
    """
    Test 2: Complete quote flow to billing page, click Purchase Policy without payment info
    Same as E2E but WITHOUT payment info
    """
    print("\n" + "=" * 60)
    print("TEST 2: Billing Validation Errors")
    print("=" * 60)
    print("   Running E2E flow to billing page...")

    # Import the needed classes
    from quote_flow import TrackrQuoteFlow, generate_scenario_config

    page.goto(START_QUOTE_URL)
    page.wait_for_load_state("networkidle")

    # Generate E2E config
    scenario_config = generate_scenario_config("e2e_dog_only")

    quote_flow = TrackrQuoteFlow(page, output_folder=output_folder)

    # Run the flow manually up to billing
    quote_flow.select_brand_button(scenario_config["brand"])
    quote_flow.select_call_source(scenario_config["brand"])
    quote_flow.fill_pet_parent_info(force_name=True)
    quote_flow.fill_phone_number(force_phone=True)
    quote_flow.fill_email()
    zip_code = quote_flow.fill_zip_code()

    quote_flow.click_first_next()

    # Military question
    page.click('span.mat-button-toggle-label-content:has-text("No")')
    time.sleep(0.5)

    quote_flow.click_second_next()

    # Multi-pet question
    page.click('span.mat-button-toggle-label-content:has-text("No")')
    time.sleep(0.5)

    # Add pet
    for pet_config in scenario_config["pets"]:
        quote_flow.add_dog_pet(
            pet_name=pet_config["name"],
            gender=pet_config["gender"],
            is_service_dog=pet_config["is_service_dog"],
            breed=pet_config["breed"],
            age=pet_config["age"]
        )

    quote_flow.click_next_with_arrow()
    time.sleep(3)

    # Continue to billing
    quote_flow.click_next_from_quote_page()
    quote_flow.fill_contact_info_address(zip_code)
    quote_flow.click_next_from_contact_info()
    quote_flow.check_acknowledgements()
    quote_flow.click_next_from_acknowledgements()

    # Now on billing page - DO NOT fill payment info
    print("   On billing page - clicking Purchase Policy without payment info...")

    # Scroll to bottom to find Purchase Policy button
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)

    page.click('button:has-text("Purchase Policy")')
    time.sleep(2)

    screenshot_path = os.path.join(output_folder, "screenshots", "test2_billing_validation_errors.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"✓ Screenshot saved: {screenshot_path}")
    print("✓ Test 2 completed")


def test_3_quote_lookup_by_email(page, output_folder):
    """
    Test 3: Use email from a quote to search on start-quote page
    """
    print("\n" + "=" * 60)
    print("TEST 3: Quote Lookup by Email")
    print("=" * 60)

    # Hardcoded quote email
    email = "testingtrackr20251118131442849@yopmail.com"

    # Start fresh on start-quote page
    page.goto(START_QUOTE_URL)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    print(f"\n🔍 Searching for email: {email}")

    # Step 1: Click Search button to open the search modal
    page.click('button:has-text("Search")')
    time.sleep(1)

    # Step 2: Click on the email field to focus it
    page.click('input[data-quat="input_searchEmail"]')
    time.sleep(0.5)

    # Enter email
    page.fill('input[data-quat="input_searchEmail"]', email)
    time.sleep(0.5)

    # Step 3: Click Search button inside the modal (the yellow one)
    page.locator('button:has-text("Search")').nth(1).click()

    # Step 4: Wait 2s
    time.sleep(2)

    # Step 5: Take screenshot

    # Take screenshot of search results
    screenshot_path = os.path.join(output_folder, "screenshots", "test3_quote_lookup_by_email.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"✓ Screenshot saved: {screenshot_path}")
    print("✓ Test 3 completed")


def test_4_policy_lookup_by_email(page, output_folder):
    """
    Test 4: Use email from a purchased policy to search on start-quote page
    """
    print("" + "=" * 60)
    print("TEST 4: Policy Lookup by Email")
    print("=" * 60)

    # Hardcoded policy email
    policy_email = "testingtrackr20251118132932742@yopmail.com"

    # Start fresh on start-quote page
    page.goto(START_QUOTE_URL)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    print(f"🔍 Searching for purchased policy email: {policy_email}")

    # Step 1: Click Search button to open the search modal
    page.click('button:has-text("Search")')
    time.sleep(1)

    # Step 2: Click on the email field to focus it
    page.click('input[data-quat="input_searchEmail"]')
    time.sleep(0.5)

    # Enter email
    page.fill('input[data-quat="input_searchEmail"]', policy_email)
    time.sleep(0.5)

    # Step 3: Click Search button inside the modal (the yellow one)
    page.locator('button:has-text("Search")').nth(1).click()

    # Step 4: Wait 2s
    time.sleep(2)

    # Step 5: Take screenshot

    # Take screenshot of policy search results
    screenshot_path = os.path.join(output_folder, "screenshots", "test4_policy_lookup_by_email.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"✓ Screenshot saved: {screenshot_path}")
    print("✓ Test 4 completed")



def run_error_validation_tests():
    """Run all 4 error and validation tests"""

    print("=" * 60)
    print("ERROR AND VALIDATION TEST RUNNER")
    print("=" * 60)
    print("\nThis will run 4 tests:")
    print("  1. Start Quote validation errors (click Next without filling)")
    print("  2. Billing validation errors (click Purchase without payment)")
    print("  3. Quote lookup by email")
    print("  4. Policy lookup by email")
    print("=" * 60)

    # Create timestamped output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"output_validation_{timestamp}"
    os.makedirs(os.path.join(output_folder, "screenshots"), exist_ok=True)
    print(f"\n📁 Output folder: {output_folder}")

    input("\nPress Enter to start validation tests...")

    # Use Playwright profile
    playwright_profile_path = str(Path.home() / "playwright-profiles" / "trackr-qa")

    if not Path(playwright_profile_path).exists():
        print(f"\n✗ Playwright profile not found!")
        print(f"\nRun setup first:")
        print(f"  python3 setup_playwright_profile.py")
        return

    with sync_playwright() as p:
        try:
            # Test 1: Start quote validation errors
            context = p.chromium.launch_persistent_context(
                user_data_dir=playwright_profile_path,
                headless=False,
                slow_mo=100,
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
            )
            page = context.pages[0] if context.pages else context.new_page()
            test_1_start_quote_validation_errors(page, output_folder)
            context.close()
            time.sleep(3)

            # Test 2: Billing validation errors
            context = p.chromium.launch_persistent_context(
                user_data_dir=playwright_profile_path,
                headless=False,
                slow_mo=100,
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
            )
            page = context.pages[0] if context.pages else context.new_page()
            test_2_billing_validation_errors(page, output_folder)
            context.close()
            time.sleep(3)

            # Test 3: Quote lookup by email
            context = p.chromium.launch_persistent_context(
                user_data_dir=playwright_profile_path,
                headless=False,
                slow_mo=100,
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
            )
            page = context.pages[0] if context.pages else context.new_page()
            test_3_quote_lookup_by_email(page, output_folder)
            context.close()
            time.sleep(3)

            # Test 4: Policy lookup by email
            context = p.chromium.launch_persistent_context(
                user_data_dir=playwright_profile_path,
                headless=False,
                slow_mo=100,
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
            )
            page = context.pages[0] if context.pages else context.new_page()
            test_4_policy_lookup_by_email(page, output_folder)
            context.close()

            print("\n" + "=" * 60)
            print("ALL VALIDATION TESTS COMPLETED")
            print("=" * 60)
            print(f"\n✓ All 4 tests completed successfully")
            print(f"✓ Screenshots saved to: {output_folder}/screenshots/")
            print("=" * 60)

        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            try:
                error_path = os.path.join(output_folder, "screenshots", "error.png")
                page.screenshot(path=error_path, full_page=True)
                print(f"Error screenshot saved: {error_path}")
            except:
                pass
            try:
                context.close()
            except:
                pass


if __name__ == "__main__":
    run_error_validation_tests()
