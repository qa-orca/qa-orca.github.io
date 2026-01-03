"""
Trackr Quote Flow Automation
Automated test suite for creating quotes with various options
"""

from playwright.sync_api import sync_playwright, Page
from pathlib import Path
import random
import time
from datetime import datetime
from typing import Dict, List
import json
import os
from config import START_QUOTE_URL


# Constants for pet options
DOG_BREEDS = [
    "Mixed Breed - Toy (< 10 lbs)",
    "Mixed Breed - Small (11-30 lbs)",
    "Mixed Breed - Medium (31-50 lbs)",
    "Mixed Breed - Large (51-90 lbs)",
    "Mixed Breed - Giant (> 90 lbs)"
]

CAT_BREEDS = [
    "Domestic Longhair",
    "Domestic Mediumhair",
    "Domestic Shorthair",
    "Mixed Breed"
]

PET_AGES = [
    "2 years old",
    "3 years old",
    "4 years old",
    "5 years old",
    "15 years old"
]

GENDERS = ["Male", "Female"]

BRANDS = ["USAA", "Geico"]

QUOTE_JOURNEYS = ["Bind Online Journey", "Save & Close Record"]


def generate_scenario_config(scenario_type: str) -> Dict:
    """
    Generate a random scenario configuration

    Args:
        scenario_type: 'dog_only', 'cat_only', 'multi_pet', 'one_of_each',
                      or end-to-end versions: 'e2e_dog_only', 'e2e_cat_only', etc.
                      or good/better/best versions: 'gbb_dog_15_only', etc.

    Returns:
        Dictionary with scenario configuration
    """
    # Check if this is an end-to-end scenario
    end_to_end = scenario_type.startswith("e2e_")

    # Check if this is a GBB-related scenario (accident or actual GBB)
    is_gbb_scenario = scenario_type.startswith("gbb_")

    # Check if this is a brand-specific scenario (USAA or Geico)
    is_usaa = scenario_type.startswith("usaa_")
    is_geico = scenario_type.startswith("geico_")

    # Determine base scenario and brand
    if is_usaa:
        base_scenario = scenario_type.replace("usaa_", "")
        brand = "USAA"
    elif is_geico:
        base_scenario = scenario_type.replace("geico_", "")
        brand = "Geico"
    elif end_to_end:
        base_scenario = scenario_type.replace("e2e_", "")
        brand = "Embrace"
    elif is_gbb_scenario:
        base_scenario = scenario_type.replace("gbb_", "")
        brand = "Embrace"
    else:
        base_scenario = scenario_type
        brand = "Embrace"

    config = {
        "scenario_type": scenario_type,
        "military": random.choice([True, False]),
        "brand": brand,
        "quote_journey": None,  # Will be set by caller if needed
        "end_to_end": end_to_end,
        "is_gbb": False,  # Will be set to True only for actual GBB scenarios
        "force_name": end_to_end,  # Always use name for end-to-end scenarios
        "force_phone": end_to_end,  # Always use phone for end-to-end scenarios
        "pets": []
    }

    print(f"🔍 DEBUG generate_scenario_config:")
    print(f"   scenario_type = {scenario_type}")
    print(f"   base_scenario = {base_scenario}")

    if base_scenario == "dog_only":
        gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(PET_AGES)
        })

    elif base_scenario == "cat_only":
        gender = random.choice(GENDERS)
        config["pets"].append({
            "type": "cat",
            "name": "Add Cat",
            "gender": gender,
            "breed": random.choice(CAT_BREEDS),
            "age": random.choice(PET_AGES)
        })

    elif base_scenario == "multi_pet":
        # Randomly add multiple dogs or multiple cats
        if random.choice([True, False]):
            # Multiple dogs
            for i in range(2):
                dog_gender = random.choice(GENDERS)
                is_service = random.choice([True, False])
                config["pets"].append({
                    "type": "dog",
                    "name": "Add Dog",
                    "gender": dog_gender,
                    "is_service_dog": is_service,
                    "breed": random.choice(DOG_BREEDS),
                    "age": random.choice(PET_AGES)
                })
        else:
            # Multiple cats
            for i in range(2):
                cat_gender = random.choice(GENDERS)
                config["pets"].append({
                    "type": "cat",
                    "name": "Add Cat",
                    "gender": cat_gender,
                    "breed": random.choice(CAT_BREEDS),
                    "age": random.choice(PET_AGES)
                })

    elif base_scenario == "one_of_each":
        # Add one dog and one cat
        dog_gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": dog_gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(PET_AGES)
        })

        cat_gender = random.choice(GENDERS)
        config["pets"].append({
            "type": "cat",
            "name": "Add Cat",
            "gender": cat_gender,
            "breed": random.choice(CAT_BREEDS),
            "age": random.choice(PET_AGES)
        })

    # Accident-only scenarios (3 total) - NO GBB testing
    elif base_scenario == "accident_dog_15":
        # 1. Single dog aged 15 - accident-only, no GBB
        gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": "15 years old"
        })
        config["is_gbb"] = False  # No GBB testing

    elif base_scenario == "accident_cat_15":
        # 2. Single cat aged 15 - accident-only, no GBB
        gender = random.choice(GENDERS)
        config["pets"].append({
            "type": "cat",
            "name": "Add Cat",
            "gender": gender,
            "breed": random.choice(CAT_BREEDS),
            "age": "15 years old"
        })
        config["is_gbb"] = False  # No GBB testing

    elif base_scenario == "accident_mixed_age":
        # 3. Dog under 15 + Cat aged 15 - mixed coverage
        # Dog will have GBB options, Cat will be accident-only
        dog_gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": dog_gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })

        cat_gender = random.choice(GENDERS)
        config["pets"].append({
            "type": "cat",
            "name": "Add Cat",
            "gender": cat_gender,
            "breed": random.choice(CAT_BREEDS),
            "age": "15 years old"
        })
        config["is_gbb"] = "mixed"  # Special flag for mixed scenario

    # Good/Better/Best scenarios (3 total - pets UNDER 15) - WITH GBB testing
    elif base_scenario == "dog_young":
        # 1. Single dog under 15 - full coverage with GBB
        gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })
        config["is_gbb"] = True  # Enable GBB testing

    elif base_scenario == "cat_young":
        # 2. Single cat under 15 - full coverage with GBB
        gender = random.choice(GENDERS)
        config["pets"].append({
            "type": "cat",
            "name": "Add Cat",
            "gender": gender,
            "breed": random.choice(CAT_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })
        config["is_gbb"] = True  # Enable GBB testing

    elif base_scenario == "one_of_each_young":
        # 3. Dog + Cat both under 15 - full coverage with GBB (2 accordions)
        dog_gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": dog_gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })

        cat_gender = random.choice(GENDERS)
        config["pets"].append({
            "type": "cat",
            "name": "Add Cat",
            "gender": cat_gender,
            "breed": random.choice(CAT_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })
        config["is_gbb"] = True  # Enable GBB testing

    # E2E scenarios with specific tier selection (Good/Better/Best)
    elif base_scenario == "tier_good":
        # E2E with Good tier - single dog
        gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })
        config["end_to_end"] = True
        config["force_name"] = True
        config["force_phone"] = True
        config["selected_tier"] = "Good"

    elif base_scenario == "tier_better":
        # E2E with Better tier - single dog
        gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })
        config["end_to_end"] = True
        config["force_name"] = True
        config["force_phone"] = True
        config["selected_tier"] = "Better"

    elif base_scenario == "tier_best":
        # E2E with Best tier - single dog
        gender = random.choice(GENDERS)
        is_service = random.choice([True, False])
        config["pets"].append({
            "type": "dog",
            "name": "Add Dog",
            "gender": gender,
            "is_service_dog": is_service,
            "breed": random.choice(DOG_BREEDS),
            "age": random.choice(["2 years old", "3 years old", "4 years old", "5 years old"])
        })
        config["end_to_end"] = True
        config["force_name"] = True
        config["force_phone"] = True
        config["selected_tier"] = "Best"

    print(f"   Returning config with {len(config['pets'])} pets, is_gbb={config['is_gbb']}")
    return config


class TrackrQuoteFlow:
    """Handles the complete quote creation flow with randomization"""

    def __init__(self, page: Page, output_folder: str = None):
        self.page = page
        self.quote_id = None
        self.network_responses = []
        self.output_folder = output_folder
        self.json_folder = None
        self.screenshot_folder = None

        # Create output folders if specified
        if output_folder:
            self.json_folder = os.path.join(output_folder, "json")
            self.screenshot_folder = os.path.join(output_folder, "screenshots")
            os.makedirs(self.json_folder, exist_ok=True)
            os.makedirs(self.screenshot_folder, exist_ok=True)

        # Set up network listener to capture activatepolicyquote response
        self.page.on("response", self._handle_response)

    def _get_screenshot_path(self, filename):
        """Get screenshot path - use output folder if specified, otherwise screenshots/"""
        if self.screenshot_folder:
            return os.path.join(self.screenshot_folder, filename)
        return f"screenshots/{filename}"

    def _save_scenario_data(self, scenario_name, quote_id, email, zip_code):
        """Save scenario data to JSON file"""
        if not self.json_folder:
            return

        data = {
            "scenario": scenario_name,
            "quoteID": quote_id,
            "email": email,
            "zip": zip_code,
            "timestamp": datetime.now().isoformat()
        }

        json_file = os.path.join(self.json_folder, f"{scenario_name}.json")
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"   JSON data saved: {json_file}")

    def _handle_response(self, response):
        """Handle network responses and capture quoteID from activatepolicyquote"""
        try:
            if "activatepolicyquote" in response.url.lower():
                # Get the JSON response
                if response.status == 200:
                    json_data = response.json()

                    # Extract the nested quote.id (the actual quote ID we want)
                    if "quote" in json_data and isinstance(json_data["quote"], dict):
                        if "id" in json_data["quote"]:
                            self.quote_id = json_data["quote"]["id"]
                    # Fallback to other possible locations
                    elif "quoteId" in json_data:
                        self.quote_id = json_data["quoteId"]
                    elif "quoteID" in json_data:
                        self.quote_id = json_data["quoteID"]
                    elif "id" in json_data:
                        self.quote_id = json_data["id"]

                    # Only print if we found it
                    if self.quote_id:
                        print(f"\n🎯 Quote ID: {self.quote_id}")
        except Exception as e:
            # Silently fail - we'll show warning in summary if no quote ID
            pass

    def navigate_to_start_quote(self):
        """Navigate to start quote page - URL already goes there, just verify"""
        print("\n📍 Verifying we're on Start Quote page...")

        # Check if we need to click the tab or if we're already there
        current_url = self.page.url
        if "/quoting/start-quote" not in current_url:
            print("   Not on start-quote page, navigating...")
            # Try clicking the tab if it exists
            if self.page.locator('a:has-text("Start Quote")').count() > 0:
                self.page.click('a:has-text("Start Quote")')
                self.page.wait_for_load_state("networkidle")
            else:
                # Navigate directly via URL
                self.page.goto(self.page.url.split('/quoting')[0] + '/quoting/start-quote')
                self.page.wait_for_load_state("networkidle")

        print("✓ On Start Quote page")
        time.sleep(1)  # Give page time to fully render

    def select_brand_button(self, brand: str):
        """Click the brand button (Embrace, USAA, Geico) on the quote lookup page"""
        print(f"\n🏢 Selecting brand button: {brand}...")

        # Click the brand button
        self.page.click(f'button:has-text("{brand}")')
        time.sleep(1)  # Wait for page to update
        print(f"✓ {brand} brand button clicked")

    def select_call_source(self, brand: str = "Embrace"):
        """Select call source based on brand - for USAA/Geico, select brand-specific option"""
        print("\n📞 Selecting call source...")

        # For USAA or Geico, select the brand with California
        if brand == "USAA":
            selected_source = "USAA, California"
        elif brand == "Geico":
            selected_source = "Geico, California"
        else:
            # For Embrace, select from available Embrace sources
            call_sources = [
                "Embrace - Affiliates",
                "Embrace Atwave Email",
                "Embrace - Better Impression"
            ]
            selected_source = random.choice(call_sources)

        print(f"   Selected: {selected_source}")

        # Wait for the input to be visible
        self.page.wait_for_selector('input[formcontrolname="callSource"]', state="visible", timeout=10000)

        # Click the call source input to open dropdown
        self.page.click('input[formcontrolname="callSource"]')
        time.sleep(1)  # Wait for dropdown to open

        # Click the selected option from the dropdown
        self.page.click(f'span.mat-option-text:has-text("{selected_source}")')
        print(f"✓ Call source set to: {selected_source}")

        return selected_source

    def fill_pet_parent_info(self, force_name: bool = False):
        """Fill pet parent information with random decision to use real name or leave blank"""
        print("\n👤 Filling pet parent information...")

        # Randomly decide whether to fill name (50% chance), or force it if required
        use_real_name = True if force_name else random.choice([True, False])

        if use_real_name:
            first_name = "Mark"
            last_name = "Testingtrackr"
            print(f"   Using name: {first_name} {last_name}")

            self.page.fill('input[name="firstName"]', first_name)
            self.page.fill('input[name="lastName"]', last_name)
        else:
            print("   Leaving name blank (will be 'Pet Parent')")
            # Leave blank - will default to "Pet Parent"
            pass

        return use_real_name

    def fill_phone_number(self, force_phone: bool = False):
        """Randomly decide whether to fill phone number"""
        print("\n📱 Filling phone number...")

        # Randomly decide whether to fill phone (50% chance), or force it if required
        use_phone = True if force_phone else random.choice([True, False])

        if use_phone:
            phone = "5036640756"
            print(f"   Using phone: {phone}")
            self.page.fill('input[formcontrolname="phoneNumber"]', phone)
        else:
            print("   Leaving phone blank")

        return use_phone

    def fill_email(self):
        """Generate and fill email with timestamp"""
        print("\n📧 Generating email with timestamp...")

        # Create timestamp to millisecond
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # Remove last 3 digits to get milliseconds
        email = f"testingtrackr{timestamp}@yopmail.com"

        print(f"   Email: {email}")
        self.page.fill('input[formcontrolname="email"]', email)
        print(f"✓ Email set to: {email}")

        return email

    def fill_zip_code(self):
        """Select a random zip code from available options"""
        print("\n📍 Filling zip code...")

        zip_codes = ["98642", "60302"]
        selected_zip = random.choice(zip_codes)

        print(f"   Selected zip: {selected_zip}")
        self.page.fill('input[formcontrolname="ratingZipCode"]', selected_zip)
        print(f"✓ Zip code set to: {selected_zip}")

        return selected_zip

    def click_first_next(self):
        """Click the first Next button after filling initial form"""
        print("\n⏭️  Clicking Next button...")

        # Click Next button
        self.page.click('button:has-text("Next")')
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked Next")
        time.sleep(1)

    def answer_military_question(self):
        """Randomly answer the military question"""
        print("\n🎖️  Answering military question...")

        # Randomly select Yes or No
        answer = random.choice(["Yes", "No"])
        print(f"   Selected: {answer}")

        # Click the selected option
        self.page.click(f'span.mat-button-toggle-label-content:has-text("{answer}")')
        print(f"✓ Military question answered: {answer}")
        time.sleep(0.5)

        return answer

    def click_second_next(self):
        """Click the second Next button (with arrow icon)"""
        print("\n⏭️  Clicking Next button (with arrow)...")

        # Click Next button with the arrow icon
        self.page.click('button:has(mat-icon:has-text("east"))')
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked Next")
        time.sleep(1)

    def add_dog_pet(self, pet_name: str, gender: str, is_service_dog: bool, breed: str, age: str):
        """Add a dog to the quote"""
        print(f"\n🐕 Adding dog: {pet_name}...")

        # Wait for the form to be visible
        time.sleep(2)

        # Fill pet name - get the last visible pet name input (for multi-pet scenarios)
        pet_name_inputs = self.page.locator('input[formcontrolname="name"]').all()
        print(f"   Found {len(pet_name_inputs)} pet name inputs")
        last_input = pet_name_inputs[-1]
        last_input.scroll_into_view_if_needed()
        last_input.click()  # Focus the input first
        time.sleep(0.3)
        last_input.fill(pet_name)
        print(f"   Name: {pet_name}")
        time.sleep(0.5)

        # Select gender - click the last set of gender buttons
        gender_buttons = self.page.locator(f'span.mat-button-toggle-label-content:has-text("{gender}")').all()
        print(f"   Found {len(gender_buttons)} {gender} buttons")
        last_gender_btn = gender_buttons[-1]
        last_gender_btn.scroll_into_view_if_needed()
        last_gender_btn.click()
        print(f"   Gender: {gender}")
        time.sleep(0.5)

        # Select Dog - click the last Dog button
        dog_buttons = self.page.locator('span.mat-button-toggle-label-content:has-text("Dog")').all()
        print(f"   Found {len(dog_buttons)} Dog buttons")
        last_dog_btn = dog_buttons[-1]
        last_dog_btn.scroll_into_view_if_needed()
        last_dog_btn.click()
        print(f"   Type: Dog")
        time.sleep(1)  # Wait for service dog question to appear

        # Answer service dog question - click the last Yes/No button
        service_answer = "Yes" if is_service_dog else "No"
        service_buttons = self.page.locator(f'span.mat-button-toggle-label-content:has-text("{service_answer}")').all()
        print(f"   Found {len(service_buttons)} {service_answer} buttons")
        last_service_btn = service_buttons[-1]
        last_service_btn.scroll_into_view_if_needed()
        last_service_btn.click()
        print(f"   Service Dog: {service_answer}")
        time.sleep(0.5)

        # Select breed - click the last breed input
        breed_inputs = self.page.locator('input[formcontrolname="breed"]').all()
        print(f"   Found {len(breed_inputs)} breed inputs")
        last_breed_input = breed_inputs[-1]
        last_breed_input.scroll_into_view_if_needed()
        last_breed_input.click()
        time.sleep(0.5)
        self.page.click(f'span.mat-option-text:has-text("{breed}")')
        print(f"   Breed: {breed}")
        time.sleep(0.5)

        # Select age - click the last age select
        age_selects = self.page.locator('mat-select[formcontrolname="ageInYears"]').all()
        print(f"   Found {len(age_selects)} age selects")
        last_age_select = age_selects[-1]
        last_age_select.scroll_into_view_if_needed()
        last_age_select.click()
        time.sleep(0.5)
        self.page.click(f'span.mat-option-text:has-text("{age}")')
        print(f"   Age: {age}")

        print(f"✓ Dog added: {pet_name}")

    def add_cat_pet(self, pet_name: str, gender: str, breed: str, age: str):
        """Add a cat to the quote"""
        print(f"\n🐱 Adding cat: {pet_name}...")

        # Wait for the form to be visible
        time.sleep(2)

        # Fill pet name - get the last visible pet name input (for multi-pet scenarios)
        pet_name_inputs = self.page.locator('input[formcontrolname="name"]').all()
        print(f"   Found {len(pet_name_inputs)} pet name inputs")
        last_input = pet_name_inputs[-1]
        last_input.scroll_into_view_if_needed()
        last_input.click()  # Focus the input first
        time.sleep(0.3)
        last_input.fill(pet_name)
        print(f"   Name: {pet_name}")
        time.sleep(0.5)

        # Select gender - click the last set of gender buttons
        gender_buttons = self.page.locator(f'span.mat-button-toggle-label-content:has-text("{gender}")').all()
        print(f"   Found {len(gender_buttons)} {gender} buttons")
        last_gender_btn = gender_buttons[-1]
        last_gender_btn.scroll_into_view_if_needed()
        last_gender_btn.click()
        print(f"   Gender: {gender}")
        time.sleep(0.5)

        # Select Cat - click the last Cat button
        cat_buttons = self.page.locator('span.mat-button-toggle-label-content:has-text("Cat")').all()
        print(f"   Found {len(cat_buttons)} Cat buttons")
        last_cat_btn = cat_buttons[-1]
        last_cat_btn.scroll_into_view_if_needed()
        last_cat_btn.click()
        print(f"   Type: Cat")
        time.sleep(0.5)

        # Select breed - click the last breed input
        breed_inputs = self.page.locator('input[formcontrolname="breed"]').all()
        print(f"   Found {len(breed_inputs)} breed inputs")
        last_breed_input = breed_inputs[-1]
        last_breed_input.scroll_into_view_if_needed()
        last_breed_input.click()
        time.sleep(0.5)
        self.page.click(f'span.mat-option-text:has-text("{breed}")')
        print(f"   Breed: {breed}")
        time.sleep(0.5)

        # Select age - click the last age select
        age_selects = self.page.locator('mat-select[formcontrolname="ageInYears"]').all()
        print(f"   Found {len(age_selects)} age selects")
        last_age_select = age_selects[-1]
        last_age_select.scroll_into_view_if_needed()
        last_age_select.click()
        time.sleep(0.5)
        self.page.click(f'span.mat-option-text:has-text("{age}")')
        print(f"   Age: {age}")

        print(f"✓ Cat added: {pet_name}")

    def click_add_another_pet(self):
        """Click the Add Another Pet button"""
        print("\n➕ Clicking Add Another Pet...")
        self.page.click('span:has-text("Add Another Pet")')
        time.sleep(1)
        print("✓ Ready to add another pet")

    def click_next_with_arrow(self):
        """Click Next button with arrow icon"""
        print("\n⏭️  Clicking Next...")
        self.page.click('button:has(mat-icon:has-text("east"))')
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked Next")
        time.sleep(1)

    def select_quote_journey(self, journey: str):
        """Select quote journey (Bind Online Journey or Save & Close Record)"""
        print(f"\n📋 Selecting quote journey: {journey}...")

        try:
            # Wait for the element to be available with timeout
            self.page.wait_for_selector(f'span:has-text("{journey}")', timeout=10000, state="visible")

            # Click the journey option
            self.page.click(f'span:has-text("{journey}")')
            print(f"✓ Quote journey selected: {journey}")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️  Could not find quote journey option: {journey}")
            print(f"   Error: {e}")
            print(f"   Current URL: {self.page.url}")
            print(f"   This might be expected depending on the page state")
            # Take screenshot for debugging
            error_path = self._get_screenshot_path("quote_journey_error.png")
            self.page.screenshot(path=error_path, full_page=True)
            print(f"   Screenshot saved: {error_path}")

    def click_next_from_quote_page(self):
        """Click Next button on the quote page to go to contact info"""
        print("\n⏭️  Clicking Next from quote page...")
        self.page.click('button:has(mat-icon:has-text("east"))')
        self.page.wait_for_load_state("networkidle")
        print("✓ Navigated to contact info page")
        time.sleep(1)

    def fill_contact_info_address(self, zip_code: str):
        """Fill in the mailing address on contact info page based on zip code"""
        print("\n🏠 Filling mailing address...")

        # Map zip codes to addresses
        address_map = {
            "98642": "723 nw 175th way, ridgefield, wa, 98642",
            "60302": "1012 Chicago Ave, Oak Park, IL, 60302"
        }

        address = address_map.get(zip_code)
        if not address:
            print(f"⚠️  No address mapping for zip code: {zip_code}")
            return

        print(f"   Using address: {address}")

        # Wait for the address input field
        self.page.wait_for_selector('input[formcontrolname="addressLine1"]', state="visible", timeout=10000)

        # Type the address into the field
        self.page.fill('input[formcontrolname="addressLine1"]', address)
        time.sleep(1.5)  # Wait for Google autocomplete to appear

        # Click the first Google autocomplete suggestion
        print("   Selecting from Google autocomplete...")
        try:
            # Wait for the autocomplete dropdown to appear
            self.page.wait_for_selector('.pac-item', state="visible", timeout=5000)

            # Click the first suggestion
            self.page.click('.pac-item:first-child')
            print("✓ Address selected from Google autocomplete")
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️  Could not select from autocomplete: {e}")
            print("   Address may have been entered manually")

    def click_next_from_contact_info(self):
        """Click Next button on the contact info page"""
        print("\n⏭️  Clicking Next from contact info page...")
        self.page.click('button:has(mat-icon:has-text("east"))')
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked Next")
        time.sleep(1)

    def check_acknowledgements(self):
        """Check the acknowledgements checkbox on /quoting/acknowledgements"""
        print("\n✅ Checking acknowledgements...")

        # Wait for the checkbox to be visible
        self.page.wait_for_selector('mat-checkbox[formcontrolname="confirmAll"]', state="visible", timeout=10000)

        # Try multiple selectors to ensure the checkbox gets clicked
        checkbox_selectors = [
            'mat-checkbox[formcontrolname="confirmAll"]',
            'div.o-checkbox-wrapper mat-checkbox[formcontrolname="confirmAll"]',
            'label[for^="mat-checkbox-"][for$="-input"]',
            'input[id^="mat-checkbox-"][id$="-input"]'
        ]

        clicked = False
        for selector in checkbox_selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    print(f"   Trying selector: {selector}")
                    self.page.click(selector, force=True)
                    clicked = True
                    print(f"   ✓ Clicked using: {selector}")
                    break
            except Exception as e:
                print(f"   ⚠️  Failed with {selector}: {e}")
                continue

        if not clicked:
            print("   ⚠️  Warning: Could not click acknowledgements checkbox")
            error_path = self._get_screenshot_path("acknowledgements_error.png")
            self.page.screenshot(path=error_path, full_page=True)
            print(f"   Screenshot saved: {error_path}")

        # Verify checkbox is checked
        time.sleep(0.5)
        checkbox = self.page.locator('mat-checkbox[formcontrolname="confirmAll"]')
        is_checked = "mat-checkbox-checked" in checkbox.get_attribute("class")

        if is_checked:
            print("✓ Acknowledgements checkbox confirmed as checked")
        else:
            print("⚠️  Warning: Checkbox may not be checked, attempting one more time...")
            self.page.click('mat-checkbox[formcontrolname="confirmAll"]', force=True)
            time.sleep(0.5)

    def click_next_from_acknowledgements(self):
        """Click Next button on the acknowledgements page"""
        print("\n⏭️  Clicking Next from acknowledgements page...")
        self.page.click('button:has(mat-icon:has-text("east"))')
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked Next")
        time.sleep(1)

    def fill_billing_info(self, zip_code: str):
        """Fill in billing information on /quoting/billing page"""
        print("\n💳 Filling billing information...")

        # Wait for Stripe iframes to load
        print("   Waiting for Stripe payment form...")
        time.sleep(3)

        # Stripe uses separate iframes for each field
        # Find and fill each field in its respective iframe
        def fill_stripe_iframe_field(field_id, value, field_name):
            """Fill a Stripe field that's inside an iframe"""
            print(f"   Filling {field_name}...")

            # Try direct page selectors first
            try:
                direct_field = self.page.locator(f'input#{field_id}')
                if direct_field.count() > 0:
                    direct_field.click()
                    time.sleep(0.2)
                    direct_field.fill(value)
                    print(f"   ✓ {field_name} entered")
                    time.sleep(0.3)
                    return True
            except:
                pass

            # Try each iframe
            for frame in self.page.frames:
                try:
                    # Check if this frame contains the field
                    field = frame.locator(f'input#{field_id}')
                    if field.count() > 0:
                        # Click and type into the field
                        field.click()
                        time.sleep(0.2)
                        field.fill(value)
                        print(f"   ✓ {field_name} entered")
                        time.sleep(0.3)
                        return True
                except:
                    continue

            print(f"   ✗ Could not find {field_name} field")
            return False

        # Fill each Stripe field using their IDs from the HTML
        card_filled = fill_stripe_iframe_field('Field-numberInput', '4242424242424242', 'Card number')
        expiry_filled = fill_stripe_iframe_field('Field-expiryInput', '1169', 'Expiration')
        cvc_filled = fill_stripe_iframe_field('Field-cvcInput', '369', 'CVC')
        zip_filled = fill_stripe_iframe_field('Field-postalCodeInput', zip_code, 'ZIP code')

        # Report results
        if card_filled and expiry_filled and cvc_filled and zip_filled:
            print("✓ All billing information entered successfully")
        else:
            print("⚠️  Warning: Some billing fields may not have been filled")
            error_path = self._get_screenshot_path("billing_error.png")
            self.page.screenshot(path=error_path, full_page=True)
            print(f"   Screenshot saved: {error_path}")

        time.sleep(1)

    def click_purchase_policy(self):
        """Click Purchase Policy button"""
        print("\n🛒 Clicking Purchase Policy...")
        self.page.click('button:has-text("Purchase Policy")')

        # Wait for navigation to success page instead of networkidle
        # (success page may have ongoing activity that prevents networkidle)
        print("   Waiting for success page...")
        self.page.wait_for_url("**/quoting/success", timeout=15000)
        print("✓ Purchase completed - reached success page")
        time.sleep(2)

    def select_coverage_tier(self, tier: str):
        """
        Open accordion and select a specific coverage tier (Good/Better/Best)

        Args:
            tier: 'Good', 'Better', or 'Best'
        """
        print(f"\n💎 Selecting {tier} coverage tier...")

        # First expand the accordion
        print("   Expanding coverage accordion...")
        accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
        if len(accordion_icons) > 0:
            accordion_icons[0].scroll_into_view_if_needed()
            time.sleep(0.5)
            accordion_icons[0].click()
            time.sleep(1.5)
            print("   ✓ Accordion expanded")
        else:
            print("   ⚠️ No accordion found - may already be expanded")

        # Select the tier (Better is default, so only click if Good or Best)
        if tier == "Better":
            print(f"   ✓ {tier} tier is default - no click needed")
        else:
            print(f"   Clicking {tier} tier...")
            try:
                tier_button = self.page.locator(f'span:has-text("{tier}")').first
                tier_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                tier_button.click(force=True)
                time.sleep(1.5)
                print(f"   ✓ {tier} tier selected")
            except Exception as e:
                print(f"   ⚠️ Could not click {tier}: {e}")

        # Take screenshot of selected tier
        screenshot_path = self._get_screenshot_path(f"tier_{tier.lower()}_selected.png")
        self.page.screenshot(path=screenshot_path, full_page=True)
        print(f"   ✓ Screenshot saved: tier_{tier.lower()}_selected.png")

    def click_all_coverage_accordions(self):
        """Click all coverage accordions to expand options (for multi-pet scenarios)"""
        print("\n📋 Expanding all coverage accordions...")

        try:
            # Find all unfold_more icons (one per pet)
            accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
            num_accordions = len(accordion_icons)

            print(f"   Found {num_accordions} accordion(s)")

            # Click each accordion
            for idx, icon in enumerate(accordion_icons, 1):
                icon.click()
                time.sleep(0.5)
                print(f"   ✓ Accordion {idx} expanded")

            time.sleep(1)
            print(f"✓ All {num_accordions} accordion(s) expanded")
        except Exception as e:
            print(f"⚠️  Could not click accordions: {e}")
            error_path = self._get_screenshot_path("accordion_error.png")
            self.page.screenshot(path=error_path, full_page=True)
            print(f"   Screenshot saved: {error_path}")

    def test_good_better_best_options(self, scenario_name: str, num_pets: int = 1):
        """Test Good/Better/Best coverage options with screenshots
        Handles both single pet and multi-pet scenarios

        Args:
            scenario_name: Name of the scenario for screenshot naming
            num_pets: Number of pets (1 for single pet, 2 for multi-pet)
        """
        print(f"\n💎 Testing Good/Better/Best coverage options ({num_pets} pet(s))...")

        if num_pets == 1:
            # Single pet - expand accordion and test GBB
            print("\n📋 Expanding accordion...")
            accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
            if len(accordion_icons) > 0:
                # Scroll accordion into view before clicking
                accordion_icons[0].scroll_into_view_if_needed()
                time.sleep(0.5)
                accordion_icons[0].click()
                time.sleep(1.5)
                print("   ✓ Accordion expanded")

            # Screenshot 1: Better (default)
            print("\n   1. Verifying Better (default) coverage...")
            time.sleep(1)
            screenshot_path = self._get_screenshot_path(f"{scenario_name}_better_default.png")
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"   ✓ Screenshot saved: {scenario_name}_better_default.png")

            # Screenshot 2: Good
            print("\n   2. Switching to Good coverage...")
            try:
                good_button = self.page.locator('span:has-text("Good")').first
                good_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                good_button.click(force=True)
                time.sleep(1.5)
                screenshot_path = self._get_screenshot_path(f"{scenario_name}_good.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_name}_good.png")
            except Exception as e:
                print(f"   ⚠️  Could not click Good: {e}")

            # Screenshot 3: Best
            print("\n   3. Switching to Best coverage...")
            try:
                best_button = self.page.locator('span:has-text("Best")').first
                best_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                best_button.click(force=True)
                time.sleep(1.5)
                screenshot_path = self._get_screenshot_path(f"{scenario_name}_best.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_name}_best.png")
            except Exception as e:
                print(f"   ⚠️  Could not click Best: {e}")

        elif num_pets == 2:
            # Multi-pet - test each pet separately (accordions toggle)
            print("\n📋 Testing Pet 1...")
            accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
            if len(accordion_icons) > 0:
                accordion_icons[0].scroll_into_view_if_needed()
                time.sleep(0.5)
                accordion_icons[0].click()  # Open first accordion
                time.sleep(1.5)
                print("   ✓ Pet 1 accordion expanded")

            # Pet 1 - Screenshot 1: Better (default)
            print("\n   Pet 1 - Screenshot 1: Better (default)...")
            time.sleep(1)
            screenshot_path = self._get_screenshot_path(f"{scenario_name}_pet1_better.png")
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"   ✓ Screenshot saved: {scenario_name}_pet1_better.png")

            # Pet 1 - Screenshot 2: Good
            print("\n   Pet 1 - Screenshot 2: Switching to Good...")
            try:
                good_button = self.page.locator('span:has-text("Good")').first
                good_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                good_button.click(force=True)
                time.sleep(1.5)
                screenshot_path = self._get_screenshot_path(f"{scenario_name}_pet1_good.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_name}_pet1_good.png")
            except Exception as e:
                print(f"   ⚠️  Could not click Good: {e}")

            # Pet 1 - Screenshot 3: Best
            print("\n   Pet 1 - Screenshot 3: Switching to Best...")
            try:
                best_button = self.page.locator('span:has-text("Best")').first
                best_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                best_button.click(force=True)
                time.sleep(1.5)
                screenshot_path = self._get_screenshot_path(f"{scenario_name}_pet1_best.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_name}_pet1_best.png")
            except Exception as e:
                print(f"   ⚠️  Could not click Best: {e}")

            # Now test Pet 2
            print("\n📋 Testing Pet 2...")
            print("   (Opening Pet 2 accordion will close Pet 1)")
            accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
            if len(accordion_icons) >= 1:
                accordion_icons[-1].scroll_into_view_if_needed()
                time.sleep(0.5)
                accordion_icons[-1].click()  # Click last accordion (Pet 2)
                time.sleep(1.5)
                print("   ✓ Pet 2 accordion expanded (Pet 1 closed)")

            # Pet 2 - Screenshot 4: Better (default)
            print("\n   Pet 2 - Screenshot 4: Better (default)...")
            time.sleep(1)
            screenshot_path = self._get_screenshot_path(f"{scenario_name}_pet2_better.png")
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"   ✓ Screenshot saved: {scenario_name}_pet2_better.png")

            # Pet 2 - Screenshot 5: Good
            print("\n   Pet 2 - Screenshot 5: Switching to Good...")
            try:
                # Use :visible to ensure we only get visible buttons
                good_button = self.page.locator('span:has-text("Good"):visible').last
                good_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                good_button.click(force=True)
                time.sleep(1.5)
                screenshot_path = self._get_screenshot_path(f"{scenario_name}_pet2_good.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_name}_pet2_good.png")
            except Exception as e:
                print(f"   ⚠️  Could not click Good: {e}")

            # Pet 2 - Screenshot 6: Best
            print("\n   Pet 2 - Screenshot 6: Switching to Best...")
            try:
                # Use :visible to ensure we only get visible buttons
                best_button = self.page.locator('span:has-text("Best"):visible').last
                best_button.scroll_into_view_if_needed()
                time.sleep(0.5)
                best_button.click(force=True)
                time.sleep(1.5)
                screenshot_path = self._get_screenshot_path(f"{scenario_name}_pet2_best.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_name}_pet2_best.png")
            except Exception as e:
                print(f"   ⚠️  Could not click Best: {e}")

        print("\n✓ Good/Better/Best testing complete")

    def complete_quote_flow(self, scenario_config: Dict):
        """Complete the entire quote flow with given scenario configuration"""
        print("\n" + "=" * 60)
        print(f"SCENARIO: {scenario_config['scenario_type'].upper().replace('_', ' ')}")
        print("=" * 60)

        # Verify we're on the right page
        self.navigate_to_start_quote()

        # Select brand button first (Embrace, USAA, or Geico)
        self.select_brand_button(scenario_config["brand"])

        # Fill out the initial form with randomization
        # Call source selection includes state for USAA/Geico (e.g., "USAA, California")
        call_source = self.select_call_source(scenario_config["brand"])
        used_name = self.fill_pet_parent_info(force_name=scenario_config.get("force_name", False))
        used_phone = self.fill_phone_number(force_phone=scenario_config.get("force_phone", False))
        email = self.fill_email()
        zip_code = self.fill_zip_code()

        # Click Next to proceed
        self.click_first_next()

        # Answer military question based on scenario
        military_answer = "Yes" if scenario_config["military"] else "No"
        print(f"\n🎖️  Answering military question: {military_answer}")
        self.page.click(f'span.mat-button-toggle-label-content:has-text("{military_answer}")')
        time.sleep(0.5)

        # Click Next to continue
        self.click_second_next()

        # Answer "do you own more than one pet" question
        # Randomly answer Yes or No (doesn't affect actual pet count)
        multi_pet_answer = random.choice(["Yes", "No"])
        print(f"\n🐾 Answering 'Do you own more than one pet': {multi_pet_answer}")
        self.page.click(f'span.mat-button-toggle-label-content:has-text("{multi_pet_answer}")')
        time.sleep(0.5)
        print(f"✓ Selected: {multi_pet_answer}")

        # Add pets based on scenario
        print(f"\n🐾 DEBUG: scenario_config['pets'] = {scenario_config['pets']}")
        print(f"   Number of pets to add: {len(scenario_config['pets'])}")

        for idx, pet_config in enumerate(scenario_config["pets"]):
            if pet_config["type"] == "dog":
                self.add_dog_pet(
                    pet_name=pet_config["name"],
                    gender=pet_config["gender"],
                    is_service_dog=pet_config["is_service_dog"],
                    breed=pet_config["breed"],
                    age=pet_config["age"]
                )
            elif pet_config["type"] == "cat":
                self.add_cat_pet(
                    pet_name=pet_config["name"],
                    gender=pet_config["gender"],
                    breed=pet_config["breed"],
                    age=pet_config["age"]
                )

            # If not the last pet, click Add Another Pet
            if idx < len(scenario_config["pets"]) - 1:
                self.click_add_another_pet()

        # Click Next to finish pet details
        self.click_next_with_arrow()

        # Wait for quote page to load
        print("\n⏳ Waiting for quote page to load...")
        time.sleep(3)
        print(f"   Current URL: {self.page.url}")

        # If end-to-end scenario, skip quote journey and continue to contact info
        if scenario_config.get("end_to_end", False):
            print("\n🔄 Continuing with end-to-end flow...")

            # If a specific tier is selected, open accordion and select it
            selected_tier = scenario_config.get("selected_tier")
            if selected_tier:
                self.select_coverage_tier(selected_tier)

            # Click Next from quote page to go to contact info
            self.click_next_from_quote_page()
            print(f"   Current URL: {self.page.url}")

            # Fill in the mailing address based on zip code
            self.fill_contact_info_address(zip_code)

            # Click Next from contact info page
            self.click_next_from_contact_info()
            print(f"   Current URL: {self.page.url}")

            # Check acknowledgements
            self.check_acknowledgements()

            # Click Next from acknowledgements
            self.click_next_from_acknowledgements()
            print(f"   Current URL: {self.page.url}")

            # Fill billing information
            self.fill_billing_info(zip_code)

            # Click Purchase Policy
            self.click_purchase_policy()

            # Take final screenshot
            print(f"   Current URL: {self.page.url}")
            final_screenshot = self._get_screenshot_path(f"{scenario_config['scenario_type']}_final.png")
            self.page.screenshot(path=final_screenshot, full_page=True)
            print(f"   Screenshot saved: {final_screenshot}")

            # Save JSON data
            self._save_scenario_data(
                scenario_config['scenario_type'],
                self.quote_id,
                email,
                zip_code
            )

            print("\n✅ End-to-end flow completed!")
        else:
            # For non-e2e scenarios
            # Only select quote journey if one is specified (Bind Online or Save & Close)
            # Most scenarios stop at the quote page
            if scenario_config.get("quote_journey"):
                self.select_quote_journey(scenario_config["quote_journey"])

            # Handle different screenshot scenarios
            is_gbb_value = scenario_config.get("is_gbb", False)
            print(f"\n🔍 DEBUG: is_gbb_value = {is_gbb_value} (type: {type(is_gbb_value)})")
            print(f"   scenario_type = {scenario_config['scenario_type']}")

            if is_gbb_value == True:
                # GBB scenarios - test Good/Better/Best with screenshots
                # Determine number of pets to test
                num_pets = len(scenario_config['pets'])
                print(f"   Testing {num_pets} pet(s) for GBB options")
                self.test_good_better_best_options(scenario_config['scenario_type'], num_pets)
                print("\n✅ Good/Better/Best quote flow completed!")

            elif is_gbb_value == "mixed":
                # Mixed scenario (AO test 3) - Dog young + Cat 15
                # Pet 1 (top) = Dog young with GBB
                # Pet 2 (bottom) = Cat 15 with accident-only

                # Step 1: Expand first accordion (dog) and test GBB
                print("\n📋 Expanding first accordion (dog - young)...")
                accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
                if len(accordion_icons) > 0:
                    accordion_icons[0].click()  # Click only first accordion
                    time.sleep(1)
                    print("   ✓ First accordion expanded")

                # Screenshot 1: Dog with Better (default)
                print("\n📸 Taking screenshot 1: Dog Better (default)...")
                screenshot_path = self._get_screenshot_path(f"{scenario_config['scenario_type']}_dog_better.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_config['scenario_type']}_dog_better.png")

                # Screenshot 2: Switch dog to Good
                print("\n   Switching dog to Good coverage...")
                good_buttons = self.page.locator('span:has-text("Good")').all()
                if len(good_buttons) > 0:
                    good_buttons[0].click(force=True)  # Force click to bypass overlays
                    time.sleep(1)
                    screenshot_path = self._get_screenshot_path(f"{scenario_config['scenario_type']}_dog_good.png")
                    self.page.screenshot(path=screenshot_path, full_page=True)
                    print(f"   ✓ Screenshot saved: {scenario_config['scenario_type']}_dog_good.png")

                # Screenshot 3: Switch dog to Best
                print("\n   Switching dog to Best coverage...")
                best_buttons = self.page.locator('span:has-text("Best")').all()
                if len(best_buttons) > 0:
                    best_buttons[0].click(force=True)  # Force click to bypass overlays
                    time.sleep(1)
                    screenshot_path = self._get_screenshot_path(f"{scenario_config['scenario_type']}_dog_best.png")
                    self.page.screenshot(path=screenshot_path, full_page=True)
                    print(f"   ✓ Screenshot saved: {scenario_config['scenario_type']}_dog_best.png")

                # Step 2: Expand second accordion (cat - accident-only)
                # This will close the dog accordion
                print("\n📋 Expanding second accordion (cat - aged 15, accident-only)...")
                print("   (This will close dog accordion)")
                accordion_icons = self.page.locator('mat-icon:has-text("unfold_more")').all()
                if len(accordion_icons) >= 1:
                    # After clicking dog's GBB buttons, need to find accordions again
                    # The cat accordion should now be visible
                    accordion_icons[-1].click()  # Click last accordion (cat)
                    time.sleep(1)
                    print("   ✓ Cat accordion expanded (dog accordion closed)")

                # Screenshot 4: Cat accident-only coverage
                print("\n📸 Taking screenshot 4: Cat accident-only...")
                screenshot_path = self._get_screenshot_path(f"{scenario_config['scenario_type']}_cat_accident_only.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_config['scenario_type']}_cat_accident_only.png")

                print("\n✅ Mixed coverage quote flow completed!")
                print("   (4 screenshots total: dog Better/Good/Best + cat accident-only)")

            else:
                # Accident-only scenarios - expand accordion and take 1 screenshot
                print(f"\n📸 Accident-only coverage - expanding accordion...")
                self.click_all_coverage_accordions()

                print(f"\n📸 Taking screenshot...")
                print(f"   Current URL: {self.page.url}")
                final_screenshot = self._get_screenshot_path(f"{scenario_config['scenario_type']}_final.png")
                self.page.screenshot(path=final_screenshot, full_page=True)
                print(f"   ✓ Screenshot saved: {scenario_config['scenario_type']}_final.png")
                print("\n✅ Accident-only quote flow completed!")

            # Save JSON data for all non-e2e scenarios
            self._save_scenario_data(
                scenario_config['scenario_type'],
                self.quote_id,
                email,
                zip_code
            )

        # Print summary
        print("\n" + "=" * 60)
        print("QUOTE FLOW SUMMARY")
        print("=" * 60)
        print(f"Scenario Type: {scenario_config['scenario_type'].replace('_', ' ').title()}")
        print(f"Brand: {scenario_config['brand']}")
        print(f"Call Source: {call_source}")
        print(f"Pet Parent: {'Mark Testingtrackr' if used_name else 'Pet Parent (blank)'}")
        print(f"Phone: {'5036640756' if used_phone else '(blank)'}")
        print(f"Email: {email}")
        print(f"Zip Code: {zip_code}")
        print(f"Military: {military_answer}")
        print(f"Quote Journey: {scenario_config['quote_journey']}")
        print(f"\nPets Added: {len(scenario_config['pets'])}")
        for pet in scenario_config["pets"]:
            if pet["type"] == "dog":
                print(f"  - {pet['name']} ({pet['type'].title()}, {pet['gender']}, {pet['breed']}, {pet['age']}, Service: {pet['is_service_dog']})")
            else:
                print(f"  - {pet['name']} ({pet['type'].title()}, {pet['gender']}, {pet['breed']}, {pet['age']})")

        # Print Quote ID if captured
        if self.quote_id:
            print(f"\n🎯 Quote ID: {self.quote_id}")
        else:
            print(f"\n⚠️  Quote ID not captured (may not have reached that step)")

        print("=" * 60)

        return {
            "scenario_config": scenario_config,
            "call_source": call_source,
            "used_name": used_name,
            "used_phone": used_phone,
            "email": email,
            "zip_code": zip_code,
            "quote_id": self.quote_id
        }


def main(scenario_type: str = None, output_folder: str = None, quote_journey: str = None, scenario_name: str = None):
    """
    Main execution function

    Args:
        scenario_type: 'dog_only', 'cat_only', 'multi_pet', or None for random
        output_folder: Optional output folder path. If None, creates a timestamped folder
        quote_journey: Optional quote journey. If None, uses random from config
        scenario_name: Optional unique name for file saving. If None, uses scenario_type
    """

    # Use Playwright profile with saved login
    playwright_profile_path = str(Path.home() / "playwright-profiles" / "trackr-qa")

    print("=" * 60)
    print("Trackr Quote Flow Automation")
    print("=" * 60)

    if not Path(playwright_profile_path).exists():
        print(f"\n✗ Playwright profile not found!")
        print(f"\nRun setup first:")
        print(f"  python3 setup_playwright_profile.py")
        return

    # Generate scenario configuration
    if scenario_type is None:
        scenario_type = random.choice(["dog_only", "cat_only", "multi_pet", "one_of_each"])

    scenario_config = generate_scenario_config(scenario_type)

    # Use unique scenario_name for file saving if provided, otherwise use scenario_type
    if scenario_name:
        scenario_config["scenario_type"] = scenario_name

    # Override quote_journey if specified
    if quote_journey:
        scenario_config["quote_journey"] = quote_journey

    # Create timestamp folder for output if not provided
    if output_folder is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = f"output_{timestamp}"
        os.makedirs(output_folder, exist_ok=True)
        print(f"\n📁 Output folder: {output_folder}")

    print(f"\n📋 Generated scenario: {scenario_type.replace('_', ' ').title()}")
    print(f"   Military: {scenario_config['military']}")
    print(f"   Pets: {len(scenario_config['pets'])}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=playwright_profile_path,
            headless=False,
            slow_mo=100,
            viewport={'width': 1920, 'height': 1080},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check'
            ]
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("\n📂 Opening Trackr application...")
            page.goto(START_QUOTE_URL)

            # Wait for page to load
            page.wait_for_load_state("networkidle")
            print("✓ Page loaded")

            # Run the complete quote flow
            quote_flow = TrackrQuoteFlow(page, output_folder=output_folder)
            quote_flow.complete_quote_flow(scenario_config)

            if output_folder:
                print(f"\n📸 Output saved to {output_folder}/")
                print(f"   - JSON data: {output_folder}/json/")
                print(f"   - Screenshots: {output_folder}/screenshots/")

            print("\n✓ Quote flow completed successfully!")
            print("\nBrowser will remain open for 10 seconds for inspection...")
            time.sleep(10)

        except Exception as e:
            print(f"\n✗ Error during automation: {str(e)}")
            if output_folder:
                error_screenshot = os.path.join(output_folder, "screenshots", "error.png")
                page.screenshot(path=error_screenshot, full_page=True)
                print(f"Error screenshot saved: {error_screenshot}")
            raise
        finally:
            context.close()


if __name__ == "__main__":
    import sys

    # Allow command line argument for scenario type
    scenario = sys.argv[1] if len(sys.argv) > 1 else None

    if scenario and scenario not in ["dog_only", "cat_only", "multi_pet", "one_of_each"]:
        print("Invalid scenario type. Use: dog_only, cat_only, multi_pet, or one_of_each")
        print("Or run without arguments for random scenario")
        sys.exit(1)

    main(scenario)
