# scraper.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from amadeus import Client, ResponseError

load_dotenv()

# Load Amadeus credentials from .env
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

# JSON file to track already-sent alerts (no DB required)
ALERTS_FILE = Path("alerts_sent.json")


def load_alerts():
    """Load previously sent alerts from JSON file."""
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_alerts(alerts):
    """Save alerts dictionary back to JSON file."""
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def was_alert_sent(route_key):
    """Check if alert for this route/price has already been sent."""
    alerts = load_alerts()
    return route_key in alerts


def record_alert_sent(route_key):
    """Record that we sent an alert for this route/price."""
    alerts = load_alerts()
    alerts[route_key] = True
    save_alerts(alerts)


def get_lowest_price(origin: str, destination: str, date: str):
    """
    Query Amadeus API and return the cheapest flight offer details:
    - Route (Origin → Destination)
    - Date
    - Airline
    - Price
    - Departure Time
    - Booking Link
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            currencyCode="USD",
            max=10
        )

        if not response.data:
            return None

        # Find cheapest offer
        cheapest = min(response.data, key=lambda offer: float(offer["price"]["total"]))
        price = float(cheapest["price"]["total"])
        currency = cheapest["price"]["currency"]

        airline = cheapest["validatingAirlineCodes"][0]

        first_segment = cheapest["itineraries"][0]["segments"][0]
        departure_time = first_segment["departure"]["at"]

        # Generate a search link (Amadeus doesn’t give booking URLs directly)
        link = f"https://www.google.com/flights?hl=en#flt={origin}.{destination}.{date}"

        return {
            "route": f"{origin} → {destination}",
            "date": date,
            "airline": airline,
            "price": f"{price} {currency}",
            "departure_time": departure_time,
            "link": link,
        }

    except ResponseError as e:
        print("❌ Amadeus API error:", e)
        return None
