"""
Parallel test runner - FIXED VERSION
Creates separate profile copies for each parallel worker to avoid conflicts
"""

import subprocess
import time
from datetime import datetime
import os
import shutil
from pathlib import Path
from config import START_QUOTE_URL

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

PARALLEL_WORKERS = 4  # Run 4 tests at a time


def setup_worker_profiles(num_workers: int):
    """Create separate profile copies for each worker"""
    base_profile = Path.home() / "playwright-profiles" / "trackr-qa"

    if not base_profile.exists():
        print(f"✗ Base profile not found at: {base_profile}")
        print("Please run: python3 setup_playwright_profile.py")
        return None

    print(f"\n📂 Creating {num_workers} profile copies...")
    worker_profiles = []

    for i in range(num_workers):
        worker_profile = Path.home() / "playwright-profiles" / f"trackr-qa-worker-{i+1}"

        # Remove old worker profile if exists
        if worker_profile.exists():
            shutil.rmtree(worker_profile)

        # Copy base profile to worker profile
        shutil.copytree(base_profile, worker_profile)
        worker_profiles.append(str(worker_profile))
        print(f"  ✓ Worker {i+1} profile created")

    return worker_profiles


def cleanup_worker_profiles(worker_profiles: list):
    """Clean up worker profile copies"""
    print(f"\n🧹 Cleaning up worker profiles...")
    for profile in worker_profiles:
        try:
            if Path(profile).exists():
                shutil.rmtree(profile)
        except Exception as e:
            print(f"  Warning: Could not remove {profile}: {e}")
    print("  ✓ Cleanup complete")


def run_scenario_process(scenario_type: str, worker_profile: str, batch_num: int, scenario_num: int):
    """
    Run a single scenario as a subprocess with dedicated worker profile

    Args:
        scenario_type: Type of scenario
        worker_profile: Path to worker's dedicated profile
        batch_num: Batch number
        scenario_num: Scenario number

    Returns:
        subprocess.Popen object
    """
    print(f"  [Batch {batch_num}, Slot {scenario_num}] Starting {scenario_type}...")

    # Create a modified version of quote_flow that uses the worker profile
    env = os.environ.copy()
    env['WORKER_PROFILE'] = worker_profile

    process = subprocess.Popen(
        ["python3", "-c", f"""
import sys
import os
sys.path.insert(0, '{os.getcwd()}')
from quote_flow import main, generate_scenario_config
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

# Use worker profile from environment
worker_profile = os.environ.get('WORKER_PROFILE')

# Override main to use worker profile
scenario_config = generate_scenario_config('{scenario_type}')

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=worker_profile,
        headless=False,
        slow_mo=500,
        viewport={{'width': 1920, 'height': 1080}},
        args=['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
    )

    page = context.pages[0] if context.pages else context.new_page()

    try:
        from quote_flow import TrackrQuoteFlow
        page.goto(START_QUOTE_URL)
        page.wait_for_load_state("networkidle")

        quote_flow = TrackrQuoteFlow(page)
        result = quote_flow.complete_quote_flow(scenario_config)

        time.sleep(5)  # Brief wait instead of 10s for parallel runs
    except Exception as e:
        print(f"Error: {{e}}")
        raise
    finally:
        context.close()
"""],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    return process


def run_parallel_batch():
    """Run all scenarios in parallel batches of 4 with separate profiles"""

    print("=" * 60)
    print("PARALLEL TEST RUNNER - 4 Tests at a Time (FIXED)")
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

    # Setup worker profiles
    worker_profiles = setup_worker_profiles(PARALLEL_WORKERS)
    if not worker_profiles:
        return

    input("\nPress Enter to start parallel batch run...")

    start_time = datetime.now()
    results = []

    try:
        # Process scenarios in batches
        for batch_idx in range(0, len(SCENARIOS_TO_RUN), PARALLEL_WORKERS):
            batch_num = (batch_idx // PARALLEL_WORKERS) + 1
            batch = SCENARIOS_TO_RUN[batch_idx:batch_idx + PARALLEL_WORKERS]

            print("\n" + "█" * 60)
            print(f"BATCH {batch_num} - Running {len(batch)} tests in parallel")
            print("█" * 60)

            # Start all processes in this batch
            processes = []
            for slot_num, scenario_type in enumerate(batch, 1):
                worker_profile = worker_profiles[slot_num - 1]
                process = run_scenario_process(scenario_type, worker_profile, batch_num, slot_num)
                processes.append({
                    "process": process,
                    "scenario_type": scenario_type,
                    "batch": batch_num,
                    "slot": slot_num,
                    "scenario_num": batch_idx + slot_num
                })

            # Wait for all processes in this batch
            for proc_info in processes:
                proc_info["process"].wait()
                exit_code = proc_info["process"].returncode

                if exit_code == 0:
                    status = "SUCCESS"
                    print(f"  ✓ [Batch {proc_info['batch']}, Slot {proc_info['slot']}] {proc_info['scenario_type']} completed")
                else:
                    status = "FAILED"
                    print(f"  ✗ [Batch {proc_info['batch']}, Slot {proc_info['slot']}] {proc_info['scenario_type']} failed")

                results.append({
                    "scenario": proc_info['scenario_num'],
                    "type": proc_info['scenario_type'],
                    "status": status,
                    "batch": proc_info['batch'],
                    "slot": proc_info['slot']
                })

            print(f"\n✓ Batch {batch_num} complete!")

            if batch_idx + PARALLEL_WORKERS < len(SCENARIOS_TO_RUN):
                print("\nWaiting 3 seconds before next batch...")
                time.sleep(3)

    finally:
        # Always cleanup worker profiles
        cleanup_worker_profiles(worker_profiles)

    # Print summary
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

    if failed > 0:
        print("\nFailed scenarios:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - Scenario {r['scenario']} ({r['type']}) - Batch {r['batch']}, Slot {r['slot']}")

    print("\n" + "=" * 60)
    print(f"Run completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)
    run_parallel_batch()
