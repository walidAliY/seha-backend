"""
Script to populate the healthcare database with realistic Egyptian data
This will clear existing data and create:
- Hospitals across major Egyptian cities
- Doctors with Egyptian names and specializations
- Patient accounts
- Medical records
- Appointments
- CSV file with all account credentials
"""

import requests
import random
import csv
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker with Arabic locale for Egyptian names
fake = Faker(['ar_EG', 'en_US'])

BASE_URL = "http://localhost:8000"

# Egyptian Cities and their governorates
EGYPTIAN_CITIES = [
    "Cairo", "Giza", "Alexandria", "Port Said", "Suez",
    "Luxor", "Aswan", "Asyut", "Beheira", "Beni Suef",
    "Dakahlia", "Damietta", "Faiyum", "Gharbia", "Ismailia",
    "Kafr El Sheikh", "Matruh", "Minya", "Monufia", "New Valley",
    "North Sinai", "Qalyubia", "Qena", "Red Sea", "Sharqia",
    "Sohag", "South Sinai", "Tanta", "Mansoura", "Zagazig"
]

# Egyptian Hospital Names
EGYPTIAN_HOSPITALS = [
    {"name": "Cairo University Hospital", "city": "Cairo", "emergency": True},
    {"name": "Ain Shams University Hospital", "city": "Cairo", "emergency": True},
    {"name": "Kasr Al Ainy Hospital", "city": "Cairo", "emergency": True},
    {"name": "El Galaa Teaching Hospital", "city": "Cairo", "emergency": True},
    {"name": "Alexandria University Hospital", "city": "Alexandria", "emergency": True},
    {"name": "El Raml Hospital", "city": "Alexandria", "emergency": True},
    {"name": "Mansoura University Hospital", "city": "Mansoura", "emergency": True},
    {"name": "Assiut University Hospital", "city": "Asyut", "emergency": True},
    {"name": "Tanta University Hospital", "city": "Tanta", "emergency": True},
    {"name": "Zagazig University Hospital", "city": "Zagazig", "emergency": True},
    {"name": "Suez Canal University Hospital", "city": "Ismailia", "emergency": True},
    {"name": "Benha University Hospital", "city": "Qalyubia", "emergency": True},
    {"name": "Minya University Hospital", "city": "Minya", "emergency": True},
    {"name": "Sohag University Hospital", "city": "Sohag", "emergency": True},
    {"name": "57357 Children's Cancer Hospital", "city": "Cairo", "emergency": True},
    {"name": "Dar Al Fouad Hospital", "city": "Giza", "emergency": True},
    {"name": "Saudi German Hospital Cairo", "city": "Cairo", "emergency": True},
    {"name": "Cleopatra Hospital", "city": "Alexandria", "emergency": True},
    {"name": "As-Salam International Hospital", "city": "Cairo", "emergency": True},
    {"name": "Anglo American Hospital", "city": "Cairo", "emergency": False},
    {"name": "Nile Badrawi Hospital", "city": "Cairo", "emergency": False},
    {"name": "Maghrabi Eye Hospital", "city": "Cairo", "emergency": False},
    {"name": "Al Safa Hospital", "city": "Giza", "emergency": False},
    {"name": "El Nozha International Hospital", "city": "Cairo", "emergency": False},
    {"name": "Maadi Military Hospital", "city": "Cairo", "emergency": True},
]

# Egyptian Doctor Names (First + Last)
EGYPTIAN_FIRST_NAMES_MALE = [
    "محمد", "أحمد", "محمود", "علي", "حسن", "عمر", "خالد", "يوسف", "كريم", "طارق",
    "Mohamed", "Ahmed", "Mahmoud", "Ali", "Hassan", "Omar", "Khaled", "Youssef", "Karim", "Tarek"
]

EGYPTIAN_FIRST_NAMES_FEMALE = [
    "فاطمة", "عائشة", "نور", "ياسمين", "مريم", "سارة", "هدى", "دينا", "منى", "سلمى",
    "Fatma", "Aisha", "Nour", "Yasmine", "Maryam", "Sara", "Hoda", "Dina", "Mona", "Salma"
]

EGYPTIAN_LAST_NAMES = [
    "محمد", "أحمد", "علي", "حسن", "إبراهيم", "عبد الله", "السيد", "عثمان", "الشريف",
    "Mohamed", "Ahmed", "Ali", "Hassan", "Ibrahim", "Abdullah", "El Sayed", "Othman", "El Sherif",
    "Abdel Rahman", "Abdelaziz", "El Masry", "El Guindy", "Khattab", "Gaber", "Sadek"
]

# Medical Specializations
SPECIALIZATIONS = [
    "General Practitioner",
    "Cardiologist",
    "Dermatologist",
    "Orthopedic Surgeon",
    "Neurologist",
    "Pediatrician",
    "Gynecologist",
    "Psychiatrist",
    "Ophthalmologist",
    "ENT Specialist",
    "Gastroenterologist",
    "Endocrinologist",
    "Urologist",
    "Oncologist",
    "Radiologist",
    "Anesthesiologist",
    "Nephrologist",
    "Pulmonologist",
    "Rheumatologist",
    "Dentist"
]

# Common Egyptian diagnoses and prescriptions
DIAGNOSES = [
    "Common Cold", "Flu", "Hypertension", "Diabetes Type 2", "Asthma",
    "Allergic Rhinitis", "Gastritis", "Migraine", "Back Pain", "Arthritis",
    "Sinusitis", "Bronchitis", "Urinary Tract Infection", "Vitamin D Deficiency",
    "Anemia", "High Cholesterol", "Thyroid Disorder", "Skin Infection",
    "Eye Infection", "Dental Cavity"
]

PRESCRIPTIONS = [
    "Paracetamol 500mg - 3 times daily",
    "Amoxicillin 500mg - twice daily for 7 days",
    "Omeprazole 20mg - once daily before breakfast",
    "Metformin 500mg - twice daily with meals",
    "Lisinopril 10mg - once daily",
    "Aspirin 75mg - once daily",
    "Vitamin D 1000 IU - once daily",
    "Iron supplements - once daily",
    "Antihistamine - once at night",
    "Pain relief gel - apply as needed"
]

def create_token_headers(token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def register_user(email, password, full_name, user_type="patient"):
    """Register a new user"""
    data = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "phone": f"+20{random.randint(1000000000, 1999999999)}",
        "date_of_birth": str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
        "gender": random.choice(["Male", "Female"]),
        "address": f"{random.randint(1, 100)} {random.choice(['Street', 'Avenue', 'Road'])}, {random.choice(EGYPTIAN_CITIES)}, Egypt",
        "user_type": user_type
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to register {email}: {response.text}")
            return None
    except Exception as e:
        print(f"Error registering {email}: {e}")
        return None

def create_hospital(token, hospital_data):
    """Create a hospital"""
    address = f"{random.randint(1, 500)} {random.choice(['St', 'Ave', 'Rd'])}, {hospital_data['city']}, Egypt"
    data = {
        "name": hospital_data["name"],
        "address": address,
        "city": hospital_data["city"],
        "phone": f"+20{random.randint(2, 3)}{random.randint(10000000, 99999999)}",
        "has_emergency": hospital_data["emergency"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/hospitals",
            json=data,
            headers=create_token_headers(token)
        )
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        print(f"Error creating hospital: {e}")
        return None

def create_doctor_profile(token, user_id, hospital_id, specialization):
    """Create a doctor profile"""
    qualifications = random.choice([
        "MD, MBBS, Cairo University",
        "MD, Fellowship in Specialization, Ain Shams University",
        "MBBS, Masters Degree, Alexandria University",
        "MD, Board Certified, Kasr Al Ainy",
        "MBBS, PhD, Assiut University"
    ])
    
    data = {
        "user_id": user_id,
        "specialization": specialization,
        "license_number": f"EG-{random.randint(100000, 999999)}",
        "hospital_id": hospital_id,
        "qualifications": qualifications,
        "availability_schedule": "Saturday-Thursday: 10:00 AM - 4:00 PM",
        "is_available_online": random.choice([True, False])
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/doctors",
            json=data,
            headers=create_token_headers(token)
        )
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to create doctor profile. Status: {response.status_code}, Response: {response.text}")
        return None
    except Exception as e:
        print(f"Error creating doctor profile: {e}")
        return None

def create_medical_record(doctor_token, patient_user_id, doctor_id):
    """Create a medical record - doctors create records for patients"""
    data = {
        "diagnosis": random.choice(DIAGNOSES),
        "prescription": random.choice(PRESCRIPTIONS),
        "tests_ordered": random.choice([
            "Complete Blood Count (CBC)",
            "Blood Sugar Test",
            "Chest X-Ray",
            "ECG",
            "Urine Analysis",
            "Lipid Profile"
        ]),
        "doctor_notes": random.choice([
            "Patient responded well to treatment",
            "Follow-up recommended in 2 weeks",
            "Patient advised to rest and hydrate",
            "Chronic condition requires long-term management",
            "Patient should avoid allergens"
        ]),
        "visit_date": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
        "user_id": patient_user_id,
        "doctor_id": doctor_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/medical/medical-records",
            json=data,
            headers=create_token_headers(doctor_token)
        )
        return response.status_code == 201
    except Exception as e:
        print(f"Error creating medical record: {e}")
        return False

def create_appointment(token, doctor_id, hospital_id):
    """Create an appointment"""
    future_date = datetime.now() + timedelta(days=random.randint(1, 60))
    hour = random.randint(9, 16)
    
    data = {
        "doctor_id": doctor_id,
        "hospital_id": hospital_id,
        "appointment_datetime": future_date.replace(hour=hour, minute=0, second=0).isoformat(),
        "reason_for_visit": random.choice([
            "Regular checkup",
            "Follow-up consultation",
            "New symptoms evaluation",
            "Prescription renewal",
            "Lab results review",
            "Chronic condition management"
        ]),
        "patient_notes": random.choice([
            "First visit",
            "Experiencing symptoms for 2 weeks",
            "Need prescription refill",
            "Follow-up from last visit",
            ""
        ])
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/scheduling/appointments",
            json=data,
            headers=create_token_headers(token)
        )
        return response.status_code == 201
    except Exception as e:
        print(f"Error creating appointment: {e}")
        return False

def main():
    print("=" * 60)
    print("EGYPTIAN HEALTHCARE DATABASE POPULATION SCRIPT")
    print("=" * 60)
    print()
    
    # Store created data
    hospitals = []
    doctors = []
    patients = []
    all_accounts = []  # Store all accounts for CSV export
    
    # Step 1: Create Doctors (who will create hospitals)
    print("\n[Step 1: Creating Doctors]")
    for i in range(50):  # Create 50 doctors
        # Generate Egyptian name
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first_name = random.choice(EGYPTIAN_FIRST_NAMES_MALE)
        else:
            first_name = random.choice(EGYPTIAN_FIRST_NAMES_FEMALE)
        
        last_name = random.choice(EGYPTIAN_LAST_NAMES)
        full_name = f"Dr. {first_name} {last_name}"
        email = f"doctor{i+1}@seha.eg"
        password = "Doctor@123"
        
        # Register doctor
        doctor_user = register_user(email, password, full_name, "doctor")
        
        if doctor_user:
            doctors.append({
                "user_data": doctor_user,
                "profile": None,
                "hospital_id": None
            })
            # Save account info
            all_accounts.append({
                "type": "doctor",
                "email": email,
                "password": password,
                "full_name": full_name
            })
            if (i + 1) % 10 == 0:
                print(f"✅ Created {i + 1} doctors...")
    
    print(f"\n📊 Total doctors created: {len(doctors)}")
    
    # Step 2: Create Hospitals (using first doctor's token)
    print("\n[Step 2: Creating Hospitals]")
    if doctors:
        first_doctor_token = doctors[0]["user_data"]["access_token"]
        for hospital_data in EGYPTIAN_HOSPITALS:
            result = create_hospital(first_doctor_token, hospital_data)
            if result:
                hospitals.append(result)
                print(f"✅ Created: {hospital_data['name']} in {hospital_data['city']}")
    
    print(f"\n📊 Total hospitals created: {len(hospitals)}")
    
    # Step 3: Create Doctor Profiles
    print("\n[Step 3: Creating Doctor Profiles]")
    doctors_with_profiles = []
    for i, doctor in enumerate(doctors):
        hospital = random.choice(hospitals)
        specialization = random.choice(SPECIALIZATIONS)
        
        doctor_profile = create_doctor_profile(
            doctor["user_data"]["access_token"],
            doctor["user_data"]["user"]["user_id"],
            hospital.get("hospital_id"),
            specialization
        )
        
        if doctor_profile:
            doctors_with_profiles.append({
                "user_data": doctor["user_data"],
                "profile": doctor_profile,
                "hospital_id": hospital.get("hospital_id")
            })
            if (i + 1) % 10 == 0:
                print(f"✅ Created {i + 1} doctor profiles...")
        else:
            print(f"❌ Failed to create profile for doctor {i + 1}")
    
    print(f"\n📊 Total doctor profiles created: {len(doctors_with_profiles)}")
    
    if len(doctors_with_profiles) == 0:
        print("❌ ERROR: No doctor profiles were created. Cannot continue.")
        print("Please check your API endpoint and permissions.")
        return
    
    # Step 4: Create Patients
    print("\n[Step 4: Creating Patients]")
    for i in range(100):  # Create 100 patients
        # Generate Egyptian name
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first_name = random.choice(EGYPTIAN_FIRST_NAMES_MALE)
        else:
            first_name = random.choice(EGYPTIAN_FIRST_NAMES_FEMALE)
        
        last_name = random.choice(EGYPTIAN_LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        email = f"patient{i+1}@example.com"
        password = "Patient@123"
        
        patient_user = register_user(email, password, full_name, "patient")
        
        if patient_user:
            patients.append(patient_user)
            # Save account info
            all_accounts.append({
                "type": "patient",
                "email": email,
                "password": password,
                "full_name": full_name
            })
            if (i + 1) % 20 == 0:
                print(f"✅ Created {i + 1} patients...")
    
    print(f"\n📊 Total patients created: {len(patients)}")
    
    # Step 5: Create Medical Records
    print("\n[Step 5: Creating Medical Records]")
    records_created = 0
    if len(doctors_with_profiles) > 0:
        for patient in patients[:50]:  # Create records for 50 patients
            # Create 1-3 medical records per patient
            num_records = random.randint(1, 3)
            for _ in range(num_records):
                doctor = random.choice(doctors_with_profiles)
                # Use doctor's token to create the medical record
                if create_medical_record(
                    doctor["user_data"]["access_token"],
                    patient["user"]["user_id"],
                    doctor["profile"]["doctor_id"]
                ):
                    records_created += 1
    else:
        print("⚠️  Skipping medical records - no doctors available")
    
    print(f"✅ Total medical records created: {records_created}")
    
    # Step 6: Create Appointments
    print("\n[Step 6: Creating Appointments]")
    appointments_created = 0
    if len(doctors_with_profiles) > 0:
        for patient in patients:
            # Create 1-2 appointments per patient
            num_appointments = random.randint(1, 2)
            for _ in range(num_appointments):
                doctor = random.choice(doctors_with_profiles)
                if create_appointment(
                    patient["access_token"],
                    doctor["profile"]["doctor_id"],
                    doctor["hospital_id"]
                ):
                    appointments_created += 1
    else:
        print("⚠️  Skipping appointments - no doctors available")
    
    print(f"✅ Total appointments created: {appointments_created}")
    
    # Step 7: Export accounts to CSV
    print("\n[Step 7: Exporting Account Credentials]")
    csv_filename = f"seha_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['account_type', 'email', 'password', 'full_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for account in all_accounts:
                writer.writerow({
                    'account_type': account['type'],
                    'email': account['email'],
                    'password': account['password'],
                    'full_name': account['full_name']
                })
        
        print(f"✅ Account credentials exported to: {csv_filename}")
    except Exception as e:
        print(f"❌ Failed to export credentials: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    print(f"""
📊 Summary:
   - Hospitals: {len(hospitals)}
   - Doctors: {len(doctors_with_profiles)}
   - Patients: {len(patients)}
   - Medical Records: {records_created}
   - Appointments: {appointments_created}

🔑 Login Credentials:
   Doctor Example: doctor1@seha.eg / Doctor@123
   Patient Example: patient1@example.com / Patient@123
   
📄 All credentials saved to: {csv_filename}

🏥 Cities Covered: {', '.join(set([h['city'] for h in EGYPTIAN_HOSPITALS]))}

⚠️  Note: No admin account created. Doctors can manage hospitals.
    """)

if __name__ == "__main__":
    main()