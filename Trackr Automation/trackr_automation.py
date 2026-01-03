"""
Trackr Automation Script
Automates the quoting process on the Trackr application
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time
from typing import Optional
from config import BASE_URL, START_QUOTE_URL


class TrackrAutomation:
    """Main automation class for Trackr quoting application"""

    def __init__(self, headless: bool = False, slow_mo: int = 500, user_data_dir: Optional[str] = None):
        """
        Initialize the automation

        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by specified milliseconds
            user_data_dir: Path to Chrome user data directory for persistent authentication
        """
        self.base_url = BASE_URL
        self.start_quote_url = START_QUOTE_URL
        self.headless = headless
        self.slow_mo = slow_mo
        self.user_data_dir = user_data_dir
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.using_persistent_context = False

    def setup(self):
        """Setup browser and navigate to start quote page"""
        self.playwright = sync_playwright().start()

        # Use persistent context if user data directory is provided
        if self.user_data_dir:
            print(f"Using persistent context from: {self.user_data_dir}")
            print("Note: Playwright uses Chromium engine but will load your Chrome profile data")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                slow_mo=self.slow_mo,
                viewport={'width': 1920, 'height': 1080},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--no-default-browser-check'
                ]
            )
            self.using_persistent_context = True
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        else:
            # Launch browser with configuration (standard mode)
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )

            # Create context with viewport
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            # Create new page
            self.page = self.context.new_page()

        # Enable console logging
        self.page.on("console", lambda msg: print(f"Browser console: {msg.text}"))

        print(f"Navigating to {self.start_quote_url}")
        self.page.goto(self.start_quote_url, wait_until="networkidle")

        # Take screenshot of initial page
        self.page.screenshot(path="screenshots/01_initial_page.png", full_page=True)
        print("Screenshot saved: screenshots/01_initial_page.png")

    def explore_page(self):
        """Explore and log page elements"""
        if not self.page:
            raise Exception("Page not initialized. Call setup() first.")

        print("\n=== Page Exploration ===")
        print(f"Current URL: {self.page.url}")
        print(f"Page Title: {self.page.title()}")

        # Find all input fields
        inputs = self.page.locator("input").all()
        print(f"\nFound {len(inputs)} input fields:")
        for idx, input_field in enumerate(inputs):
            input_type = input_field.get_attribute("type") or "text"
            input_name = input_field.get_attribute("name") or "N/A"
            input_id = input_field.get_attribute("id") or "N/A"
            input_placeholder = input_field.get_attribute("placeholder") or "N/A"
            print(f"  {idx + 1}. Type: {input_type}, Name: {input_name}, ID: {input_id}, Placeholder: {input_placeholder}")

        # Find all buttons
        buttons = self.page.locator("button").all()
        print(f"\nFound {len(buttons)} buttons:")
        for idx, button in enumerate(buttons):
            button_text = button.text_content() or "N/A"
            button_type = button.get_attribute("type") or "N/A"
            print(f"  {idx + 1}. Text: '{button_text}', Type: {button_type}")

        # Find all links
        links = self.page.locator("a").all()
        print(f"\nFound {len(links)} links:")
        for idx, link in enumerate(links[:10]):  # Limit to first 10
            link_text = link.text_content() or "N/A"
            link_href = link.get_attribute("href") or "N/A"
            print(f"  {idx + 1}. Text: '{link_text}', Href: {link_href}")

    def fill_quote_form(self, form_data: dict):
        """
        Fill out the quote form with provided data

        Args:
            form_data: Dictionary with form field names as keys and values to fill
        """
        if not self.page:
            raise Exception("Page not initialized. Call setup() first.")

        print("\n=== Filling Quote Form ===")
        for field_name, value in form_data.items():
            try:
                # Try by name attribute
                if self.page.locator(f"input[name='{field_name}']").count() > 0:
                    self.page.locator(f"input[name='{field_name}']").fill(str(value))
                    print(f"Filled field '{field_name}' with '{value}'")
                # Try by id
                elif self.page.locator(f"#{field_name}").count() > 0:
                    self.page.locator(f"#{field_name}").fill(str(value))
                    print(f"Filled field '#{field_name}' with '{value}'")
                else:
                    print(f"Warning: Field '{field_name}' not found")
            except Exception as e:
                print(f"Error filling field '{field_name}': {str(e)}")

    def click_button(self, button_text: str):
        """
        Click a button by its text content

        Args:
            button_text: The visible text on the button
        """
        if not self.page:
            raise Exception("Page not initialized. Call setup() first.")

        try:
            self.page.get_by_role("button", name=button_text).click()
            print(f"Clicked button: '{button_text}'")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Error clicking button '{button_text}': {str(e)}")

    def take_screenshot(self, filename: str):
        """Take a screenshot of current page"""
        if not self.page:
            raise Exception("Page not initialized. Call setup() first.")

        self.page.screenshot(path=f"screenshots/{filename}", full_page=True)
        print(f"Screenshot saved: screenshots/{filename}")

    def teardown(self):
        """Close browser and cleanup"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("\nBrowser closed successfully")


def main():
    """Main execution function"""
    # Create screenshots directory
    import os
    os.makedirs("screenshots", exist_ok=True)

    # Initialize automation
    automation = TrackrAutomation(headless=False, slow_mo=500)

    try:
        # Setup and navigate
        automation.setup()

        # Explore the page
        automation.explore_page()

        # Example: Fill form (customize based on actual form fields)
        # form_data = {
        #     "firstName": "John",
        #     "lastName": "Doe",
        #     "email": "john.doe@example.com"
        # }
        # automation.fill_quote_form(form_data)

        # Example: Click submit button
        # automation.click_button("Submit")

        # Wait for user to see the result
        input("\nPress Enter to close browser...")

    except Exception as e:
        print(f"Error during automation: {str(e)}")
        automation.take_screenshot("error.png")
    finally:
        automation.teardown()


if __name__ == "__main__":
    main()
