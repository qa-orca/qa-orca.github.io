"""
Parallel test runner - Runs 4 tests concurrently
Executes multiple quote scenarios simultaneously for faster test execution
"""

import subprocess
import time
from datetime import datetime
import os

# Define all scenario combinations to test
SCENARIOS_TO_RUN = [
    # Dog scenarios (6 combinations)
    "dog_only",
    "dog_only",
    "dog_only",
    "dog_only",
    "dog_only",
    "dog_only",

    # Cat scenarios (6 combinations)
    "cat_only",
    "cat_only",
    "cat_only",
    "cat_only",
    "cat_only",
    "cat_only",

    # Multi-pet scenarios (4 combinations - 2 dogs or 2 cats)
    "multi_pet",
    "multi_pet",
    "multi_pet",
    "multi_pet",

    # One of each scenarios (4 combinations - 1 dog + 1 cat)
    "one_of_each",
    "one_of_each",
    "one_of_each",
    "one_of_each",
]

PARALLEL_WORKERS = 1  # Run tests one at a time (profile sharing limitation)


def run_scenario_process(scenario_type: str, batch_num: int, scenario_num: int):
    """
    Run a single scenario as a subprocess

    Args:
        scenario_type: Type of scenario (dog_only, cat_only, multi_pet)
        batch_num: Batch number
        scenario_num: Scenario number within batch

    Returns:
        subprocess.Popen object
    """
    print(f"  [Batch {batch_num}, Slot {scenario_num}] Starting {scenario_type}...")

    # Run the scenario
    process = subprocess.Popen(
        ["python3", "quote_flow.py", scenario_type],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return process


def run_parallel_batch():
    """Run all scenarios in parallel batches of 4"""

    print("=" * 60)
    print("PARALLEL TEST RUNNER - 4 Tests at a Time")
    print("=" * 60)
    print(f"\nTotal scenarios to run: {len(SCENARIOS_TO_RUN)}")
    print(f"Parallel workers: {PARALLEL_WORKERS}")
    print(f"Estimated batches: {(len(SCENARIOS_TO_RUN) + PARALLEL_WORKERS - 1) // PARALLEL_WORKERS}")
    print("\nThis will run:")
    print(f"  - {SCENARIOS_TO_RUN.count('dog_only')} Dog-only scenarios")
    print(f"  - {SCENARIOS_TO_RUN.count('cat_only')} Cat-only scenarios")
    print(f"  - {SCENARIOS_TO_RUN.count('multi_pet')} Multi-pet scenarios (2 dogs or 2 cats)")
    print(f"  - {SCENARIOS_TO_RUN.count('one_of_each')} One-of-each scenarios (1 dog + 1 cat)")
    print("=" * 60)

    input("\nPress Enter to start parallel batch run...")

    start_time = datetime.now()
    results = []

    # Process scenarios in batches of 4
    for batch_idx in range(0, len(SCENARIOS_TO_RUN), PARALLEL_WORKERS):
        batch_num = (batch_idx // PARALLEL_WORKERS) + 1
        batch = SCENARIOS_TO_RUN[batch_idx:batch_idx + PARALLEL_WORKERS]

        print("\n" + "█" * 60)
        print(f"BATCH {batch_num} - Running {len(batch)} tests in parallel")
        print("█" * 60)

        # Start all processes in this batch
        processes = []
        for slot_num, scenario_type in enumerate(batch, 1):
            process = run_scenario_process(scenario_type, batch_num, slot_num)
            processes.append({
                "process": process,
                "scenario_type": scenario_type,
                "batch": batch_num,
                "slot": slot_num,
                "scenario_num": batch_idx + slot_num
            })

        # Wait for all processes in this batch to complete
        for proc_info in processes:
            stdout, stderr = proc_info["process"].wait(), None
            exit_code = proc_info["process"].returncode

            if exit_code == 0:
                status = "SUCCESS"
                print(f"  ✓ [Batch {proc_info['batch']}, Slot {proc_info['slot']}] {proc_info['scenario_type']} completed")
            else:
                status = "FAILED"
                print(f"  ✗ [Batch {proc_info['batch']}, Slot {proc_info['slot']}] {proc_info['scenario_type']} failed (exit code {exit_code})")

            results.append({
                "scenario": proc_info['scenario_num'],
                "type": proc_info['scenario_type'],
                "status": status,
                "batch": proc_info['batch'],
                "slot": proc_info['slot']
            })

        print(f"\n✓ Batch {batch_num} complete!")

        # Brief pause between batches
        if batch_idx + PARALLEL_WORKERS < len(SCENARIOS_TO_RUN):
            print("\nWaiting 3 seconds before next batch...")
            time.sleep(3)

    # Print final summary
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n\n")
    print("=" * 60)
    print("PARALLEL BATCH RUN COMPLETE")
    print("=" * 60)

    successful = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = sum(1 for r in results if r["status"] == "FAILED")

    print(f"\nTotal scenarios run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {duration}")
    print(f"Average time per scenario: {duration / len(results) if results else 'N/A'}")

    if failed > 0:
        print("\nFailed scenarios:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - Scenario {r['scenario']} ({r['type']}) - Batch {r['batch']}, Slot {r['slot']}")

    print("\n" + "=" * 60)
    print(f"Run completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    # Make sure screenshots directory exists
    os.makedirs("screenshots", exist_ok=True)

    run_parallel_batch()
