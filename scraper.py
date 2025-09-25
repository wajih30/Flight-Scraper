# scraper.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote
from amadeus import Client, ResponseError  # Amadeus API

load_dotenv()

# --- Load credentials ---
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
    raise ValueError("Amadeus credentials are not set in .env")

# Initialize Amadeus client
amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

# JSON file to track already-sent alerts
ALERTS_FILE = Path("alerts_sent.json")


# --- Alert tracking functions ---
def load_alerts():
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def was_alert_sent(route_key):
    alerts = load_alerts()
    return route_key in alerts


def record_alert_sent(route_key):
    alerts = load_alerts()
    alerts[route_key] = True
    save_alerts(alerts)


# --- Function to generate generic Google Flights link ---
def get_google_flights_link(origin, destination, date):
    """
    Returns a standard Google Flights link for the given route and date.
    The link will NOT pre-fill exact flights.
    """
    return f"https://www.google.com/travel/flights?hl=en&f={quote(origin)}&t={quote(destination)}&d={quote(date)}"


# --- Main function to get flight info ---
def get_lowest_price(origin: str, destination: str, date: str, currency: str = "USD"):
    """
    Query Amadeus API and return the cheapest flight offer details:
    - Route (Origin → Destination)
    - Date
    - Airline (full name)
    - Price
    - Departure Time
    - Booking Link (generic Google Flights)
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            currencyCode=currency,
            max=10
        )

        if not response.data:
            print("❌ No flight data returned by Amadeus.")
            return None

        # Find cheapest flight
        cheapest = min(response.data, key=lambda offer: float(offer["price"]["total"]))
        price = float(cheapest["price"]["total"])
        currency_code = cheapest["price"]["currency"]

        # Get full airline name
        airline_code = cheapest["validatingAirlineCodes"][0]
        try:
            airline_info = amadeus.reference_data.airlines.get(airlineCodes=airline_code)
            airline = airline_info.data[0].get("commonName") or airline_code
        except Exception as e:
            print(f"❌ Failed to fetch full airline name for {airline_code}: {e}")
            airline = airline_code

        # Get first segment departure time
        first_segment = cheapest["itineraries"][0]["segments"][0]
        departure_time = first_segment["departure"]["at"]

        # Use generic Google Flights link
        link = get_google_flights_link(origin, destination, date)

        return {
            "route": f"{origin} → {destination}",
            "date": date,
            "airline": airline,
            "price": f"{price} {currency_code}",
            "departure_time": departure_time,
            "link": link,
        }

    except ResponseError as e:
        print("❌ Amadeus API error:", e)
        return None
