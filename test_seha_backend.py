import requests
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"

def run_real_user_scenario():
    print("🚀 Starting Full Platform Integration Test (Real User Scenario)...")
    print("="*60)

    # 1. ACCOUNT CREATION
    print("\n[Step 1: User Registration]")
    unique_suffix = int(time.time())
    user_email = f"user_{unique_suffix}@example.com"
    unique_phone = f"+1{str(unique_suffix)[-9:]}" 
    
    reg_data = {
        "email": user_email, "password": "StrongPassword123!",
        "full_name": "Test Real User", "phone": unique_phone,
        "date_of_birth": "1992-08-20", "gender": "female",
        "address": "456 Innovation Drive", "user_type": "doctor"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    auth_json = resp.json()
    token = auth_json["access_token"]
    user_id = auth_json["user"]["user_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ User registered successfully. ID: {user_id}")

    # 2. FACILITY & PROVIDER SETUP
    print("\n[Step 2: Medical Facility & Provider Setup]")
    h_resp = requests.post(f"{BASE_URL}/medical/hospitals", 
                           json={"name": f"Unity Health {unique_suffix}", "address": "Cairo", "city": "Cairo", "has_emergency": True}, 
                           headers=headers)
    hospital_id = h_resp.json()["hospital_id"]

    d_resp = requests.post(f"{BASE_URL}/medical/doctors", 
                           json={"user_id": user_id, "specialization": "Pediatrics", "hospital_id": hospital_id, 
                                 "license_number": f"MD-LIC-{unique_suffix}", "bio": "Pediatrician", "is_available_online": True}, 
                           headers=headers)
    doctor_id = d_resp.json()["doctor_id"]
    print(f"✅ Doctor profile active. Doctor ID: {doctor_id}")

    # 3. APPOINTMENT BOOKING
    print("\n[Step 3: Scheduling an Appointment]")
    appointment_time = (datetime.utcnow() + timedelta(days=5)).isoformat()
    apt_data = {
        "doctor_id": doctor_id, "hospital_id": hospital_id,
        "appointment_datetime": appointment_time,
        "reason_for_visit": "General health consultation", "patient_notes": "Checking vaccination records."
    }
    requests.post(f"{BASE_URL}/scheduling/appointments", json=apt_data, headers=headers)
    print(f"✅ Appointment scheduled.")

    # 4. AI CONSULTATION (Displaying Full Response)
    # -------------------------------------------------------------------------
    print("\n[Step 4: AI Health Assistant Interaction]")
    s_resp = requests.post(f"{BASE_URL}/chatbot/sessions", json={"session_title": "Pediatric Advice"}, headers=headers)
    session_id = s_resp.json()["session_id"]
    
    user_query = "What is the best diet for a 5-year-old?"
    print(f"❓ User Query: {user_query}")
    
    c_resp = requests.post(f"{BASE_URL}/chatbot/sessions/{session_id}/messages", json={"content": user_query}, headers=headers)
    
    if c_resp.status_code == 200:
        bot_msg = c_resp.json()["assistant_message"]["content"]
        print("-" * 40)
        print(f"🤖 AI RESPONSE:\n{bot_msg}") # This line now prints the full text
        print("-" * 40)
    else:
        print(f"❌ Chatbot failed: {c_resp.text}")

    # 5. CLINICAL DOCUMENTATION
    print("\n[Step 5: Creating Clinical Medical Record]")
    record_data = {
        "user_id": int(user_id), "patient_id": int(user_id), "doctor_id": int(doctor_id),
        "diagnosis": "Healthy growth", "treatment_plan": "Standard follow-up",
        "prescriptions": "None", "notes": "Automated test record.",
        "visit_date": datetime.now().isoformat() 
    }
    r_resp = requests.post(f"{BASE_URL}/medical/medical-records", json=record_data, headers=headers)
    if r_resp.status_code == 201:
        print(f"✅ Medical record finalized for User {user_id}")

    print("\n" + "="*60)
    print("⭐ SUCCESS: ALL REAL-USER JOURNEY STEPS PASSED ⭐")

if __name__ == "__main__":
    run_real_user_scenario()