import json
from typing import Dict, Any, List

def evaluate_emergency_protocol(
    disaster_type: str,
    location_name: str,
    household: Dict[str, Any],
    alert_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates key disaster protocols deterministically for life-saving triage:
    1. Urban Flooding with insulin & pets
    2. Heatwave with elderly living alone
    3. Cyclone with countdown & time-staged checklist
    4. Storm Surge (move inland/elevated, NOT just upstairs)
    5. Tsunami (immediate run to high ground, skip pleasantries)
    6. Fisher at sea (return to harbor & boat status)
    7. Life-threatening emergency: 112 priority notice
    """
    disaster_type = disaster_type.lower()
    needs_evacuation = False
    urgency_level = "MODERATE"
    headline = ""
    action_directive = ""
    checklist = []
    special_advisories = []
    
    # Check special needs
    has_elderly = bool(household.get("has_elderly"))
    has_infants = bool(household.get("has_infants"))
    has_disabled = bool(household.get("has_disabled"))
    meds = json.loads(household.get("critical_medicines", "[]")) if isinstance(household.get("critical_medicines"), str) else household.get("critical_medicines", [])
    pets = json.loads(household.get("pets_livestock", "[]")) if isinstance(household.get("pets_livestock"), str) else household.get("pets_livestock", [])
    home_type = household.get("home_type", "pucca")
    dist_coast = float(household.get("distance_from_coast_km", 0))
    works_sea = bool(household.get("works_at_sea"))

    # Protocol 5: TSUNAMI
    if "tsunami" in disaster_type or "sea recession" in alert_info.get("headline", "").lower():
        urgency_level = "CRITICAL_IMMEDIATE_ACTION"
        needs_evacuation = True
        headline = "🚨 TSUNAMI ALERT — EVACUATE TO HIGH GROUND NOW! DO NOT DELAY!"
        action_directive = "MOVE INLAND & UPWARD IMMEDIATELY. Reach an elevation of at least 15 meters or move 2 km inland. DO NOT STAY ON GROUND OR FIRST FLOORS. Do not wait to gather belongings. Keep moving to high ground!"
        checklist = [
            "🏃 Run immediately inland towards higher elevation (Kunjibettu/Manipal Ridge)",
            "🚫 DO NOT go near the beach to watch the receding sea",
            "🚫 DO NOT stay in ground or first-floor structures",
            "📞 If unable to move due to injury or disability, shout for local assistance or call 112"
        ]
        return {
            "evacuate": True,
            "urgency": urgency_level,
            "headline": headline,
            "directive": action_directive,
            "checklist": checklist,
            "advisories": ["Immediate threat to life. Move to St. Mary's Elevated Ridge or Manipal High Ground."],
            "call_112_priority": True
        }

    # Protocol 4: STORM SURGE
    if "storm_surge" in disaster_type or "surge" in disaster_type or "high_waves" in disaster_type:
        surge_height = alert_info.get("surge_height_m", 3.5)
        needs_evacuation = True
        urgency_level = "HIGH"
        headline = f"🌊 STORM SURGE WARNING: {surge_height}m Sea Inundation Expected"
        action_directive = f"CRITICAL: Move INLAND to elevated shelters above surge level. DO NOT JUST MOVE UPSTAIRS. Storm surge waves carry destructive force that can undermine building foundations. Relocate to elevated ground immediately."
        checklist = [
            "Move at least 1.5 km inland or to relief shelters above 15m elevation",
            "Secure boats and fishing equipment well above the high tide line",
            "Carry waterproof bags with identification, land records, and emergency cash",
            "Pack 48-hour dry rations, bottled water, and emergency torch"
        ]
        if works_sea:
            special_advisories.append("⚠️ SEAFARER ALERT: Complete suspension of all fishing and boat operations. Ensure vessels are anchored in protected inner docks.")
        return {
            "evacuate": True,
            "urgency": urgency_level,
            "headline": headline,
            "directive": action_directive,
            "checklist": checklist,
            "advisories": special_advisories,
            "call_112_priority": False
        }

    # Protocol 1: URBAN FLOODING (Ground floor, elderly insulin, pets)
    if "flood" in disaster_type:
        is_ground_floor = "ground" in home_type.lower()
        has_insulin = any("insulin" in str(m).lower() for m in meds)
        needs_evacuation = is_ground_floor or has_elderly or has_disabled
        urgency_level = "HIGH" if (is_ground_floor and (has_elderly or has_insulin)) else "MODERATE"
        
        headline = "🌊 URBAN FLOOD ALERT: Rising Water Threat"
        action_directive = "EVACUATE GROUND FLOORS IMMEDIATELY to designated pet-friendly and accessible shelters, or move to upper floors if rescue boat is requested."
        
        checklist = [
            "⚡ Turn OFF the main electrical breaker and gas cylinder valve before water reaches sockets",
            "🧊 Keep Insulin in waterproof insulated cold pack / thermos with ice blocks",
            "🐕 Leash pet dog and carry dry pet food and vaccination records",
            "📄 Pack waterproof pouch: Aadhaar, prescriptions, deeds, cash, and power banks",
            "🦽 Coordinate wheelchair / accessible transfer with neighborhood responders or NDRF/SDRF"
        ]
        
        if has_insulin:
            special_advisories.append("🧊 CRITICAL MEDICINE: Insulin must not freeze or overheat. Shelters with medical cold chain are prioritized.")
        if pets:
            special_advisories.append("🐾 PET ADVISORY: BBMP Community Relief Center (HSR) and Malpe School have designated pet holding areas.")
        
        return {
            "evacuate": needs_evacuation,
            "urgency": urgency_level,
            "headline": headline,
            "directive": action_directive,
            "checklist": checklist,
            "advisories": special_advisories,
            "call_112_priority": is_ground_floor and has_elderly
        }

    # Protocol 2: HEATWAVE (Elderly living alone)
    if "heatwave" in disaster_type:
        needs_evacuation = False
        urgency_level = "HIGH" if has_elderly else "MODERATE"
        headline = "☀️ SEVERE HEATWAVE ALERT (Peak 40.5°C): High Thermal Stress"
        action_directive = "STAY INDOORS in the coolest room between 11:00 AM and 4:30 PM. Keep hydrated and monitor body temperature."
        
        checklist = [
            "💧 Drink plenty of fluids (water, tender coconut, buttermilk, ORS) even if not thirsty",
            "🪟 Keep curtains, blinds, and windows closed during peak sunlight; open for cross-ventilation after sunset",
            "👕 Wear loose, lightweight, light-colored cotton clothing",
            "🧊 Keep a damp washcloth or ice pack on neck and forehead to reduce heat strain",
            "📞 Maintain daily check-in calls with family or local welfare volunteer"
        ]
        
        special_advisories.append("🚩 HEATSTROKE DANGER SIGNS: High body temperature (>103°F), confusion, dizziness, rapid pulse, lack of sweating. If seen, cool with wet cloth and CALL 112 IMMEDIATELY.")
        if has_elderly:
            special_advisories.append("👵 ELDERLY LIVING ALONE: Avoid cooking over open flame during peak noon hours. Request neighbors to check twice daily.")
            
        return {
            "evacuate": False,
            "urgency": urgency_level,
            "headline": headline,
            "directive": action_directive,
            "checklist": checklist,
            "advisories": special_advisories,
            "call_112_priority": False
        }

    # Protocol 3: CYCLONE APPROACHING COAST
    if "cyclone" in disaster_type:
        eta = alert_info.get("landfall_eta_hours", 14.0)
        is_weak_home = "kutcha" in home_type.lower() or "semi" in home_type.lower()
        is_coastal = dist_coast <= 5.0
        needs_evacuation = is_weak_home or is_coastal
        
        urgency_level = "HIGH" if eta <= 12 else "MODERATE"
        headline = f"🌀 CYCLONE WARNING: Landfall Expected in ~{int(eta)} Hours"
        action_directive = f"STAGED TIMELINE: {'EVACUATE IMMEDIATELY to Cyclone Relief Center (weak house / coastal zone)' if needs_evacuation else 'SHELTER IN PLACE in reinforced pucca structure'}."
        
        checklist = [
            f"⏰ Stage 1 (T minus {int(eta)}h to 10h): Board windows, tie down loose outdoor objects, clear drains",
            "⏰ Stage 2 (T minus 10h to 4h): Full evacuation of coastal/kutcha structures to Cyclone Relief Centers",
            "⏰ Stage 3 (T minus 4h to Landfall): Complete shelter in place. Never venture out during the eye of the storm (false calm)",
            "📻 Charge all emergency lights, power banks, and keep battery radio tuned to All India Radio / DD"
        ]
        
        if works_sea:
            special_advisories.append("⚓ HARBOR PROTOCOL: All fishing boats must return to harbor immediately and be winched onto slipways.")
            
        return {
            "evacuate": needs_evacuation,
            "urgency": urgency_level,
            "headline": headline,
            "directive": action_directive,
            "checklist": checklist,
            "advisories": special_advisories,
            "call_112_priority": False
        }

    # Default Fallback
    return {
        "evacuate": False,
        "urgency": "MODERATE",
        "headline": f"⚠️ Weather Alert: {disaster_type.title()}",
        "directive": "Stay alert and monitor local official advisories. Call 112 for emergencies.",
        "checklist": ["Keep emergency kit ready", "Charge phone and battery banks", "Follow district administration guidelines"],
        "advisories": [],
        "call_112_priority": False
    }
