# main.py
import time
from datetime import datetime, timedelta
from scraper import get_lowest_price, was_alert_sent, record_alert_sent
from emailer import send_alert

INTERVAL = 30 * 60  # 30 minutes default
TOTAL_RUNTIME = 340  # total runtime in minutes

def get_route_from_user():
    """
    Ask the user to enter flight details and recipient email in the terminal.
    """
    recipient_email = input("Enter recipient email: ").strip()
    origin = input("Enter origin airport code (e.g., JFK): ").strip().upper()
    destination = input("Enter destination airport code (e.g., SFO): ").strip().upper()
    date = input("Enter departure date (YYYY-MM-DD): ").strip()
    threshold = float(input("Enter price threshold: ").strip())
    currency = input("Enter currency (e.g., USD, EUR): ").strip().upper()

    return {
        "recipient_email": recipient_email,
        "origin": origin,
        "destination": destination,
        "date": date,
        "threshold": threshold,
        "currency": currency
    }

def check_flight(route):
    """
    Check the flight price and send an email alert if price is below threshold.
    Returns True if user wants to check another flight, False to stop.
    """
    recipient_email = route["recipient_email"]
    origin = route["origin"]
    destination = route["destination"]
    date = route["date"]
    threshold = route["threshold"]
    currency = route.get("currency", "USD")

    while True:
        print(f"\n🔍 Checking {origin} → {destination} on {date} in {currency}...")
        flight = get_lowest_price(origin, destination, date, currency)

        if not flight:
            print("❌ No flights found.")
            choice = input("Do you want to search for another flight? (y/n): ").strip().lower()
            return choice == 'y'

        # Include recipient email in the route key to handle multiple users
        route_key = f"{recipient_email}-{origin}-{destination}-{date}-{flight['price']}"
        price_value = float(flight["price"].split()[0])

        # Check if alert was already sent for this user & price
        if was_alert_sent(route_key):
            print(f"⚠️ Alert already sent to {recipient_email} for {origin}-{destination} on {date} at {flight['price']}.")
        elif price_value <= threshold:
            # Send email
            subject = f"✈️ Flight Alert: {flight['route']} at {flight['price']}"
            body = (
                f"<p>Good news! We found a cheap flight:</p>"
                f"<ul>"
                f"<li><strong>Route:</strong> {flight['route']}</li>"
                f"<li><strong>Date:</strong> {flight['date']}</li>"
                f"<li><strong>Airline:</strong> {flight['airline']}</li>"
                f"<li><strong>Price:</strong> {flight['price']}</li>"
                f"<li><strong>Departure Time:</strong> {flight['departure_time']}</li>"
                f"<li><strong>Booking Link:</strong> "
                f"<a href='{flight['link']}' target='_blank'>Go to Google Flights</a></li>"
                f"</ul>"
                f"<p>Note: This link directs to Google Flights for the route. You may need to select the exact flight manually.</p>"
            )
            send_alert(subject, body, recipient_email, html=True)
            print(f"✅ Alert sent to {recipient_email} for {route_key}!")
            record_alert_sent(route_key)

        else:
            print(f"💸 Cheapest price {flight['price']} is above threshold {threshold} {currency}.")

        # Ask next action
        choice = input("Enter 'c' to change threshold, 's' to skip, 'r' to recheck, or 'n' for new flight: ").strip().lower()
        if choice == 'c':
            threshold = float(input("Enter new price threshold: ").strip())
        elif choice in ['s', 'n']:
            return True  # go back to main loop for new route or skip
        elif choice == 'r':
            print(f"⏳ Will recheck this route after {INTERVAL/60} minutes.")
            time.sleep(INTERVAL)
        else:
            print("❌ Invalid choice. Skipping route.")
            return True

if __name__ == "__main__":
    print("🚀 Flight price monitor started.")
    end_time = datetime.now() + timedelta(minutes=TOTAL_RUNTIME)

    while datetime.now() < end_time:
        route = get_route_from_user()
        continue_loop = check_flight(route)
        if not continue_loop:
            print("⏹ Stopping further flight checks as requested by user.")
            break
        print("\n")  # spacing for readability
