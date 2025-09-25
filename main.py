# main.py
import yaml
import time
from scraper import get_lowest_price, was_alert_sent, record_alert_sent
from emailer import send_alert

# Load config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

INTERVAL = config["scheduler"]["interval_minutes"] * 60
EMAIL_FROM = config["email"]["from"]
EMAIL_TO = config["email"]["to"]
ROUTES = config["routes"]

def check_flights():
    for route in ROUTES:
        origin = route["origin"]
        destination = route["destination"]
        date = route["date"]
        threshold = route["threshold"]

        print(f"🔍 Checking {origin} → {destination} on {date}...")

        flight = get_lowest_price(origin, destination, date)

        if not flight:
            print("❌ No flights found.")
            continue

        # Unique key for this alert (route + date + price)
        route_key = f"{origin}-{destination}-{date}-{flight['price']}"

        if was_alert_sent(route_key):
            print(f"⏩ Alert already sent for {route_key}, skipping.")
            continue

        price_value = float(flight["price"].split()[0])  # e.g. "164.52 USD" → 164.52

        if price_value <= threshold:
            subject = f"✈️ Flight Alert: {flight['route']} at {flight['price']}"
            body = (
                f"Good news! We found a cheap flight:\n\n"
                f"Route: {flight['route']}\n"
                f"Date: {flight['date']}\n"
                f"Airline: {flight['airline']}\n"
                f"Price: {flight['price']}\n"
                f"Departure Time: {flight['departure_time']}\n"
                f"Booking Link: {flight['link']}\n\n"
                f"Don't wait too long — prices can change quickly!"
            )

            # Send the email
            send_alert(subject, body, EMAIL_TO)
            print(f"✅ Alert sent for {route_key}!")

            # Record alert in alerts_sent.json
            record_alert_sent(route_key)
        else:
            print(f"💸 Cheapest price {flight['price']} is above threshold {threshold}.")

if __name__ == "__main__":
    print("🚀 Flight price monitor started.")
    while True:
        check_flights()
        print(f"⏳ Waiting {INTERVAL/60} minutes before next check...\n")
        time.sleep(INTERVAL)
