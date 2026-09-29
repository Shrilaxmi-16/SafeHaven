import json
import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Ensure safehaven root is in sys.path
sys.path.insert(0, "/config/Desktop/BuildWithGemini/safehaven")

from app.database import get_db
from app.rules_engine import evaluate_emergency_protocol
from app.tools import (
    get_active_alerts,
    get_nearest_safe_locations,
    submit_help_or_safety_status,
    get_household_profile,
    generate_emergency_card_text,
    generate_emergency_map_image
)
from google import genai
from google.genai import types

app = FastAPI(title="SafeHaven Emergency Assistant")

class EvaluationRequest(BaseModel):
    disaster_type: str
    location_name: str
    household_id: Optional[str] = None
    language: str = "en"

class CheckinRequest(BaseModel):
    user_name: str
    phone: str
    status: str  # "SAFE" or "NEED_HELP"
    location_name: str
    needs_description: str = ""
    num_people: int = 1
    has_elderly: bool = False
    has_pets: bool = False
    requires_boat: bool = False
    requires_medical: bool = False

class ChatRequest(BaseModel):
    message: str
    household_id: Optional[str] = "HH-BLR-01"
    language: str = "en"

@app.get("/api/households")
def list_households():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM households ORDER BY user_name")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    for r in rows:
        r["critical_medicines"] = json.loads(r.get("critical_medicines", "[]")) if isinstance(r.get("critical_medicines"), str) else r.get("critical_medicines", [])
        r["pets_livestock"] = json.loads(r.get("pets_livestock", "[]")) if isinstance(r.get("pets_livestock"), str) else r.get("pets_livestock", [])
        r["emergency_contacts"] = json.loads(r.get("emergency_contacts", "[]")) if isinstance(r.get("emergency_contacts"), str) else r.get("emergency_contacts", [])
    return rows

@app.get("/api/alerts")
def list_alerts(region: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    if region:
        cursor.execute("SELECT * FROM alerts WHERE LOWER(region) LIKE ? ORDER BY issued_at DESC", (f"%{region.lower()}%",))
    else:
        cursor.execute("SELECT * FROM alerts ORDER BY issued_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/safe_locations")
def list_safe_locations(region: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    if region:
        cursor.execute("SELECT * FROM safe_locations WHERE LOWER(region) LIKE ? ORDER BY elevation_meters DESC", (f"%{region.lower()}%",))
    else:
        cursor.execute("SELECT * FROM safe_locations ORDER BY elevation_meters DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/help_requests")
def list_help_requests():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM help_requests ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/sea_trackers")
def list_sea_trackers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sea_trackers ORDER BY contacted_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/evaluate_risk")
def evaluate_risk(req: EvaluationRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch household if provided
    hh = {}
    if req.household_id:
        cursor.execute("SELECT * FROM households WHERE id = ?", (req.household_id,))
        row = cursor.fetchone()
        if row:
            hh = dict(row)
            
    # Fetch alert
    cursor.execute("SELECT * FROM alerts WHERE LOWER(disaster_type) LIKE ? LIMIT 1", (f"%{req.disaster_type.lower()}%",))
    alert_row = cursor.fetchone()
    alert_info = dict(alert_row) if alert_row else {}
    conn.close()

    result = evaluate_emergency_protocol(
        disaster_type=req.disaster_type,
        location_name=req.location_name,
        household=hh,
        alert_info=alert_info
    )
    result["household"] = hh
    result["alert"] = alert_info
    return result

@app.post("/api/checkin")
def submit_checkin(req: CheckinRequest):
    res = submit_help_or_safety_status(
        user_name=req.user_name,
        phone=req.phone,
        status=req.status,
        location_name=req.location_name,
        needs_description=req.needs_description,
        num_people=req.num_people,
        has_elderly=req.has_elderly,
        has_pets=req.has_pets,
        requires_boat=req.requires_boat,
        requires_medical=req.requires_medical
    )
    return {"message": res}

@app.get("/api/emergency_card")
def get_card(user: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM households WHERE LOWER(user_name) LIKE ? OR phone LIKE ?",
        (f"%{user.lower()}%", f"%{user}%")
    )
    row = cursor.fetchone()
    conn.close()

    hh = dict(row) if row else {}
    if hh:
        hh["critical_medicines"] = json.loads(hh.get("critical_medicines", "[]")) if isinstance(hh.get("critical_medicines"), str) else hh.get("critical_medicines", [])
        hh["pets_livestock"] = json.loads(hh.get("pets_livestock", "[]")) if isinstance(hh.get("pets_livestock"), str) else hh.get("pets_livestock", [])
        hh["emergency_contacts"] = json.loads(hh.get("emergency_contacts", "[]")) if isinstance(hh.get("emergency_contacts"), str) else hh.get("emergency_contacts", [])

    card_text = generate_emergency_card_text(user)
    return {"card_text": card_text, "household": hh}

@app.post("/api/chat")
def chat_with_agent(req: ChatRequest):
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-ee8fb0191fd4")
    client = genai.Client(vertexai=True, project=project, location="us-central1")

    # Fetch remembered household context
    conn = get_db()
    cursor = conn.cursor()
    hh_context = "No household profile loaded."
    if req.household_id:
        cursor.execute("SELECT * FROM households WHERE id = ?", (req.household_id,))
        r = cursor.fetchone()
        if r:
            hh = dict(r)
            hh_context = f"Household Profile for {hh['user_name']}: Location={hh['location_name']}, Coastal Dist={hh['distance_from_coast_km']}km, Home={hh['home_type']}, Elderly={hh['has_elderly']}, Infants={hh['has_infants']}, Disabled={hh['has_disabled']}, Meds={hh['critical_medicines']}, Pets={hh['pets_livestock']}, WorksAtSea={hh['works_at_sea']}."
    conn.close()

    lang_instruction = "Respond in English."
    if req.language == "kn":
        lang_instruction = "Respond in clear, simple Kannada (ಕನ್ನಡ) script with emergency instructions."
    elif req.language == "hi":
        lang_instruction = "Respond in clear, simple Hindi (हिन्दी) script with emergency instructions."

    prompt = f"""You are SafeHaven, a life-saving emergency assistant for India.
Always prioritize immediate safety. If life-threatening, urge calling 112.
{lang_instruction}

Household Memory Context:
{hh_context}

User Emergency Query:
{req.message}

Provide a short, direct, actionable emergency response (under 120 words). If evacuation is required, say so explicitly.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"🚨 EMERGENCY NOTICE: For life-threatening emergencies, call 112 immediately. (Offline response: {str(e)})"}

app.mount("/", StaticFiles(directory="/config/Desktop/BuildWithGemini/safehaven/frontend/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)
