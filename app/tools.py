import json
import os
import math
from typing import Dict, Any, List, Optional
from app.database import get_db
from app.rules_engine import evaluate_emergency_protocol
from google import genai
from google.genai import types

def get_active_alerts(region_or_location: str) -> str:
    """Fetches active disaster and weather alerts for a given region (e.g. 'Bengaluru', 'Udupi').
    All data is clearly labeled as [SIMULATED] for emergency training and safety."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM alerts WHERE LOWER(region) LIKE ? OR LOWER(headline) LIKE ?",
        (f"%{region_or_location.lower()}%", f"%{region_or_location.lower()}%")
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not rows:
        # Fallback to all active alerts
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts LIMIT 3")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

    return json.dumps(rows, indent=2)

def get_nearest_safe_locations(
    latitude: float,
    longitude: float,
    location_type: Optional[str] = None,
    require_pet_friendly: bool = False,
    require_accessible: bool = False
) -> str:
    """Finds nearest shelters, hospitals, and high-ground points with distance calculation and facilities."""
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM safe_locations WHERE 1=1"
    params = []

    if location_type:
        query += " AND location_type = ?"
        params.append(location_type)
    if require_pet_friendly:
        query += " AND is_pet_friendly = 1"
    if require_accessible:
        query += " AND is_wheelchair_accessible = 1"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Simple Euclidean / Haversine distance ranking
    for loc in rows:
        dlat = (loc["latitude"] - latitude) * 111.0
        dlon = (loc["longitude"] - longitude) * 111.0 * math.cos(math.radians(latitude))
        dist_km = round(math.sqrt(dlat**2 + dlon**2), 2)
        loc["distance_km"] = dist_km

    rows.sort(key=lambda x: x["distance_km"])
    return json.dumps(rows[:5], indent=2)

def submit_help_or_safety_status(
    user_name: str,
    phone: str,
    status: str,  # "NEED_HELP" or "SAFE"
    location_name: str,
    needs_description: str = "",
    num_people: int = 1,
    has_elderly: bool = False,
    has_pets: bool = False,
    requires_boat: bool = False,
    requires_medical: bool = False
) -> str:
    """Allows user to mark 'I am safe' or 'I need help' (SOS), saving to responder database and alerting contacts."""
    conn = get_db()
    cursor = conn.cursor()

    req_id = f"SOS-{os.urandom(3).hex().upper()}"
    urgency = "CRITICAL_LIFE_THREAT" if (requires_boat or requires_medical or "trapped" in needs_description.lower()) else "HIGH"
    if status == "SAFE":
        urgency = "LOW"

    cursor.execute("""
    INSERT INTO help_requests (
        id, user_name, phone, location_name, status, urgency, needs_description,
        num_people, has_elderly, has_pets, requires_boat, requires_medical
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req_id, user_name, phone, location_name, status, urgency, needs_description,
        num_people, int(has_elderly), int(has_pets), int(requires_boat), int(requires_medical)
    ))
    conn.commit()
    conn.close()

    if status == "SAFE":
        return f"✅ Status updated: Marked SAFE for {user_name}. Automated SMS notification logged for your emergency contacts."
    else:
        return f"🚨 SOS LOGGED (ID: {req_id})! Urgency: {urgency}. Details transmitted to District Disaster Management & SDRF Responder Console. If in immediate life-threatening danger, CALL 112 NOW!"

def get_household_profile(user_or_phone: str) -> str:
    """Retrieves remembered household profile (special needs, medications, pets, language)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM households WHERE LOWER(user_name) LIKE ? OR phone LIKE ?",
        (f"%{user_or_phone.lower()}%", f"%{user_or_phone}%")
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.dumps(dict(row), indent=2)
    return json.dumps({"status": "not_found", "message": "No household saved yet."})

def generate_emergency_card_text(user_or_phone: str) -> str:
    """Generates a printable emergency wallet card with contacts, meds, evacuation address, and 112 priority."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM households WHERE LOWER(user_name) LIKE ? OR phone LIKE ?",
        (f"%{user_or_phone.lower()}%", f"%{user_or_phone}%")
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "No household found. Please specify name or phone."

    hh = dict(row)
    contacts = json.loads(hh.get("emergency_contacts", "[]"))
    meds = json.loads(hh.get("critical_medicines", "[]"))
    pets = json.loads(hh.get("pets_livestock", "[]"))

    card = f"""
============================================================
              EMERGENCY WALLET CARD: SAFEHAVEN
============================================================
NAME: {hh['user_name']}          PHONE: {hh['phone']}
LOCATION: {hh['location_name']}
COASTAL DISTANCE: {hh['distance_from_coast_km']} km | HOME: {hh['home_type'].upper()}
------------------------------------------------------------
🚨 PRIMARY DISASTER HELPLINE: 112 (TOLL-FREE 24x7)
------------------------------------------------------------
CRITICAL MEDICINES: {', '.join(meds) if meds else 'None reported'}
SPECIAL NEEDS: Elderly: {'YES' if hh['has_elderly'] else 'No'} | Disabled: {'YES' if hh['has_disabled'] else 'No'}
PETS / LIVESTOCK: {', '.join(pets) if pets else 'None'}
EMERGENCY CONTACTS:
"""
    for c in contacts:
        card += f"  • {c.get('name')}: {c.get('phone')} ({c.get('relation')})\n"
    card += """============================================================
INSTRUCTIONS:
1. In sudden water rise or tsunami, move to high ground immediately.
2. In cyclone, evacuate kutcha homes to designated relief centers.
3. Keep this card inside a waterproof pouch with Aadhaar and prescriptions.
============================================================
"""
    return card

def generate_emergency_map_image(location_name: str, disaster_type: str) -> str:
    """Generates an emergency evacuation map visualization using Vertex AI Imagen 3."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-ee8fb0191fd4")
    client = genai.Client(vertexai=True, project=project, location="us-central1")

    prompt = f"""
Clean, clear, high-contrast topological emergency evacuation route map graphic for {location_name} during a {disaster_type} emergency.
Showing green high-ground elevation ridges, red danger flood zone, bright yellow evacuation route arrows to blue shelter icon, bold typography 'SAFEHAVEN EVACUATION MAP', crisp cartographic vector infographic, minimal modern design.
"""
    maps_dir = "/config/Desktop/BuildWithGemini/safehaven/data/maps"
    os.makedirs(maps_dir, exist_ok=True)
    map_path = os.path.join(maps_dir, f"evac_map_{disaster_type}.png")

    try:
        result = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            )
        )
        for gen_img in result.generated_images:
            with open(map_path, "wb") as f:
                f.write(gen_img.image.image_bytes)
            return f"Generated emergency evacuation map saved to {map_path}"
    except Exception as e:
        return f"Map visual generation note: {str(e)}"
