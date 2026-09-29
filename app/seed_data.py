import json
from app.database import get_db, init_db

def seed():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Clear existing seed data to allow clean re-runs
    cursor.execute("DELETE FROM alerts")
    cursor.execute("DELETE FROM safe_locations")
    cursor.execute("DELETE FROM households")
    cursor.execute("DELETE FROM help_requests")
    cursor.execute("DELETE FROM sea_trackers")

    # 1. Active Alerts (Bengaluru & Udupi Coastal) - Clearly labeled SIMULATED
    alerts = [
        (
            "ALERT-BLR-FLD-01",
            "Bengaluru Urban",
            "flood",
            "severe",
            "[SIMULATED] Red Alert: Severe Urban Inundation & Bellandur Lake Breach",
            "Continuous torrential rainfall (185mm) has caused severe waterlogging across Bellandur, Sarjapur, HSR Layout, and Whitefield. Ground-floor residences report 3-4 ft water ingress.",
            "Evacuate ground floors immediately. If trapped by rising water, switch off main breaker, move to first floor or roof, and call 112.",
            None,
            None,
            "2026-09-29 08:00:00",
            "2026-09-30 18:00:00"
        ),
        (
            "ALERT-BLR-HTW-02",
            "Bengaluru Urban",
            "heatwave",
            "warning",
            "[SIMULATED] Orange Alert: Severe Heatwave Conditions (Peak 40.5°C)",
            "Day temperatures are 5-6°C above normal. High UV index and severe thermal discomfort expected between 11:30 AM and 4:00 PM.",
            "Stay indoors during peak hours. Drink ORS, tender coconut, or water frequently. Check on elderly relatives living alone.",
            None,
            None,
            "2026-09-29 06:00:00",
            "2026-09-29 20:00:00"
        ),
        (
            "ALERT-UDP-CYC-01",
            "Udupi Coastal",
            "cyclone",
            "severe",
            "[SIMULATED] Cyclone Warning: Severe Cyclonic Storm 'Sagar' Landfall in 14 Hours",
            "Cyclone Sagar is tracking Northeastward at 16 km/h with sustained winds of 110-120 kmph gusting to 135 kmph. Expected landfall near Malpe-Kundapura belt in 14 hours.",
            "Evacuate kutcha and low-lying coastal homes within 5 km of coast immediately. Move to designated Cyclone Shelters.",
            14.0,
            2.5,
            "2026-09-29 07:30:00",
            "2026-09-30 22:00:00"
        ),
        (
            "ALERT-UDP-TSU-02",
            "Udupi Coastal",
            "tsunami",
            "catastrophic",
            "[SIMULATED] EMERGENCY: Tsunami Warning - Sea Recession Reported at Malpe Beach",
            "Major undersea seismic event in Arabian basin. Massive sea recession observed along Karnataka coast. Tsunami wave surge imminent.",
            "IMMEDIATE ACTION REQUIRED: Move inland to high ground (minimum 15m elevation or 2 km inland) NOW. Do not stop to collect belongings. Do not stay on ground or first floors.",
            0.5,
            4.2,
            "2026-09-29 08:45:00",
            "2026-09-29 14:00:00"
        ),
        (
            "ALERT-UDP-SURGE-03",
            "Udupi Coastal",
            "storm_surge",
            "severe",
            "[SIMULATED] Storm Surge & High Wave Warning (4.5m Inundation)",
            "High astronomical spring tides coupled with cyclone approach will cause 3.5m to 4.5m surge waves breaching coastal seawalls from Kaup to Kundapura.",
            "Do not stay on ground or first floors near the coast. Storm surge waves carry destructive force; move inland to elevated relief centers.",
            6.0,
            4.5,
            "2026-09-29 08:00:00",
            "2026-09-30 12:00:00"
        )
    ]
    cursor.executemany("""
    INSERT INTO alerts (id, region, disaster_type, severity, headline, description, instructions, landfall_eta_hours, surge_height_m, issued_at, valid_until)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alerts)

    # 2. Safe Locations (Shelters, Hospitals, High Ground) in Bengaluru and Udupi
    safe_locs = [
        # Bengaluru Shelters & Hospitals
        (
            "SHELTER-BLR-01",
            "BBMP Community Relief Center & Indoor Stadium",
            "shelter",
            "Bengaluru Urban",
            12.9128,
            77.6387,
            "14th Main, Sector 3, HSR Layout, Bengaluru (Elevated Ground)",
            350,
            42,
            1, # Pet friendly
            1, # Wheelchair accessible
            1, # Has medical facility (insulin cold storage available)
            910.0,
            "080-22660000"
        ),
        (
            "HOSP-BLR-02",
            "St. John's Medical College Hospital",
            "hospital",
            "Bengaluru Urban",
            12.9344,
            77.6200,
            "Sarjapur Main Road, Koramangala 2nd Block, Bengaluru",
            500,
            380,
            0,
            1,
            1,
            915.0,
            "080-22065000"
        ),
        (
            "HIGH-BLR-03",
            "Koramangala Indoor High-Ground Evacuation Hub",
            "high_ground",
            "Bengaluru Urban",
            12.9352,
            77.6245,
            "80 Feet Road, 4th Block, Koramangala (Elevated Ridgeline)",
            600,
            110,
            1,
            1,
            1,
            925.0,
            "112"
        ),
        # Udupi Coastal Shelters & High Ground
        (
            "SHELTER-UDP-01",
            "Malpe Cyclone Relief Center & Govt High School",
            "cyclone_relief_center",
            "Udupi Coastal",
            13.3512,
            74.7088,
            "Kodi Bengre Road, Vadabhandeshwara, Malpe, Udupi",
            400,
            85,
            1, # Pet/Livestock holding yard
            1, # Wheelchair ramps
            1, # First Aid & Paramedics
            22.0, # 22 meters above sea level
            "0820-2521155"
        ),
        (
            "HIGH-UDP-02",
            "St. Mary's Elevated Ridge & District Relief Camp",
            "high_ground",
            "Udupi Coastal",
            13.3408,
            74.7421,
            "Kunjibettu - Manipal Elevated Ridge, Udupi",
            800,
            140,
            1,
            1,
            1,
            65.0, # 65 meters elevation - immune to storm surge & tsunami
            "0820-2571200"
        ),
        (
            "HOSP-UDP-03",
            "KMC Hospital Manipal (Tertiary Trauma Care)",
            "hospital",
            "Udupi Coastal",
            13.3525,
            74.7850,
            "Tiger Circle, Madhav Nagar, Manipal, Udupi",
            1200,
            950,
            0,
            1,
            1,
            75.0,
            "0820-2922761"
        )
    ]
    cursor.executemany("""
    INSERT INTO safe_locations (id, name, location_type, region, latitude, longitude, address, capacity, current_occupancy, is_pet_friendly, is_wheelchair_accessible, has_medical_facility, elevation_meters, contact_phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, safe_locs)

    # 3. Seed Households representing Key Scenarios
    households = [
        (
            "HH-BLR-01",
            "Ramesh Rao",
            "+91-9845012345",
            "kn", # Kannada preferred
            "Rainbow Drive Layout, Sarjapur Road, Bengaluru",
            12.9150,
            77.6740,
            350.0,
            0, # Not at sea
            1, # Has elderly mother (82 yrs)
            0,
            1, # Limited mobility
            json.dumps(["Insulin (Lantus / Regular)", "BP medication"]),
            json.dumps(["Golden Retriever dog"]),
            json.dumps([{"name": "Suresh Rao (Brother)", "phone": "+91-9845099887", "relation": "Brother"}]),
            "ground_floor_apartment"
        ),
        (
            "HH-BLR-02",
            "Kamala Devi",
            "+91-9845123456",
            "en",
            "Indiranagar 1st Stage, Bengaluru",
            12.9784,
            77.6408,
            350.0,
            0,
            1, # Elderly living alone (76 yrs)
            0,
            0,
            json.dumps(["Hypertension pills"]),
            json.dumps([]),
            json.dumps([{"name": "Anita (Daughter in US)", "phone": "+1-408-555-0199", "relation": "Daughter"}]),
            "pucca"
        ),
        (
            "HH-UDP-01",
            "Shekar Kunder",
            "+91-9448123890",
            "kn",
            "Malpe Fishermen Colony, Udupi",
            13.3480,
            74.7010,
            0.3, # 300 meters from coast
            1,   # Fisher at sea!
            1,   # Elderly father
            1,   # 8-month infant
            0,
            json.dumps(["Baby formula", "Asthma inhaler"]),
            json.dumps(["3 goats", "1 cow"]),
            json.dumps([{"name": "Naveen (Harbor Union)", "phone": "+91-9448001122", "relation": "Harbor In-charge"}]),
            "semi-pucca"
        )
    ]
    cursor.executemany("""
    INSERT INTO households (id, user_name, phone, language, location_name, latitude, longitude, distance_from_coast_km, works_at_sea, has_elderly, has_infants, has_disabled, critical_medicines, pets_livestock, emergency_contacts, home_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, households)

    # 4. Active Sea Trackers (Fisher at sea during cyclone / high waves)
    trackers = [
        (
            "BOAT-MALPE-04",
            "Matsyagandha-II (Trawler)",
            "Shekar Kunder",
            "+91-9448123890",
            "Malpe Harbor, Udupi",
            "18 Nautical Miles West of Malpe Light House",
            "AT_SEA_RETURNING",
            "2026-09-29 08:30:00"
        )
    ]
    cursor.executemany("""
    INSERT INTO sea_trackers (id, boat_name, captain_name, phone, harbor_base, last_known_location, status, contacted_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, trackers)

    # 5. Active Help Requests (Sample for Responder Dashboard)
    requests = [
        (
            "SOS-BLR-001",
            "HH-BLR-01",
            "Ramesh Rao",
            "+91-9845012345",
            "Rainbow Drive Layout, Sarjapur Road, Bengaluru",
            12.9150,
            77.6740,
            "NEED_HELP",
            "CRITICAL_LIFE_THREAT",
            "Water entered ground floor apartment, currently 2.5 ft deep and rising. 82-year-old mother is on insulin and requires wheelchair evacuation. 1 pet dog with family.",
            3,
            1,
            0,
            1,
            1, # requires inflatable boat
            1, # requires cold chain for insulin
            "SDRF Team 4 dispatched from Bellandur station at 08:40 AM with Zodiac inflatable boat."
        )
    ]
    cursor.executemany("""
    INSERT INTO help_requests (id, household_id, user_name, phone, location_name, latitude, longitude, status, urgency, needs_description, num_people, has_elderly, has_infants, has_pets, requires_boat, requires_medical, responder_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, requests)

    conn.commit()
    conn.close()
    print("Seed data loaded successfully.")

if __name__ == "__main__":
    seed()
