import sqlite3
import json
import os
from typing import Dict, Any, List, Optional

DB_PATH = os.environ.get("SAFEHAVEN_DB_PATH", "/config/Desktop/BuildWithGemini/safehaven/data/safehaven.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Households / User profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS households (
        id TEXT PRIMARY KEY,
        user_name TEXT,
        phone TEXT,
        language TEXT DEFAULT 'en',  -- en, kn (Kannada), hi (Hindi)
        location_name TEXT,
        latitude REAL,
        longitude REAL,
        distance_from_coast_km REAL DEFAULT 0,
        works_at_sea BOOLEAN DEFAULT 0,
        has_elderly BOOLEAN DEFAULT 0,
        has_infants BOOLEAN DEFAULT 0,
        has_disabled BOOLEAN DEFAULT 0,
        critical_medicines TEXT DEFAULT '[]', -- JSON list e.g. ["insulin"]
        pets_livestock TEXT DEFAULT '[]',     -- JSON list e.g. ["dog", "2 cows"]
        emergency_contacts TEXT DEFAULT '[]', -- JSON list of {name, phone, relation}
        home_type TEXT DEFAULT 'pucca',       -- kutcha, semi-pucca, pucca, ground_floor_apartment
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Active Disaster Alerts (Simulated IMD / INCOIS alerts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        region TEXT,            -- e.g. "Bengaluru Urban", "Udupi Coastal", "Karnataka Coast"
        disaster_type TEXT,     -- flood, heatwave, cyclone, storm_surge, tsunami, high_waves
        severity TEXT,          -- warning, severe, emergency, catastrophic
        headline TEXT,
        description TEXT,
        instructions TEXT,
        landfall_eta_hours REAL, -- for cyclone
        surge_height_m REAL,    -- for storm surge / tsunami
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        valid_until TIMESTAMP
    )
    """)

    # Shelters, Hospitals, and High Ground Points
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS safe_locations (
        id TEXT PRIMARY KEY,
        name TEXT,
        location_type TEXT,     -- shelter, hospital, high_ground, cyclone_relief_center
        region TEXT,
        latitude REAL,
        longitude REAL,
        address TEXT,
        capacity INTEGER,
        current_occupancy INTEGER DEFAULT 0,
        is_pet_friendly BOOLEAN DEFAULT 0,
        is_wheelchair_accessible BOOLEAN DEFAULT 0,
        has_medical_facility BOOLEAN DEFAULT 0,
        elevation_meters REAL DEFAULT 10.0,
        contact_phone TEXT
    )
    """)

    # Help Requests / SOS & Safety Checkins
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS help_requests (
        id TEXT PRIMARY KEY,
        household_id TEXT,
        user_name TEXT,
        phone TEXT,
        location_name TEXT,
        latitude REAL,
        longitude REAL,
        status TEXT,            -- NEED_HELP, SAFE, RESCUED, IN_PROGRESS
        urgency TEXT,           -- CRITICAL_LIFE_THREAT, HIGH, MEDIUM, LOW
        needs_description TEXT, -- e.g. "Water entered ground floor, elderly insulin user"
        num_people INTEGER DEFAULT 1,
        has_elderly BOOLEAN DEFAULT 0,
        has_infants BOOLEAN DEFAULT 0,
        has_pets BOOLEAN DEFAULT 0,
        requires_boat BOOLEAN DEFAULT 0,
        requires_medical BOOLEAN DEFAULT 0,
        responder_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Fishing / Sea Operations Tracker
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sea_trackers (
        id TEXT PRIMARY KEY,
        boat_name TEXT,
        captain_name TEXT,
        phone TEXT,
        harbor_base TEXT,       -- e.g. "Malpe Harbor, Udupi"
        last_known_location TEXT,
        status TEXT,            -- AT_SEA_RETURNING, SAFELY_DOCKED, IN_DISTRESS, SEARCH_RESCUE
        contacted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
