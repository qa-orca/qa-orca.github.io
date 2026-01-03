"""
End-to-End scenario runner
Runs scenarios that complete the full quote flow including contact info, acknowledgements, billing, and purchase
"""

from quote_flow import main
import time
import os
from datetime import datetime

# Define end-to-end scenarios to test
# These complete the entire purchase flow: quote -> contact -> acknowledgements -> billing -> purchase
E2E_SCENARIOS_TO_RUN = [
    # End-to-end Dog scenario
    "e2e_dog_only",

    # End-to-end Cat scenario
    "e2e_cat_only",

    # End-to-end Multi-pet scenarios (2 dogs or 2 cats)
    "e2e_multi_pet",
    "e2e_multi_pet",
]


def run_e2e_batch():
    """Run all end-to-end scenarios"""

    print("=" * 60)
    print("END-TO-END SCENARIO RUNNER (COMPLETE PURCHASE)")
    print("=" * 60)
    print(f"\nTotal scenarios to run: {len(E2E_SCENARIOS_TO_RUN)}")
    print("\nBreakdown:")
    print(f"  - {E2E_SCENARIOS_TO_RUN.count('e2e_dog_only')} E2E Dog-only")
    print(f"  - {E2E_SCENARIOS_TO_RUN.count('e2e_cat_only')} E2E Cat-only")
    print(f"  - {E2E_SCENARIOS_TO_RUN.count('e2e_multi_pet')} E2E Multi-pet (2 dogs or 2 cats)")
    print("\nEach scenario completes:")
    print("  1. Quote flow (brand, pet parent, pets)")
    print("  2. Contact information page")
    print("  3. Mailing address with Google autocomplete")
    print("  4. Acknowledgements checkbox")
    print("  5. Billing information (card: 4242...)")
    print("  6. Purchase Policy")
    print("=" * 60)

    # Create single timestamped output folder for all scenarios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = f"output_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)
    print(f"\n📁 Output folder: {output_folder}")
    print(f"   All scenarios will save to this folder")

    input("\nPress Enter to start end-to-end batch run...")

    results = []

    for idx, scenario_type in enumerate(E2E_SCENARIOS_TO_RUN, 1):
        # Make scenario name unique by appending index
        unique_scenario_name = f"{scenario_type}_{idx}"

        print("\n\n")
        print("█" * 60)
        print(f"RUNNING E2E SCENARIO {idx}/{len(E2E_SCENARIOS_TO_RUN)}")
        print("█" * 60)

        try:
            # Run the scenario with shared output folder and unique name
            main(scenario_type, output_folder=output_folder, scenario_name=unique_scenario_name)
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
        if idx < len(E2E_SCENARIOS_TO_RUN):
            print("\nWaiting 3 seconds before next scenario...")
            time.sleep(3)

    # Print final summary
    print("\n\n")
    print("=" * 60)
    print("E2E BATCH RUN COMPLETE")
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
    run_e2e_batch()
