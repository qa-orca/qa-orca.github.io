"""
E2E Tier Selection Scenario Runner
Runs 3 scenarios that complete full purchase flow with specific tier selection:
1. Good tier - create quote, open accordion, select Good, complete purchase
2. Better tier - create quote, open accordion, select Better, complete purchase
3. Best tier - create quote, open accordion, select Best, complete purchase
"""

from quote_flow import main
import time
import os
from datetime import datetime

# Define tier E2E scenarios
TIER_SCENARIOS = [
    ("e2e_tier_good", None),    # Create quote, open accordion, select Good, complete purchase
    ("e2e_tier_better", None),  # Create quote, open accordion, select Better, complete purchase
    ("e2e_tier_best", None),    # Create quote, open accordion, select Best, complete purchase
]


def run_tier_e2e_batch():
    """Run all tier E2E scenarios"""

    print("=" * 60)
    print("E2E TIER SELECTION SCENARIO RUNNER")
    print("=" * 60)
    print(f"\nTotal scenarios to run: {len(TIER_SCENARIOS)}")
    print("\nScenarios:")
    print("  1. Good tier - create quote, open accordion, select Good, complete purchase")
    print("  2. Better tier - create quote, open accordion, select Better, complete purchase")
    print("  3. Best tier - create quote, open accordion, select Best, complete purchase")
    print("\nEach scenario completes:")
    print("  1. Quote flow (brand, pet parent, pet)")
    print("  2. Open coverage accordion")
    print("  3. Select specific tier (Good/Better/Best)")
    print("  4. Contact information page")
    print("  5. Mailing address with Google autocomplete")
    print("  6. Acknowledgements checkbox")
    print("  7. Billing information (card: 4242...)")
    print("  8. Purchase Policy")
    print("=" * 60)

    # Create single timestamped output folder for all scenarios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"output_tier_e2e_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)
    print(f"\nOutput folder: {output_folder}")
    print(f"   All scenarios will save to this folder")

    input("\nPress Enter to start tier E2E batch run...")

    results = []

    for idx, scenario_info in enumerate(TIER_SCENARIOS, 1):
        scenario_type, quote_journey = scenario_info
        unique_scenario_name = f"{scenario_type}_{idx}"

        print("\n\n")
        print("=" * 60)
        print(f"RUNNING TIER SCENARIO {idx}/{len(TIER_SCENARIOS)}")
        print(f"Scenario: {scenario_type.upper().replace('_', ' ')}")
        print("=" * 60)

        try:
            main(scenario_type, output_folder=output_folder, quote_journey=quote_journey, scenario_name=unique_scenario_name)
            results.append({"scenario": idx, "type": scenario_type, "status": "SUCCESS"})
            print(f"\nScenario {idx} completed successfully")

        except Exception as e:
            results.append({"scenario": idx, "type": scenario_type, "status": "FAILED", "error": str(e)})
            print(f"\nScenario {idx} failed: {str(e)}")

            response = input("\nContinue with remaining scenarios? (y/n): ")
            if response.lower() != 'y':
                break

        if idx < len(TIER_SCENARIOS):
            print("\nWaiting 3 seconds before next scenario...")
            time.sleep(3)

    # Print final summary
    print("\n\n")
    print("=" * 60)
    print("TIER E2E BATCH RUN COMPLETE")
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

    print(f"\nOutput saved to: {output_folder}/")
    print(f"   - JSON files: {output_folder}/json/")
    print(f"   - Screenshots: {output_folder}/screenshots/")
    print("=" * 60)


if __name__ == "__main__":
    run_tier_e2e_batch()
