"""
Helper script to find Chrome profile paths on your system
"""

import os
import platform
from pathlib import Path


def find_chrome_profiles():
    """Find Chrome user data directories based on OS"""
    system = platform.system()
    profiles = []

    if system == "Darwin":  # macOS
        base_paths = [
            Path.home() / "Library/Application Support/Google/Chrome",
            Path.home() / "Library/Application Support/Google/Chrome Beta",
            Path.home() / "Library/Application Support/Google/Chrome Canary",
            Path.home() / "Library/Application Support/Chromium",
        ]
    elif system == "Windows":
        base_paths = [
            Path.home() / "AppData/Local/Google/Chrome/User Data",
            Path.home() / "AppData/Local/Google/Chrome Beta/User Data",
            Path.home() / "AppData/Local/Chromium/User Data",
        ]
    else:  # Linux
        base_paths = [
            Path.home() / ".config/google-chrome",
            Path.home() / ".config/chromium",
            Path.home() / ".config/google-chrome-beta",
        ]

    for base_path in base_paths:
        if base_path.exists():
            profiles.append(str(base_path))

            # List available profiles
            print(f"\n✓ Found Chrome directory: {base_path}")
            print("  Available profiles:")

            # Check for default profile
            if (base_path / "Default").exists():
                print(f"    - Default")

            # Check for numbered profiles
            for i in range(1, 10):
                profile_dir = base_path / f"Profile {i}"
                if profile_dir.exists():
                    print(f"    - Profile {i}")

    return profiles


def get_chrome_profile_path(profile_name: str = "Default"):
    """
    Get the full path to a specific Chrome profile

    Args:
        profile_name: Profile directory name (e.g., "Default", "Profile 1")

    Returns:
        Full path to the Chrome profile directory
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        base = Path.home() / "Library/Application Support/Google/Chrome"
    elif system == "Windows":
        base = Path.home() / "AppData/Local/Google/Chrome/User Data"
    else:  # Linux
        base = Path.home() / ".config/google-chrome"

    profile_path = base / profile_name

    if profile_path.exists():
        return str(profile_path)
    else:
        return str(base)  # Return base directory if profile doesn't exist


if __name__ == "__main__":
    print("=" * 60)
    print("Chrome Profile Finder")
    print("=" * 60)

    profiles = find_chrome_profiles()

    if profiles:
        print("\n" + "=" * 60)
        print("USAGE:")
        print("=" * 60)
        print("\nTo use your Chrome profile with automation:")
        print(f"\n  python trackr_with_profile.py")
        print("\nOr specify a custom path:")
        print(f'\n  python trackr_automation.py --profile "/path/to/profile"')

        print("\n" + "=" * 60)
        print("RECOMMENDED PATH:")
        print("=" * 60)
        print(f"\n{profiles[0]}")
        print("\nCopy this path to use in trackr_with_profile.py")
    else:
        print("\n✗ No Chrome profiles found")
        print("Please ensure Chrome is installed and you have a profile set up")
