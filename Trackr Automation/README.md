# Trackr Automation

Playwright automation for the Trackr quoting application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the automation:
```bash
python trackr_automation.py
```

Run with pytest:
```bash
pytest test_trackr.py -v --headed
```

## Configuration

The target URL is: https://epi-trakrui-nb-2390.azurewebsites.net/quoting/start-quote
