"""
Pytest tests for Trackr automation
Run with: pytest test_trackr.py -v --headed
"""

import pytest
from playwright.sync_api import Page, expect
import os


@pytest.fixture(scope="function")
def base_url():
    """Base URL fixture"""
    return "https://epi-trakrui-nb-2390.azurewebsites.net"


@pytest.fixture(scope="function", autouse=True)
def setup_screenshots():
    """Create screenshots directory before tests"""
    os.makedirs("screenshots", exist_ok=True)
    yield


def test_navigate_to_start_quote(page: Page, base_url):
    """Test navigation to the start quote page"""
    page.goto(f"{base_url}/quoting/start-quote")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Take screenshot
    page.screenshot(path="screenshots/test_01_navigation.png", full_page=True)

    # Verify URL
    assert "start-quote" in page.url
    print(f"Successfully navigated to: {page.url}")


def test_page_title(page: Page, base_url):
    """Test that page has a title"""
    page.goto(f"{base_url}/quoting/start-quote")
    page.wait_for_load_state("networkidle")

    title = page.title()
    assert title is not None
    assert len(title) > 0
    print(f"Page title: {title}")


def test_explore_form_elements(page: Page, base_url):
    """Explore and validate form elements on the page"""
    page.goto(f"{base_url}/quoting/start-quote")
    page.wait_for_load_state("networkidle")

    # Count input fields
    inputs = page.locator("input").all()
    print(f"\nFound {len(inputs)} input fields")

    # Count buttons
    buttons = page.locator("button").all()
    print(f"Found {len(buttons)} buttons")

    # Log details
    for idx, input_field in enumerate(inputs):
        input_type = input_field.get_attribute("type") or "text"
        input_name = input_field.get_attribute("name") or "N/A"
        print(f"  Input {idx + 1}: type={input_type}, name={input_name}")

    page.screenshot(path="screenshots/test_02_form_elements.png", full_page=True)


def test_fill_sample_form(page: Page, base_url):
    """
    Test filling out a form (customize based on actual form fields)
    This is a template - update selectors based on actual form
    """
    page.goto(f"{base_url}/quoting/start-quote")
    page.wait_for_load_state("networkidle")

    # Example: Fill form fields (uncomment and customize)
    # page.fill("input[name='firstName']", "John")
    # page.fill("input[name='lastName']", "Doe")
    # page.fill("input[name='email']", "john.doe@example.com")

    page.screenshot(path="screenshots/test_03_filled_form.png", full_page=True)

    # Add assertions based on your form
    # expect(page.locator("input[name='firstName']")).to_have_value("John")


def test_button_interaction(page: Page, base_url):
    """
    Test button interactions (customize based on actual buttons)
    """
    page.goto(f"{base_url}/quoting/start-quote")
    page.wait_for_load_state("networkidle")

    # Example: Click a button (uncomment and customize)
    # page.get_by_role("button", name="Next").click()
    # page.wait_for_load_state("networkidle")

    page.screenshot(path="screenshots/test_04_button_interaction.png", full_page=True)


@pytest.mark.slow
def test_complete_quote_flow(page: Page, base_url):
    """
    Test complete quote creation flow
    This is a template for end-to-end testing
    """
    page.goto(f"{base_url}/quoting/start-quote")
    page.wait_for_load_state("networkidle")
    page.screenshot(path="screenshots/test_05_step1.png", full_page=True)

    # Step 1: Fill initial form
    # page.fill("input[name='field1']", "value1")
    # page.screenshot(path="screenshots/test_05_step2.png", full_page=True)

    # Step 2: Submit/Next
    # page.get_by_role("button", name="Next").click()
    # page.wait_for_load_state("networkidle")
    # page.screenshot(path="screenshots/test_05_step3.png", full_page=True)

    # Step 3: Complete additional steps
    # Add more steps based on actual flow

    # Final verification
    print("Complete quote flow test executed")
