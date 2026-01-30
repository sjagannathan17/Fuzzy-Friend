# shared/red_flags.py
"""
Red Flag Detection Engine - SINGLE SOURCE OF TRUTH

This module contains ALL red flag detection rules. Both:
- llm_setup.py (ER pre-check)
- tools.py (check_red_flags)

MUST import rules from this file to ensure consistency.

Red flags are symptoms/conditions that require immediate or urgent attention.
"""

from typing import Dict, Any, Tuple, Optional, List
from shared.constants import RiskLevel, SymptomCategory, normalize_risk_level


# =============================================================================
# IMMEDIATE ER RULES (Rule-based, skip LLM)
# =============================================================================

# Emergency gum colors indicate shock/hypoxemia/sepsis
EMERGENCY_GUM_COLORS = {
    "blue": ("Breathing Issues", "Cyanosis - severe hypoxemia"),
    "purple": ("Breathing Issues", "Cyanosis - severe hypoxemia"),
    "blue-purple": ("Breathing Issues", "Cyanosis - severe hypoxemia"),
    "pale": ("Injury & Bleeding", "Shock, anemia, blood loss"),
    "white": ("Injury & Bleeding", "Shock, anemia, blood loss"),
    "pale-white": ("Injury & Bleeding", "Shock, anemia, blood loss"),
    "grey": ("Concerning Behaviour Changes", "Poor perfusion, late shock"),
    "gray": ("Concerning Behaviour Changes", "Poor perfusion, late shock"),
    "muddy": ("Concerning Behaviour Changes", "Poor perfusion, late shock"),
    "brick red": ("Concerning Behaviour Changes", "Sepsis, heat stroke"),
    "brick-red": ("Concerning Behaviour Changes", "Sepsis, heat stroke"),
}


# Dangerous ingested substances with treatment windows
DANGEROUS_SUBSTANCES = [
    ("antifreeze", "ethylene glycol"),  # Dogs: <8-12 hrs; Cats: <2-3 hrs
    ("xylitol",),                         # Hypoglycemia within 30 min (dogs)
    ("chocolate",),                       # Decontamination effective up to 8 hrs
    ("lilies", "lily"),                   # Cats only - kidney failure 24-72 hrs
    ("grapes", "raisins"),               # Kidney failure 36-72 hrs
    ("rat poison", "rodenticide"),
    ("medication", "pills", "drugs"),
    ("cleaning chemicals", "bleach"),
    ("permethrin",),                      # Cats only - found in some dog flea products
]


# Deep-chested breeds at high risk for bloat (GDV)
BLOAT_RISK_BREEDS = [
    "great dane", "weimaraner", "st. bernard", "gordon setter", "irish setter",
    "standard poodle", "german shepherd", "doberman", "boxer", "rottweiler",
    "basset hound", "bloodhound", "akita", "irish wolfhound"
]


# Brachycephalic breeds with respiratory concerns
BRACHYCEPHALIC_BREEDS = [
    "bulldog", "french bulldog", "pug", "boston terrier", "pekingese",
    "shih tzu", "boxer", "cavalier king charles spaniel",
    "persian", "himalayan", "exotic shorthair"  # cats
]


def check_immediate_er(structured_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if immediate ER rules are triggered.
    
    This is the RULE-BASED engine that runs BEFORE LLM.
    If triggered, returns ER template directly (no LLM call needed).
    
    Args:
        structured_fields: Structured fields from UI including species, category
        
    Returns:
        {
            "is_er": bool,
            "risk_level": "ER" | None,
            "category": str | None,
            "red_flags": List[str],
            "reason": str | None
        }
    """
    result = {
        "is_er": False,
        "risk_level": None,
        "category": None,
        "red_flags": [],
        "reason": None
    }
    
    species = structured_fields.get("species", "").lower()
    category = structured_fields.get("category", "")
    
    # =========================================================================
    # CROSS-CATEGORY: Gum Color (check for all categories)
    # =========================================================================
    gum_color = structured_fields.get("gum_color", "").lower()
    if gum_color in EMERGENCY_GUM_COLORS:
        mapped_category, reason = EMERGENCY_GUM_COLORS[gum_color]
        result["is_er"] = True
        result["risk_level"] = RiskLevel.ER.value
        result["category"] = mapped_category
        result["red_flags"].append(f"Abnormal gum color: {gum_color}")
        result["reason"] = reason
        return result
    
    # CRT > 2.5 seconds indicates poor perfusion
    crt = structured_fields.get("capillary_refill_time", "")
    if crt in [">2.5 sec", ">2.5s", "absent", "prolonged"]:
        result["is_er"] = True
        result["risk_level"] = RiskLevel.ER.value
        result["category"] = "Concerning Behaviour Changes"
        result["red_flags"].append("Prolonged capillary refill time")
        result["reason"] = "Poor perfusion indicates shock"
        return result
    
    # =========================================================================
    # CROSS-CATEGORY: Distress Postures
    # =========================================================================
    if structured_fields.get("orthopnea_posture") == "Yes":
        result["is_er"] = True
        result["risk_level"] = RiskLevel.ER.value
        result["category"] = "Breathing Issues"
        result["red_flags"].append("Orthopnea posture (respiratory distress)")
        return result
    
    if structured_fields.get("elbows_abducted_neck_extended") == "Yes":
        result["is_er"] = True
        result["risk_level"] = RiskLevel.ER.value
        result["category"] = "Breathing Issues"
        result["red_flags"].append("Elbows abducted, neck extended (respiratory distress)")
        return result
    
    if structured_fields.get("praying_position") == "Yes":
        result["is_er"] = True
        result["risk_level"] = RiskLevel.ER.value
        result["category"] = "Stomach Upset"
        result["red_flags"].append("Praying position (severe abdominal pain)")
        return result
    
    # =========================================================================
    # BREATHING ISSUES
    # =========================================================================
    if category == "Breathing Issues":
        # Cat open-mouth breathing = ALWAYS emergency
        if species == "cat" and structured_fields.get("open_mouth_breathing") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Breathing Issues"
            result["red_flags"].append("Cat open-mouth breathing (cats NEVER normally pant)")
            result["reason"] = "Respiratory emergency"
            return result
        
        # Respiratory rate > 35-40
        resp_rate = structured_fields.get("respiratory_rate", "")
        if resp_rate in [">35-40", ">40", ">35"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Breathing Issues"
            result["red_flags"].append("Severely elevated respiratory rate")
            return result
        
        # Paradoxical breathing
        if structured_fields.get("paradoxical_breathing") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Breathing Issues"
            result["red_flags"].append("Paradoxical breathing pattern")
            return result
        
        # Stridor
        if structured_fields.get("stridor") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Breathing Issues"
            result["red_flags"].append("Inspiratory stridor (airway obstruction)")
            return result
        
        # Refuses to lie down
        if structured_fields.get("refuses_to_lie_down") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Breathing Issues"
            result["red_flags"].append("Unable to lie down (respiratory distress)")
            return result
    
    # =========================================================================
    # URINARY & GENITAL
    # =========================================================================
    if category == "Urinary & Genital":
        sex = structured_fields.get("sex", "").lower()
        
        # Male cat urinary blockage - life-threatening
        if species == "cat" and sex == "male":
            straining = structured_fields.get("straining_no_urine") == "Yes"
            hours = structured_fields.get("hours_since_urination", "")
            
            if straining:
                result["is_er"] = True
                result["risk_level"] = RiskLevel.ER.value
                result["category"] = "Urinary & Genital"
                result["red_flags"].append("Male cat straining to urinate")
                result["reason"] = "Urinary blockage can be fatal within 24-48 hours"
                return result
            
            if hours in ["12+", ">12h", "12+ h", "12-24h", ">24h"]:
                result["is_er"] = True
                result["risk_level"] = RiskLevel.ER.value
                result["category"] = "Urinary & Genital"
                result["red_flags"].append(f"Male cat no urination for {hours}")
                return result
            
            if structured_fields.get("crying_while_urinating") == "Yes":
                result["is_er"] = True
                result["risk_level"] = RiskLevel.ER.value
                result["category"] = "Urinary & Genital"
                result["red_flags"].append("Male cat crying while attempting to urinate")
                return result
        
        # Late signs of urinary blockage (any species)
        if structured_fields.get("vomiting_with_urinary_issues") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Urinary & Genital"
            result["red_flags"].append("Vomiting with urinary issues (toxin buildup)")
            return result
        
        if structured_fields.get("collapse") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Urinary & Genital"
            result["red_flags"].append("Collapse with urinary issues")
            return result
    
    # =========================================================================
    # SEIZURES / NEUROLOGICAL
    # =========================================================================
    if category == "Concerning Behaviour Changes":
        seizure_duration = structured_fields.get("seizure_duration", "")
        if seizure_duration in [">5 min", ">5min", ">3 min", ">3min"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Concerning Behaviour Changes"
            result["red_flags"].append(f"Seizure lasting {seizure_duration}")
            result["reason"] = "Status epilepticus - 25-38% mortality risk"
            return result
        
        if structured_fields.get("multiple_seizures_no_recovery") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Concerning Behaviour Changes"
            result["red_flags"].append("Multiple seizures without recovery")
            return result
        
        seizures_in_5min = structured_fields.get("seizures_within_5min", "")
        if seizures_in_5min in ["2+", "≥2", "2", "3+"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Concerning Behaviour Changes"
            result["red_flags"].append("Cluster seizures (2+ in 5 minutes)")
            return result
        
        seizure_count = structured_fields.get("seizure_count", "")
        if seizure_count in ["3+ in 24 hours", "3+", "≥3"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Concerning Behaviour Changes"
            result["red_flags"].append("3+ seizures in 24 hours")
            return result
        
        if structured_fields.get("collapse") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Concerning Behaviour Changes"
            result["red_flags"].append("Collapse")
            return result
        
        if structured_fields.get("unresponsive") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Concerning Behaviour Changes"
            result["red_flags"].append("Unresponsive")
            return result
    
    # =========================================================================
    # GDV / BLOAT
    # =========================================================================
    if category == "Stomach Upset":
        distended = structured_fields.get("abdomen_distended") == "Yes"
        retching = structured_fields.get("unproductive_retching") == "Yes"
        
        # Classic GDV presentation
        if distended and retching:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append("Distended abdomen + unproductive retching (GDV suspected)")
            result["reason"] = "GDV can be fatal within 1-2 hours"
            return result
        
        if structured_fields.get("drum_like_abdomen") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append("Drum-like abdomen (tympanic)")
            return result
        
        # High-risk breeds - lower threshold
        breed = structured_fields.get("breed", "").lower()
        is_bloat_risk_breed = any(b in breed for b in BLOAT_RISK_BREEDS)
        is_deep_chested = structured_fields.get("deep_chested_breed") == "Yes"
        is_large = structured_fields.get("large_breed_over_100lbs") == "Yes"
        
        if (is_bloat_risk_breed or is_deep_chested or is_large) and (distended or retching):
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append("High-risk breed with bloat symptoms")
            return result
        
        # Bloody vomit/diarrhea
        if structured_fields.get("bloody_vomit") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append("Bloody vomit")
            return result
        
        if structured_fields.get("bloody_diarrhea") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append("Bloody diarrhea")
            return result
        
        if structured_fields.get("cannot_keep_water_down") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append("Cannot keep water down")
            return result
    
    # =========================================================================
    # CAT ANOREXIA (Hepatic Lipidosis Risk)
    # =========================================================================
    if species == "cat":
        days_not_eating = structured_fields.get("days_not_eating", "")
        if days_not_eating in ["3+", "3-5", "5+", ">3 days", ">5 days"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Stomach Upset"
            result["red_flags"].append(f"Cat not eating for {days_not_eating} days")
            result["reason"] = "Hepatic lipidosis risk"
            return result
        
        if structured_fields.get("not_eating") == "Yes":
            if structured_fields.get("jaundice") == "Yes" or \
               structured_fields.get("yellow_gums") == "Yes" or \
               structured_fields.get("yellow_eyes") == "Yes":
                result["is_er"] = True
                result["risk_level"] = RiskLevel.ER.value
                result["category"] = "Stomach Upset"
                result["red_flags"].append("Cat not eating with jaundice")
                return result
    
    # =========================================================================
    # INJURY & BLEEDING
    # =========================================================================
    if category == "Injury & Bleeding":
        if structured_fields.get("heavy_bleeding") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append("Heavy/uncontrolled bleeding")
            return result
        
        if structured_fields.get("bleeding_stopped_after_pressure") == "No":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append("Bleeding not stopped after 5min pressure")
            return result
        
        wound_depth = structured_fields.get("wound_depth", "").lower()
        if wound_depth in ["deep (muscle visible)", "deep", "bone visible", "tendon visible"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append(f"Deep wound: {wound_depth}")
            return result
        
        wound_location = structured_fields.get("wound_location", "").lower()
        if wound_location in ["chest", "abdomen", "neck", "throat"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append(f"Wound to critical area: {wound_location}")
            return result
        
        if structured_fields.get("bite_wound") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append("Bite wound (always worse than they appear)")
            return result
        
        if structured_fields.get("puncture_wound") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append("Puncture wound (high infection risk)")
            return result
        
        if structured_fields.get("degloving_injury") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Injury & Bleeding"
            result["red_flags"].append("Degloving injury")
            return result
    
    # =========================================================================
    # EARS, EYES, MOUTH
    # =========================================================================
    if category == "Ears, Eyes, and Mouth":
        if structured_fields.get("eye_popped_out") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Ears, Eyes, and Mouth"
            result["red_flags"].append("Eye proptosis (eye popped out)")
            return result
        
        if structured_fields.get("sudden_eye_bulging") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Ears, Eyes, and Mouth"
            result["red_flags"].append("Sudden eye bulging (acute glaucoma)")
            result["reason"] = "Permanent blindness within hours"
            return result
        
        if structured_fields.get("corneal_perforation") == "Yes" or \
           structured_fields.get("eye_rupture") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Ears, Eyes, and Mouth"
            result["red_flags"].append("Eye perforation/rupture")
            return result
        
        if structured_fields.get("severe_eye_trauma") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Ears, Eyes, and Mouth"
            result["red_flags"].append("Severe eye trauma")
            return result
    
    # =========================================================================
    # TOXIC INGESTION
    # =========================================================================
    if category == "Toxic Ingestion & Poisoning":
        eaten = structured_fields.get("what_was_eaten", [])
        
        # Normalize to list
        if isinstance(eaten, str):
            eaten = [eaten]
        
        for item in eaten:
            item_lower = item.lower()
            for substance_group in DANGEROUS_SUBSTANCES:
                if any(s in item_lower for s in substance_group):
                    result["is_er"] = True
                    result["risk_level"] = RiskLevel.ER.value
                    result["category"] = "Toxic Ingestion & Poisoning"
                    result["red_flags"].append(f"Ingestion of {item}")
                    return result
        
        # Permethrin exposure in cats
        if species == "cat" and structured_fields.get("permethrin_exposure") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Toxic Ingestion & Poisoning"
            result["red_flags"].append("Permethrin exposure (toxic to cats)")
            return result
        
        consciousness = structured_fields.get("consciousness", "")
        if consciousness in ["unconscious", "seizing"]:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Toxic Ingestion & Poisoning"
            result["red_flags"].append(f"Post-ingestion: {consciousness}")
            return result
        
        if structured_fields.get("caustic_substance") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Toxic Ingestion & Poisoning"
            result["red_flags"].append("Caustic substance ingestion (DO NOT induce vomiting)")
            return result
    
    # =========================================================================
    # ALLERGIC REACTION
    # =========================================================================
    if category == "Itching & Skin Issues":
        facial_swelling = structured_fields.get("facial_swelling") == "Yes"
        breathing_change = structured_fields.get("breathing_changes_with_swelling") == "Yes"
        
        if facial_swelling and breathing_change:
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Itching & Skin Issues"
            result["red_flags"].append("Facial swelling + breathing changes (anaphylaxis risk)")
            return result
        
        if structured_fields.get("throat_swelling") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Itching & Skin Issues"
            result["red_flags"].append("Throat swelling")
            return result
        
        if structured_fields.get("rapid_swelling") == "Yes":
            result["is_er"] = True
            result["risk_level"] = RiskLevel.ER.value
            result["category"] = "Itching & Skin Issues"
            result["red_flags"].append("Rapid swelling progression")
            return result
    
    # No ER rules triggered
    return result


# =============================================================================
# TEXT-BASED RED FLAG DETECTION (Fallback)
# =============================================================================

CRITICAL_KEYWORDS = [
    "not breathing", "stopped breathing", "can't breathe", "choking",
    "unconscious", "collapsed", "seizure", "convulsion",
    "severe bleeding", "hit by car", "trauma", "poisoning",
    "ate poison", "ate chocolate", "ate xylitol", "antifreeze",
    "bloated stomach", "trying to vomit but can't", "distended abdomen",
    "blue gums", "pale gums", "white gums",
    "not moving", "paralyzed", "can't walk suddenly",
    # Cat-specific breathing emergencies (cats should NEVER pant/open-mouth breathe)
    "open mouth breathing", "breathing with mouth open", "panting cat",
    "cat panting", "cat breathing with mouth open", "mouth open breathing"
]

URGENT_KEYWORDS = [
    "vomiting blood", "bloody diarrhea", "blood in stool", "blood in urine",
    "difficulty breathing", "labored breathing", "heavy panting",
    "eye injury", "eye swollen shut", "eye bleeding",
    "broken bone", "limping severely", "can't put weight on leg",
    "swallowed object", "ate bone", "ate toy",
    "not eating for 2 days", "not drinking", "very lethargic",
    "high fever", "extremely hot", "shaking uncontrollably",
    "snake bite", "bee sting swelling", "allergic reaction"
]

MODERATE_KEYWORDS = [
    "vomiting", "diarrhea", "not eating", "loss of appetite",
    "limping", "favoring leg", "pain when touched",
    "scratching a lot", "hot spots", "hair loss", "skin rash",
    "ear infection", "shaking head", "bad smell from ears",
    "eye discharge", "red eyes", "squinting",
    "coughing", "sneezing a lot", "runny nose",
    "drinking more than usual", "urinating more",
    "lump", "bump", "swelling"
]


def check_text_for_red_flags(
    text: str,
    species: str = None,
    breed: str = None
) -> Dict[str, Any]:
    """
    Check free text description for red flag keywords.
    
    This is a FALLBACK method when structured fields don't trigger ER.
    
    Args:
        text: User's symptom description
        species: Pet species (dog/cat)
        breed: Pet breed (for breed-specific alerts)
        
    Returns:
        {
            "severity": "CRITICAL" | "URGENT" | "MODERATE" | "LOW",
            "risk_level": RiskLevel,
            "matched_symptoms": List[str],
            "breed_alerts": List[dict],
            "recommendation": str
        }
    """
    if not text:
        return {
            "severity": "LOW",
            "risk_level": RiskLevel.MONITOR,
            "matched_symptoms": [],
            "breed_alerts": [],
            "recommendation": "Monitor your pet. If symptoms persist or worsen, consult a veterinarian."
        }
    
    text_lower = text.lower()
    matched = []
    breed_alerts = []
    
    # ==========================================================================
    # SPECIES-SPECIFIC CRITICAL CHECKS (before generic keywords)
    # ==========================================================================
    
    # CAT: Any open-mouth breathing / panting is ALWAYS emergency
    # Cats should NEVER normally pant or breathe with mouth open
    if species and species.lower() == "cat":
        cat_breathing_keywords = [
            "mouth open", "open mouth", "panting", "breathing through mouth",
            "breathing with mouth", "heavy breathing", "labored breathing"
        ]
        for keyword in cat_breathing_keywords:
            if keyword in text_lower:
                matched.append(f"Cat {keyword} (cats should NEVER pant normally)")
                return {
                    "severity": "CRITICAL",
                    "risk_level": RiskLevel.ER,
                    "matched_symptoms": matched,
                    "breed_alerts": [],
                    "recommendation": "EMERGENCY - Cat open-mouth breathing is ALWAYS an emergency! Seek immediate veterinary care!"
                }
    
    # Check CRITICAL keywords
    for keyword in CRITICAL_KEYWORDS:
        if keyword in text_lower:
            matched.append(keyword)
    
    if matched:
        return {
            "severity": "CRITICAL",
            "risk_level": RiskLevel.ER,
            "matched_symptoms": matched,
            "breed_alerts": breed_alerts,
            "recommendation": "EMERGENCY - Seek immediate veterinary care! Call emergency vet now."
        }
    
    # Check URGENT keywords
    for keyword in URGENT_KEYWORDS:
        if keyword in text_lower:
            matched.append(keyword)
    
    if matched:
        return {
            "severity": "URGENT",
            "risk_level": RiskLevel.TODAY,
            "matched_symptoms": matched,
            "breed_alerts": breed_alerts,
            "recommendation": "URGENT - Contact your veterinarian immediately or visit an emergency clinic."
        }
    
    # Check MODERATE keywords
    for keyword in MODERATE_KEYWORDS:
        if keyword in text_lower:
            matched.append(keyword)
    
    if matched:
        severity = "MODERATE"
        risk_level = RiskLevel.SOON
        recommendation = "Schedule a veterinary appointment soon (within 24-48 hours)."
    else:
        severity = "LOW"
        risk_level = RiskLevel.MONITOR
        recommendation = "Monitor your pet. If symptoms persist or worsen, consult a veterinarian."
    
    # Breed-specific alerts
    if breed:
        breed_lower = breed.lower()
        
        # Bloat risk
        if any(b in breed_lower for b in BLOAT_RISK_BREEDS):
            bloat_keywords = ["bloat", "stomach", "abdomen", "distended", "restless", 
                           "trying to vomit", "pacing", "drooling"]
            if any(k in text_lower for k in bloat_keywords):
                breed_alerts.append({
                    "alert": "BLOAT RISK",
                    "message": f"{breed} is at high risk for bloat (GDV). Seek IMMEDIATE emergency care!"
                })
                severity = "CRITICAL"
                risk_level = RiskLevel.ER
        
        # Brachycephalic
        if any(b in breed_lower for b in BRACHYCEPHALIC_BREEDS):
            breathing_keywords = ["breathing", "panting", "snoring", "wheezing", "hot", "overheated"]
            if any(k in text_lower for k in breathing_keywords):
                breed_alerts.append({
                    "alert": "BRACHYCEPHALIC CONCERN",
                    "message": f"{breed} is flat-faced. Breathing difficulties can escalate quickly."
                })
                if severity == "LOW":
                    severity = "MODERATE"
                    risk_level = RiskLevel.SOON
    
    return {
        "severity": severity,
        "risk_level": risk_level,
        "matched_symptoms": matched,
        "breed_alerts": breed_alerts,
        "recommendation": recommendation
    }


# =============================================================================
# COMBINED RED FLAG CHECK
# =============================================================================

def check_red_flags(
    structured_fields: Dict[str, Any],
    user_text: str = "",
    species: str = None,
    breed: str = None
) -> Dict[str, Any]:
    """
    Combined red flag check - structured fields FIRST, then text fallback.
    
    Args:
        structured_fields: Structured fields from UI
        user_text: User's free text description
        species: Pet species (can also be in structured_fields)
        breed: Pet breed (can also be in structured_fields)
        
    Returns:
        Unified result with is_er, risk_level, red_flags, etc.
    """
    # Merge species/breed into structured_fields if provided separately
    fields = structured_fields.copy()
    if species and "species" not in fields:
        fields["species"] = species
    if breed and "breed" not in fields:
        fields["breed"] = breed
    
    # Check structured fields first (more reliable)
    er_result = check_immediate_er(fields)
    
    if er_result["is_er"]:
        return {
            "is_er": True,
            "risk_level": RiskLevel.ER,
            "severity": "CRITICAL",
            "red_flags": er_result["red_flags"],
            "category": er_result["category"],
            "reason": er_result["reason"],
            "recommendation": "EMERGENCY - Seek immediate veterinary care!"
        }
    
    # Fallback to text check
    text_result = check_text_for_red_flags(
        user_text,
        species=fields.get("species"),
        breed=fields.get("breed")
    )
    
    return {
        "is_er": text_result["risk_level"] == RiskLevel.ER,
        "risk_level": text_result["risk_level"],
        "severity": text_result["severity"],
        "red_flags": text_result["matched_symptoms"],
        "breed_alerts": text_result["breed_alerts"],
        "recommendation": text_result["recommendation"]
    }
