"""
Geico, USAA, and E2E scenario runner
Runs only brand-specific and end-to-end scenarios
"""

from quote_flow import main
import time
import os
from datetime import datetime

# Define scenarios to test
SCENARIOS_TO_RUN = [
    # USAA scenarios (2)
    ("usaa_dog_only", None),
    ("usaa_cat_only", None),

    # Geico scenarios (2)
    ("geico_dog_only", None),
    ("geico_cat_only", None),

    # Embrace E2E scenarios (4)
    ("e2e_dog_only", None),
    ("e2e_cat_only", None),
    ("e2e_multi_pet", None),
    ("e2e_multi_pet", None),
]


def run_test_batch():
    """Run Geico, USAA, and E2E scenarios"""

    print("=" * 60)
    print("GEICO, USAA, AND E2E SCENARIO RUNNER")
    print("=" * 60)
    print(f"\nTotal scenarios to run: {len(SCENARIOS_TO_RUN)}")
    print("\nThis will run:")
    print("  - 2 USAA (USAA, California)")
    print("  - 2 Geico (Geico, California)")
    print("  - 4 Embrace E2E (complete purchase)")
    print(f"\nTotal: {len(SCENARIOS_TO_RUN)} scenarios")
    print("=" * 60)

    # Create single timestamped output folder for all scenarios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"output_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)
    print(f"\n📁 Output folder: {output_folder}")
    print(f"   All scenarios will save to this folder")

    input("\nPress Enter to start test run...")

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
    print("TEST RUN COMPLETE")
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


if __name__ == "__main__":
    run_test_batch()
