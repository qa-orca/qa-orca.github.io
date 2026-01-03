"""
Batch runner for quote scenarios
Covers all toggle variations and journey types
"""

from quote_flow import main
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from pathlib import Path
from config import START_QUOTE_URL
import json
import glob


def run_validation_tests(output_folder, batch_results):
    """Run validation tests after batch scenarios complete"""

    print("\n\n")
    print("=" * 60)
    print("RUNNING VALIDATION TESTS")
    print("=" * 60)
    print("\nThis will run 4 validation tests:")
    print("  1. Start Quote validation errors")
    print("  2. Billing validation errors")
    print("  3. Quote lookup by email")
    print("  4. Policy lookup by email")
    print("=" * 60)

    response = input("\nRun validation tests? (y/n): ")
    if response.lower() != 'y':
        print("Skipping validation tests.")
        return

    # Use Playwright profile
    playwright_profile_path = str(Path.home() / "playwright-profiles" / "trackr-qa")

    if not Path(playwright_profile_path).exists():
        print(f"\n✗ Playwright profile not found!")
        return

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=playwright_profile_path,
            headless=False,
            slow_mo=100,
            viewport={'width': 1920, 'height': 1080},
            args=['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            # Test 1: Start quote validation errors
            print("\n" + "█" * 60)
            print("TEST 1: Start Quote Validation Errors")
            print("█" * 60)

            page.goto(START_QUOTE_URL)
            page.wait_for_load_state("networkidle")
            page.click('button:has-text("Embrace")')
            time.sleep(1)
            page.click('button:has-text("Next")')
            time.sleep(2)

            screenshot_path = os.path.join(output_folder, "screenshots", "validation_test1_start_quote_errors.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"✓ Screenshot saved: {screenshot_path}")

            time.sleep(3)

            # Test 2: Billing validation errors
            # Same as E2E but WITHOUT payment info
            print("\n" + "█" * 60)
            print("TEST 2: Billing Validation Errors")
            print("█" * 60)
            print("   Running E2E flow to billing page...")

            # Run an E2E scenario but we'll intercept at billing
            # Use the TrackrQuoteFlow class directly
            from quote_flow import TrackrQuoteFlow, generate_scenario_config

            page.goto(START_QUOTE_URL)
            page.wait_for_load_state("networkidle")

            # Generate E2E config
            scenario_config = generate_scenario_config("e2e_dog_only")

            # Override to ensure we have specific data for this test
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            test_email = f"testbilling{timestamp}@yopmail.com"

            quote_flow = TrackrQuoteFlow(page, output_folder=output_folder)

            # Run the flow manually up to billing
            quote_flow.select_brand_button(scenario_config["brand"])
            call_source = quote_flow.select_call_source(scenario_config["brand"])
            quote_flow.fill_pet_parent_info(force_name=True)
            quote_flow.fill_phone_number(force_phone=True)
            # Override email
            page.fill('input[formcontrolname="email"]', test_email)
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

            screenshot_path = os.path.join(output_folder, "screenshots", "validation_test2_billing_errors.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"✓ Screenshot saved: {screenshot_path}")

            time.sleep(3)

            # Test 3: Quote lookup by email
            print("\n" + "█" * 60)
            print("TEST 3: Quote Lookup by Email")
            print("█" * 60)

            # Find a quote email from JSON files (non-E2E scenarios)
            quote_email = None
            json_files = glob.glob(os.path.join(output_folder, "json", "*.json"))
            for json_file in json_files:
                # Skip E2E scenarios - we want a quote, not a policy
                if "e2e_" not in os.path.basename(json_file):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if "email" in data:
                                quote_email = data["email"]
                                print(f"   Found quote email from: {os.path.basename(json_file)}")
                                break
                    except:
                        continue

            if quote_email:
                # Start completely fresh - close any open browser state
                page.goto(START_QUOTE_URL)
                page.wait_for_load_state("networkidle")
                time.sleep(2)

                print(f"   Searching for: {quote_email}")

                # Step 1: Click Search button to open the search modal
                page.click('button:has-text("Search")')
                time.sleep(1)

                # Step 2: Click on the email field to focus it
                page.click('input[data-quat="input_searchEmail"]')
                time.sleep(0.5)

                # Enter email
                page.fill('input[data-quat="input_searchEmail"]', quote_email)
                time.sleep(0.5)

                # Step 3: Click Search button inside the modal (the yellow one)
                page.locator('button:has-text("Search")').nth(1).click()

                # Step 4: Wait 2s
                time.sleep(2)

                screenshot_path = os.path.join(output_folder, "screenshots", "validation_test3_quote_lookup.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"✓ Screenshot saved: {screenshot_path}")
            else:
                print("   ⚠️  No quote email found in JSON files, skipping test 3")

            time.sleep(3)

            # Test 4: Policy lookup by email
            print("\n" + "█" * 60)
            print("TEST 4: Policy Lookup by Email")
            print("█" * 60)

            # Find a policy email from JSON files (E2E scenarios only)
            policy_email = None
            json_files = glob.glob(os.path.join(output_folder, "json", "*.json"))
            for json_file in json_files:
                # Only look at E2E scenarios - these are purchased policies
                if "e2e_" in os.path.basename(json_file):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if "email" in data:
                                policy_email = data["email"]
                                print(f"   Found policy email from: {os.path.basename(json_file)}")
                                break
                    except:
                        continue

            if policy_email:
                # Start completely fresh - close any open browser state
                page.goto(START_QUOTE_URL)
                page.wait_for_load_state("networkidle")
                time.sleep(2)

                print(f"   Searching for: {policy_email}")

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

                screenshot_path = os.path.join(output_folder, "screenshots", "validation_test4_policy_lookup.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"✓ Screenshot saved: {screenshot_path}")
            else:
                print("   ⚠️  No policy email found in JSON files, skipping test 4")

            print("\n" + "=" * 60)
            print("ALL VALIDATION TESTS COMPLETED")
            print("=" * 60)

        except Exception as e:
            print(f"\n✗ Validation test failed: {str(e)}")
            error_path = os.path.join(output_folder, "screenshots", "validation_error.png")
            page.screenshot(path=error_path, full_page=True)
            print(f"Error screenshot saved: {error_path}")

        finally:
            time.sleep(3)
            context.close()


# Define all scenario combinations to test
# Coverage:
# - Regular quote generation (various toggle combinations)
# - USAA scenarios (dog and cat)
# - Geico scenarios (dog and cat)
# - Embrace E2E scenarios (4 total: 1 dog, 1 cat, 2 multi-pet)
# - Good/Better/Best scenarios with age 15 cutoff (6 scenarios)

SCENARIOS_TO_RUN = [
    # Bind Online Journey (2 scenarios)
    ("dog_only", "Bind Online Journey"),
    ("cat_only", "Bind Online Journey"),

    # Save & Close Record (2 scenarios)
    ("multi_pet", "Save & Close Record"),
    ("one_of_each", "Save & Close Record"),

    # USAA scenarios - will select "USAA, California" (2)
    ("usaa_dog_only", None),
    ("usaa_cat_only", None),

    # Geico scenarios - will select "Geico, California" (2)
    ("geico_dog_only", None),
    ("geico_cat_only", None),

    # Variety of Embrace quotes with different toggles (16 scenarios)
    # These randomly vary: Military, Gender, Service Dog, Multi-pet answer, Quote Journey
    ("dog_only", None),
    ("dog_only", None),
    ("dog_only", None),
    ("dog_only", None),
    ("cat_only", None),
    ("cat_only", None),
    ("cat_only", None),
    ("cat_only", None),
    ("multi_pet", None),  # 2 dogs OR 2 cats
    ("multi_pet", None),
    ("multi_pet", None),
    ("multi_pet", None),
    ("one_of_each", None),  # 1 dog + 1 cat
    ("one_of_each", None),
    ("one_of_each", None),
    ("one_of_each", None),

    # Embrace E2E scenarios (complete purchase flow) (4)
    ("e2e_dog_only", None),
    ("e2e_cat_only", None),
    ("e2e_multi_pet", None),
    ("e2e_multi_pet", None),

    # E2E Tier Selection scenarios (3) - open accordion, select tier, complete purchase
    ("e2e_tier_good", None),    # Select Good tier, complete purchase
    ("e2e_tier_better", None),  # Select Better tier, complete purchase
    ("e2e_tier_best", None),    # Select Best tier, complete purchase

    # Accident-only scenarios (3) - Age 15, no GBB testing
    ("gbb_accident_dog_15", None),  # Dog aged 15 - accident-only
    ("gbb_accident_cat_15", None),  # Cat aged 15 - accident-only
    ("gbb_accident_mixed_age", None),  # Dog young + Cat 15 - mixed coverage

    # Good/Better/Best scenarios (3) - Pets under 15, WITH GBB testing
    ("gbb_dog_young", None),  # Dog under 15 - full coverage with GBB
    ("gbb_cat_young", None),  # Cat under 15 - full coverage with GBB
    ("gbb_one_of_each_young", None),  # Dog + Cat both under 15 - GBB (2 accordions)
]


def run_batch():
    """Run all scenarios in batch mode"""

    print("=" * 60)
    print("BATCH SCENARIO RUNNER")
    print("=" * 60)
    print(f"\nTotal scenarios to run: {len(SCENARIOS_TO_RUN)}")
    print("\nThis will run:")
    print("  - 2 Bind Online Journey")
    print("  - 2 Save & Close Record")
    print("  - 2 USAA (USAA, California)")
    print("  - 2 Geico (Geico, California)")
    print("  - 16 Variety of Embrace quotes (random toggles)")
    print("  - 4 Embrace E2E (complete purchase)")
    print("  - 3 E2E Tier Selection (Good/Better/Best)")
    print("  - 3 Accident-only (age 15)")
    print("  - 3 Good/Better/Best (age under 15)")
    print(f"\nTotal: {len(SCENARIOS_TO_RUN)} scenarios")
    print("\nAfter batch completes, you'll be prompted to run:")
    print("  - 4 Validation tests (errors + quote/policy lookup)")
    print("=" * 60)

    # Create single timestamped output folder for all scenarios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"output_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)
    print(f"\n📁 Output folder: {output_folder}")
    print(f"   All scenarios will save to this folder")

    input("\nPress Enter to start batch run...")

    results = []

    for idx, scenario_info in enumerate(SCENARIOS_TO_RUN, 1):
        # Unpack tuple (scenario_type, quote_journey)
        scenario_type, quote_journey = scenario_info

        # Make scenario name unique by appending index
        unique_scenario_name = f"{scenario_type}_{idx}"

        print("\n\n")
        print("█" * 60)
        print(f"RUNNING SCENARIO {idx}/{len(SCENARIOS_TO_RUN)}")
        print(f"Type: {scenario_type}")
        if quote_journey:
            print(f"Journey: {quote_journey}")
        print("█" * 60)

        try:
            # Run the scenario with shared output folder, specific quote journey, and unique name
            main(scenario_type, output_folder=output_folder, quote_journey=quote_journey, scenario_name=unique_scenario_name)
            results.append({"scenario": idx, "type": scenario_type, "status": "SUCCESS"})
            print(f"\n✓ Scenario {idx} completed successfully")

        except Exception as e:
            results.append({"scenario": idx, "type": scenario_type, "status": "FAILED", "error": str(e)})
            print(f"\n✗ Scenario {idx} failed: {str(e)}")

            # Ask user if they want to continue
            response = input("\nContinue with remaining scenarios? (y/n): ")
            if response.lower() != 'y':
                break

        # Brief pause between scenarios
        if idx < len(SCENARIOS_TO_RUN):
            print("\nWaiting 3 seconds before next scenario...")
            time.sleep(3)

    # Print final summary
    print("\n\n")
    print("=" * 60)
    print("BATCH RUN COMPLETE")
    print("=" * 60)

    successful = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = sum(1 for r in results if r["status"] == "FAILED")

    print(f"\nTotal scenarios run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed scenarios:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - Scenario {r['scenario']} ({r['type']}): {r.get('error', 'Unknown error')}")

    print("=" * 60)

    # Now run the 4 validation tests
    run_validation_tests(output_folder, results)


if __name__ == "__main__":
    run_batch()
