"""Database constants, static lists, and table schemas."""

from __future__ import annotations

# Static configurations for zones and incident generation
ZONES = [
    {"id": "sector-7", "name": "Sector 7", "lat": 28.6264, "lng": 77.2183, "patrol": 0.34},
    {"id": "old-town", "name": "Old Town", "lat": 28.6402, "lng": 77.2305, "patrol": 0.48},
    {"id": "rivergate", "name": "Rivergate", "lat": 28.6171, "lng": 77.2392, "patrol": 0.57},
    {"id": "central", "name": "Central Market", "lat": 28.6127, "lng": 77.2101, "patrol": 0.73},
]

ZONE_INDEX = {zone["id"]: zone for zone in ZONES}
CRIME_TYPES = ("Burglary", "Theft", "Vehicle theft", "Fraud", "Assault")
NAMES = ("Ravi Shah", "Aisha Khan", "Dev Malhotra", "Nisha Verma", "Kabir Rao", "Priya Sen", "Arun Das", "Meera Iyer")
STREETS = ("Junction 4", "Harbor Road", "Station Lane", "Market Street", "Canal View", "Civic Square")
