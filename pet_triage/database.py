"""
Database Module
===============

SQLite database for users and pet profiles.
In production, replace with PostgreSQL or similar.

Tables:
- users: User accounts (email, password_hash, name)
- pet_profiles: Pet information linked to users
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "fuzzy_friend.db")


@contextmanager
def get_db():
    """Get database connection with automatic cleanup."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Pet profiles table (one per user for now, can extend to multiple pets)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                breed TEXT,
                age_years INTEGER,
                weight REAL,
                weight_unit TEXT DEFAULT 'kg',
                sex TEXT,
                spay_neuter_status TEXT,
                last_heat_cycle TEXT,
                vaccination_status TEXT,
                lifestyle TEXT,
                allergies TEXT,
                medical_history_flags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        print(f"Database initialized at {DB_PATH}")


# =============================================================================
# User Operations
# =============================================================================

def create_user(user_id: str, email: str, password_hash: str, name: str) -> bool:
    """Create a new user."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, name, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, email.lower(), password_hash, name, datetime.utcnow().isoformat()))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False  # Email already exists


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


# =============================================================================
# Pet Profile Operations
# =============================================================================

def create_or_update_pet_profile(
    user_id: str,
    name: str,
    species: str,
    breed: str = None,
    age_years: int = None,
    weight: float = None,
    weight_unit: str = "kg",
    sex: str = None,
    spay_neuter_status: str = None,
    last_heat_cycle: str = None,
    vaccination_status: str = None,
    lifestyle: str = None,
    allergies: str = None,
    medical_history_flags: List[str] = None
) -> Dict[str, Any]:
    """Create or update pet profile for a user."""
    
    # Convert list to comma-separated string
    history_str = ",".join(medical_history_flags) if medical_history_flags else None
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM pet_profiles WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        now = datetime.utcnow().isoformat()
        
        if existing:
            # Update existing profile
            cursor.execute("""
                UPDATE pet_profiles SET
                    name = ?, species = ?, breed = ?, age_years = ?,
                    weight = ?, weight_unit = ?, sex = ?, spay_neuter_status = ?,
                    last_heat_cycle = ?, vaccination_status = ?, lifestyle = ?,
                    allergies = ?, medical_history_flags = ?, updated_at = ?
                WHERE user_id = ?
            """, (name, species, breed, age_years, weight, weight_unit, sex,
                  spay_neuter_status, last_heat_cycle, vaccination_status, lifestyle,
                  allergies, history_str, now, user_id))
            profile_id = existing["id"]
        else:
            # Create new profile
            profile_id = f"pet_{user_id}_{int(datetime.utcnow().timestamp())}"
            cursor.execute("""
                INSERT INTO pet_profiles (
                    id, user_id, name, species, breed, age_years, weight, weight_unit,
                    sex, spay_neuter_status, last_heat_cycle, vaccination_status,
                    lifestyle, allergies, medical_history_flags, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (profile_id, user_id, name, species, breed, age_years, weight, weight_unit,
                  sex, spay_neuter_status, last_heat_cycle, vaccination_status, lifestyle,
                  allergies, history_str, now))
        
        conn.commit()
        
        return get_pet_profile(user_id)


def get_pet_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get pet profile for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pet_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            profile = dict(row)
            # Convert medical_history_flags back to list
            if profile.get("medical_history_flags"):
                profile["medical_history_flags"] = profile["medical_history_flags"].split(",")
            else:
                profile["medical_history_flags"] = []
            return profile
        return None


def delete_pet_profile(user_id: str) -> bool:
    """Delete pet profile for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pet_profiles WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0


# Initialize database on module import
init_db()
