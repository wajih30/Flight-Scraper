Flight Scraper


Overview

Flight Scraper is a Python-based flight price monitoring tool that automatically checks flight prices using the Amadeus API and sends email alerts when prices drop below a user-defined threshold. It supports multiple recipients, customizable thresholds, and periodic re-checks.

Features

Monitor flight prices for any route and date.

Email alerts when prices fall below your set threshold.

Avoid duplicate alerts for the same user, route, date, and price.

Configurable interval for automatic rechecks.

Supports multiple users and email addresses.

Uses Amadeus API for accurate flight data.

Generates generic Google Flights links for booking.

Folder Structure (flight_scraper)

flight_scraper/
├── main.py            # Main script to run the flight monitoring
├── scraper.py         # Handles flight API requests and alert tracking
├── emailer.py         # Sends email alerts via SMTP
├── config.yaml        # Configuration file for intervals and email settings
├── alerts_sent.json   # Tracks already-sent alerts to avoid duplicates
├── .env               # Environment variables (SMTP and Amadeus API credentials)
└── requirements.txt   # Python dependencies

Setup

Clone the repository

git clone https://github.com/wajih30/Flight-Scraper.git
cd Flight-Scraper/flight_scraper

Create a virtual environment and activate it

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Set up environment variables in .env

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_email_password
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret

Update config.yaml if needed

scheduler:
  interval_minutes: 30  # check interval

email:
  from: your_email@gmail.com

Usage

Run the main script:

python main.py

Workflow

Enter recipient email.

Enter origin and destination airport codes.

Enter departure date (YYYY-MM-DD).

Set your price threshold.

Choose currency (USD, EUR, etc.).

The script will check flight prices and send alerts if below threshold.

Options after each check:

c: Change threshold.

s: Skip this route.

r: Recheck after the configured interval.

n: Enter a new flight route.

Notes

Alerts are tracked in alerts_sent.json to avoid sending multiple emails for the same user and price.

Google Flights links are generic; users may need to select exact flights manually.

Ensure your SMTP credentials and Amadeus API keys are correct.

Dependencies

amadeus==12.0.0

certifi==2025.8.3

charset-normalizer==3.4.3

google_search_results==2.4.2

idna==3.10

python-dotenv==1.1.1

PyYAML==6.0.2

requests==2.32.5

urllib3==2.5.0
