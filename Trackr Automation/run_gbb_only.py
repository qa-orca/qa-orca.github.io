"""
Good/Better/Best ONLY scenario runner
Runs only the 3 GBB scenarios (pets under 15 with Good/Better/Best testing)
"""

from quote_flow import main
import time
import os
from datetime import datetime

# Define Good/Better/Best scenarios ONLY (3 total)
SCENARIOS_TO_RUN = [
    # Good/Better/Best scenarios (3) - Pets under 15, WITH GBB testing
    ("gbb_dog_young", None),  # 1. Dog under 15 - full coverage with GBB
    ("gbb_cat_young", None),  # 2. Cat under 15 - full coverage with GBB
    ("gbb_one_of_each_young", None),  # 3. Dog + Cat both under 15 - full coverage with GBB (2 accordions)
]


def run_gbb_only_batch():
    """Run Good/Better/Best scenarios only"""

    print("=" * 60)
    print("GOOD/BETTER/BEST ONLY SCENARIO RUNNER")
    print("=" * 60)
    print(f"\nTotal scenarios to run: {len(SCENARIOS_TO_RUN)}")
    print("\nThis will run:")
    print("  - 3 Good/Better/Best scenarios (age under 15)")
    print("\nGBB scenarios:")
    print("  1. Dog under 15 - test Good/Better/Best options")
    print("  2. Cat under 15 - test Good/Better/Best options")
    print("  3. Dog + Cat both under 15 - test GBB (2 accordions)")
    print(f"\nTotal: {len(SCENARIOS_TO_RUN)} scenarios")
    print("=" * 60)

    # Create single timestamped output folder for all scenarios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"output_gbb_only_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)
    print(f"\n📁 Output folder: {output_folder}")
    print(f"   All scenarios will save to this folder")

    input("\nPress Enter to start GBB-only test run...")

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
    print("GBB-ONLY TEST RUN COMPLETE")
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

    print("\n📁 Output saved to: {}/".format(output_folder))
    print("   - JSON files: {}/json/".format(output_folder))
    print("   - Screenshots: {}/screenshots/".format(output_folder))
    print("=" * 60)


if __name__ == "__main__":
    run_gbb_only_batch()
