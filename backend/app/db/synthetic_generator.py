"""Enterprise synthetic data generator seeding 15,000 incidents, 3,000 cases, and 2,000+ entities."""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from typing import Any, List, Dict, Tuple

from .models import ZONES, CRIME_TYPES, NAMES, STREETS
from ..utils.helpers import NOW, iso

# Expanded pools to generate unique dataset attributes
FIRST_NAMES = ["Ravi", "Aisha", "Dev", "Nisha", "Kabir", "Priya", "Arun", "Meera", "Vikram", "Neha", "Amit", "Karan", "Siddharth", "Aditi", "Rahul", "Pooja", "Raj", "Sunita", "Sanjay", "Anjali"]
LAST_NAMES = ["Shah", "Khan", "Malhotra", "Verma", "Rao", "Sen", "Das", "Iyer", "Sharma", "Joshi", "Gupta", "Mehta", "Patel", "Reddy", "Nair", "Singh", "Choudhury", "Bose", "Trivedi", "Gill"]


def seed_demo_data(conn: Any) -> None:
    """Seed the database with a reproducible, high-volume synthetic demo dataset."""
    if not conn.is_postgres:
        old_isolation = conn.raw.isolation_level
        conn.raw.isolation_level = None
        conn.execute("BEGIN TRANSACTION")
    rng = random.Random(20260716)
    
    # 1. Insert Zones and Zone Contexts
    for zone in ZONES:
        conn.execute(
            "INSERT INTO zones VALUES (?, ?, ?, ?, ?)",
            (zone["id"], zone["name"], zone["lat"], zone["lng"], zone["patrol"]),
        )
        context = {
            "sector-7": ("high density", 0.86, "festival corridor", 0.61),
            "old-town": ("high density", 0.72, "market activity", 0.54),
            "rivergate": ("mixed density", 0.58, "weekend waterfront", 0.43),
            "central": ("commercial", 0.66, "commuter corridor", 0.37),
        }[zone["id"]]
        conn.execute(
            "INSERT INTO zone_context(zone_id, population_band, traffic_index, event_factor, unemployment_index, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (zone["id"], *context, iso(NOW)),
        )

    # 2. Build unique entity pools
    # 2000 Persons: 800 repeat offenders, 1200 non-repeaters
    all_names: List[str] = []
    while len(all_names) < 2000:
        middle_initial = chr(rng.randint(65, 90))
        name = f"{rng.choice(FIRST_NAMES)} {middle_initial}. {rng.choice(LAST_NAMES)}"
        if name not in all_names:
            all_names.append(name)
    repeat_offenders = all_names[:800]
    non_repeaters = all_names[800:]

    # 1500 Vehicles
    all_vehicles: List[str] = []
    while len(all_vehicles) < 1500:
        vehicle = f"DL-{rng.randint(1, 99):02d}-K-{rng.randint(1000, 9999):04d}"
        if vehicle not in all_vehicles:
            all_vehicles.append(vehicle)

    # 2500 Phone Numbers
    all_phones: List[str] = []
    while len(all_phones) < 2500:
        phone = f"+91-9871-{rng.randint(1000, 9999):04d}"
        if phone not in all_phones:
            all_phones.append(phone)

    # 1200 Addresses
    all_addresses: List[str] = []
    while len(all_addresses) < 1200:
        address = f"{rng.randint(10, 999)} {rng.choice(STREETS)}"
        if address not in all_addresses:
            all_addresses.append(address)

    # 3. Generate 3,000 cases and 15,000 incidents
    case_number = 7000
    incident_number = 1
    
    # CCTV, court, and prison target numbers
    cctv_targets = 1000
    court_targets = 700
    prison_targets = 400

    # Distribute cases chronologically over the past 180 days
    for day_offset in range(180, -1, -1):
        date = NOW - timedelta(days=day_offset)
        # Average cases per day: ~16 (so 180 * 16 = 2,880 + remaining)
        day_cases_count = 16 if day_offset > 0 else 120
        
        for _ in range(day_cases_count):
            if case_number >= 10000:
                break
                
            case_number += 1
            case_id = f"FIR-{case_number}"
            zone = rng.choice(ZONES)
            crime_type = rng.choice(CRIME_TYPES)
            recent = day_offset < 14
            street = rng.choice(STREETS)
            summary = f"{crime_type} reported near {street}."
            
            # Insert case record
            conn.execute(
                "INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?)",
                (case_id, zone["id"], iso(date), "Open" if recent else "Closed", summary, crime_type),
            )
            
            # Generate exactly 5 incidents per case -> 15,000 incidents total
            for i in range(5):
                incident_id = f"INC-{incident_number:05d}"
                incident_number += 1
                occurred_at = date + timedelta(hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
                lat = zone["lat"] + rng.gauss(0, 0.002)
                lng = zone["lng"] + rng.gauss(0, 0.002)
                narrative = f"Incident log {i+1} for {crime_type.lower()} case near {street}."
                
                if conn.is_postgres:
                    conn.execute(
                        """INSERT INTO incidents(id, case_id, zone_id, crime_type, occurred_at, latitude, longitude, geom, source, narrative)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ST_SetSRID(ST_MakePoint(?, ?), 4326), ?, ?)""",
                        (incident_id, case_id, zone["id"], crime_type, iso(occurred_at), lat, lng, lng, lat, "synthetic", narrative),
                    )
                else:
                    conn.execute(
                        "INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (incident_id, case_id, zone["id"], crime_type, iso(occurred_at), lat, lng, "synthetic", narrative),
                    )
            
            # Link Entities: Person, Vehicle, Phone, Address
            # Person: 60% chance to be repeat offender, 40% chance regular
            if rng.random() < 0.60:
                person = rng.choice(repeat_offenders)
            else:
                person = rng.choice(non_repeaters)
                
            vehicle = rng.choice(all_vehicles)
            phone = rng.choice(all_phones)
            address = rng.choice(all_addresses)
            
            entities = [
                ("person", person.lower(), person),
                ("vehicle", vehicle.lower(), vehicle),
                ("phone", phone.replace("-", ""), phone),
                ("address", address.lower(), address),
            ]
            
            for ent_type, norm, disp in entities:
                conn.execute(
                    "INSERT INTO case_entities(case_id, entity_type, normalized_value, display_value) VALUES (?, ?, ?, ?)",
                    (case_id, ent_type, norm, disp),
                )
                
            # Insert Source Records (Evidence)
            # Default Police FIR record
            conn.execute(
                "INSERT INTO source_records(case_id, source_system, record_type, recorded_at, payload_json, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                (case_id, "Police FIR", "FIR registration", iso(date), json.dumps({"reference": case_id, "crime_type": crime_type}), 1.0),
            )
            
            # CCTV Sighting
            if cctv_targets > 0 and rng.random() < 0.35:
                cctv_targets -= 1
                payload = {"camera_reference": f"CAM-{zone['id'][-1]}-{case_number % 40:02d}", "match_type": "vehicle"}
                conn.execute(
                    "INSERT INTO source_records(case_id, source_system, record_type, recorded_at, payload_json, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                    (case_id, "CCTV & lab", "Observation match", iso(date), json.dumps(payload), 0.75),
                )
                
            # Court Case
            if court_targets > 0 and rng.random() < 0.25:
                court_targets -= 1
                payload = {"linked_reference": f"JUD-{case_number % 100:03d}", "stage": "court filing"}
                conn.execute(
                    "INSERT INTO source_records(case_id, source_system, record_type, recorded_at, payload_json, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                    (case_id, "Court & prison", "Justice-system linkage", iso(date), json.dumps(payload), 0.85),
                )
                
            # Prison Record
            if prison_targets > 0 and rng.random() < 0.15:
                prison_targets -= 1
                payload = {"inmate_reference": f"PRIS-{case_number % 100:03d}", "facility": "Central Correctional"}
                conn.execute(
                    "INSERT INTO source_records(case_id, source_system, record_type, recorded_at, payload_json, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                    (case_id, "Court & prison", "Justice-system linkage", iso(date), json.dumps(payload), 0.90),
                )
                
    if not conn.is_postgres:
        conn.execute("COMMIT")
        conn.raw.isolation_level = old_isolation
