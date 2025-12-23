import streamlit as st
import requests
from datetime import datetime, date
import json

# Configuration - Nginx gateway is on port 8000 (from docker-compose.yml)
API_BASE_URL = "http://localhost:8000"

# Service endpoints through Nginx gateway
API_ENDPOINTS = {
    "auth": "/auth",
    "medical": "/medical",
    "scheduling": "/scheduling",
    "chatbot": "/chatbot"
}

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Helper functions
def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def api_request(service, endpoint, method="GET", data=None, params=None):
    url = f"{API_BASE_URL}{API_ENDPOINTS[service]}{endpoint}"
    headers = get_headers()
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {}
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

# Authentication Pages
def login_page():
    st.title("🏥 SEHA+")
    st.subheader("Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Login", use_container_width=True):
                data = {"email": email, "password": password}
                result = api_request("auth", "/login", "POST", data)
                
                if result:
                    st.session_state.token = result["access_token"]
                    user_info = api_request("auth", "/me", "GET")
                    if user_info:
                        st.session_state.user = user_info
                        st.session_state.page = 'dashboard'
                        st.rerun()
        
        with col_btn2:
            if st.button("Register", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()

def register_page():
    st.title("🏥 Register New Account")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone")
        dob = st.date_input("Date of Birth", max_value=date.today())
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        address = st.text_area("Address")
        user_type = st.selectbox("User Type", ["patient", "doctor", "admin"])
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Register", use_container_width=True):
                data = {
                    "email": email,
                    "password": password,
                    "full_name": full_name,
                    "phone": phone,
                    "date_of_birth": str(dob),
                    "gender": gender,
                    "address": address,
                    "user_type": user_type
                }
                result = api_request("auth", "/register", "POST", data)
                
                if result:
                    st.success("Registration successful!")
                    st.session_state.token = result["access_token"]
                    st.session_state.user = result["user"]
                    st.session_state.page = 'dashboard'
                    st.rerun()
        
        with col_btn2:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

# Dashboard
def dashboard_page():
    st.title("🏥 SEHA+")
    
    user_type = st.session_state.user.get('user_type', 'patient')
    
    # Sidebar navigation
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state.user['full_name']}**")
        st.write(f"Email: {st.session_state.user['email']}")
        st.write(f"Type: {user_type.upper()}")
        st.divider()
        
        # Role-based menu options
        menu_options = ["Dashboard", "Healthcare Chatbot", "Profile"]
        
        # Patient can view doctors, hospitals, their own records and appointments
        if user_type == "patient":
            menu_options.insert(1, "Doctors")
            menu_options.insert(2, "Hospitals")
            menu_options.insert(3, "My Medical Records")
            menu_options.insert(4, "My Appointments")
        
        # Doctor can manage their profile, view their appointments, create medical records
        elif user_type == "doctor":
            menu_options.insert(1, "My Doctor Profile")
            menu_options.insert(2, "My Appointments")
            menu_options.insert(3, "Medical Records Management")
            menu_options.insert(4, "Patients")
        
        # Admin has full access
        elif user_type == "admin":
            menu_options.insert(1, "Doctors")
            menu_options.insert(2, "Hospitals")
            menu_options.insert(3, "Medical Records")
            menu_options.insert(4, "Appointments")
            menu_options.insert(5, "System Management")
        
        menu = st.radio("Navigation", menu_options)
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content based on menu selection
    if menu == "Dashboard":
        show_dashboard_overview()
    elif menu == "Doctors":
        show_doctors_page()
    elif menu == "Hospitals":
        show_hospitals_page()
    elif menu in ["Medical Records", "My Medical Records", "Medical Records Management"]:
        show_medical_records_page(user_type)
    elif menu in ["Appointments", "My Appointments"]:
        show_appointments_page(user_type)
    elif menu == "Healthcare Chatbot":
        show_chatbot_page()
    elif menu == "Profile":
        show_profile_page()
    elif menu == "My Doctor Profile":
        show_doctor_profile_page()
    elif menu == "Patients":
        show_patients_page()
    elif menu == "System Management":
        show_system_management()

def show_dashboard_overview():
    st.header("Dashboard Overview")
    
    user_type = st.session_state.user.get('user_type', 'patient')
    
    # Get upcoming appointments count
    count_data = api_request("scheduling", "/appointments/upcoming/count", "GET")
    count = count_data.get("upcoming_appointments", 0) if isinstance(count_data, dict) else (count_data if count_data else 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Upcoming Appointments", count)
    
    with col2:
        records = api_request("medical", "/medical-records/my-records", "GET")
        st.metric("Medical Records", records.get("total", 0) if records else 0)
    
    with col3:
        st.metric("User Type", user_type.upper())
    
    st.divider()
    
    # Recent appointments
    st.subheader("Recent Appointments")
    appointments = api_request("scheduling", "/appointments", "GET", params={"limit": 5})
    
    if appointments and appointments.get("appointments"):
        for apt in appointments["appointments"]:
            with st.expander(f"Appointment #{apt['appointment_id']} - {apt.get('status', 'N/A')}"):
                st.write(f"**Status:** {apt.get('status')}")
                st.write(f"**ID:** {apt.get('appointment_id')}")
    else:
        st.info("No appointments found")

def show_doctors_page():
    st.header("👨‍⚕️ Doctors Management")
    
    tab1, tab2, tab3 = st.tabs(["List Doctors", "Doctor Details", "Create Doctor Profile"])
    
    with tab1:
        st.subheader("Search Doctors")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            specialization = st.text_input("Specialization")
        with col2:
            hospital_id = st.number_input("Hospital ID", min_value=0, value=0)
        with col3:
            online_only = st.checkbox("Available Online Only")
        
        if st.button("Search Doctors"):
            params = {}
            if specialization:
                params["specialization"] = specialization
            if hospital_id > 0:
                params["hospital_id"] = hospital_id
            if online_only:
                params["is_available_online"] = True
            
            doctors = api_request("medical", "/doctors", "GET", params=params)
            
            if doctors and doctors.get("doctors"):
                st.write(f"Found {doctors['total']} doctors")
                for doc in doctors["doctors"]:
                    with st.expander(f"Dr. {doc.get('specialization', 'N/A')} - ID: {doc['doctor_id']}"):
                        st.write(f"**Doctor ID:** {doc['doctor_id']}")
                        st.write(f"**Specialization:** {doc.get('specialization')}")
                        st.write(f"**Hospital ID:** {doc.get('hospital_id')}")
            else:
                st.info("No doctors found")
    
    with tab2:
        st.subheader("Get Doctor Details")
        doctor_id = st.number_input("Enter Doctor ID", min_value=1, value=1)
        
        if st.button("Get Doctor Info"):
            doctor = api_request("medical", f"/doctors/{doctor_id}", "GET")
            
            if doctor:
                st.json(doctor)
    
    with tab3:
        st.subheader("Create Doctor Profile")
        
        specialization = st.text_input("Specialization", key="create_spec")
        license_number = st.text_input("License Number")
        hospital_id = st.number_input("Hospital ID", min_value=1, value=1, key="create_hosp")
        qualifications = st.text_area("Qualifications")
        availability = st.text_area("Availability Schedule")
        online_available = st.checkbox("Available Online")
        
        if st.button("Create Doctor Profile"):
            data = {
                "specialization": specialization,
                "license_number": license_number,
                "hospital_id": hospital_id,
                "qualifications": qualifications,
                "availability_schedule": availability,
                "is_available_online": online_available
            }
            result = api_request("medical", "/doctors", "POST", data)
            
            if result:
                st.success(f"Doctor profile created! ID: {result['doctor_id']}")

def show_hospitals_page():
    st.header("🏥 Hospitals Management")
    
    tab1, tab2, tab3 = st.tabs(["List Hospitals", "Hospital Details", "Create Hospital"])
    
    with tab1:
        st.subheader("Search Hospitals")
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City")
        with col2:
            emergency = st.checkbox("Has Emergency Services")
        
        if st.button("Search Hospitals"):
            params = {}
            if city:
                params["city"] = city
            if emergency:
                params["has_emergency"] = True
            
            hospitals = api_request("medical", "/hospitals", "GET", params=params)
            
            if hospitals and hospitals.get("hospitals"):
                st.write(f"Found {hospitals['total']} hospitals")
                for hosp in hospitals["hospitals"]:
                    with st.expander(f"{hosp['name']} - {hosp['city']}"):
                        st.write(f"**Hospital ID:** {hosp['hospital_id']}")
                        st.write(f"**Name:** {hosp['name']}")
                        st.write(f"**City:** {hosp['city']}")
            else:
                st.info("No hospitals found")
    
    with tab2:
        st.subheader("Get Hospital Details")
        hospital_id = st.number_input("Enter Hospital ID", min_value=1, value=1)
        
        if st.button("Get Hospital Info"):
            hospital = api_request("medical", f"/hospitals/{hospital_id}", "GET")
            
            if hospital:
                st.json(hospital)
    
    with tab3:
        st.subheader("Create Hospital")
        
        name = st.text_input("Hospital Name")
        address = st.text_area("Address")
        city = st.text_input("City", key="create_city")
        phone = st.text_input("Phone")
        has_emergency = st.checkbox("Has Emergency Services", key="create_emergency")
        
        if st.button("Create Hospital"):
            data = {
                "name": name,
                "address": address,
                "city": city,
                "phone": phone,
                "has_emergency": has_emergency
            }
            result = api_request("medical", "/hospitals", "POST", data)
            
            if result:
                st.success("Hospital created successfully!")

def show_medical_records_page(user_type="patient"):
    st.header("📋 Medical Records")
    
    # Role-based access control
    if user_type == "patient":
        tab1, tab2 = st.tabs(["My Records", "View Record Details"])
    elif user_type == "doctor":
        tab1, tab2, tab3 = st.tabs(["My Patient Records", "Create Record", "View/Edit Record"])
    else:  # admin
        tab1, tab2, tab3 = st.tabs(["All Records", "Create Record", "Manage Record"])
    
    with tab1:
        if user_type == "patient":
            st.subheader("My Medical Records")
        elif user_type == "doctor":
            st.subheader("Patient Records I Created")
        else:
            st.subheader("All Medical Records")
        
        if st.button("Load Records"):
            records = api_request("medical", "/medical-records/my-records", "GET")
            
            if records and records.get("records"):
                st.write(f"Total Records: {records['total']}")
                for rec in records["records"]:
                    with st.expander(f"Record #{rec['record_id']} - {rec.get('diagnosis', 'N/A')}"):
                        st.write(f"**Record ID:** {rec['record_id']}")
                        st.write(f"**Diagnosis:** {rec.get('diagnosis')}")
                        
                        # Only doctors and admins can delete
                        if user_type in ["doctor", "admin"]:
                            if st.button(f"Delete Record {rec['record_id']}", key=f"del_rec_{rec['record_id']}"):
                                result = api_request("medical", f"/medical-records/{rec['record_id']}", "DELETE")
                                if result is not None:
                                    st.success("Record deleted!")
                                    st.rerun()
            else:
                st.info("No medical records found")
    
    with tab2:
        if user_type == "patient":
            st.subheader("View Specific Record")
            record_id = st.number_input("Enter Record ID", min_value=1, value=1)
            
            if st.button("Get Record Details"):
                record = api_request("medical", f"/medical-records/{record_id}", "GET")
                
                if record:
                    st.json(record)
        else:
            st.subheader("Create Medical Record")
            st.info("Only doctors can create medical records for patients")
            
            diagnosis = st.text_area("Diagnosis")
            prescription = st.text_area("Prescription")
            tests = st.text_area("Tests Ordered")
            notes = st.text_area("Doctor Notes")
            visit_date = st.date_input("Visit Date")
            patient_id = st.number_input("Patient User ID", min_value=1, value=1)
            doctor_id = st.number_input("Doctor ID", min_value=1, value=1)
            
            if st.button("Create Record"):
                data = {
                    "diagnosis": diagnosis,
                    "prescription": prescription,
                    "tests_ordered": tests,
                    "doctor_notes": notes,
                    "visit_date": f"{visit_date}T00:00:00Z",
                    "user_id": patient_id,
                    "doctor_id": doctor_id
                }
                result = api_request("medical", "/medical-records", "POST", data)
                
                if result:
                    st.success("Medical record created successfully!")
    
    if user_type != "patient":
        with tab3:
            st.subheader("View/Manage Specific Record")
            record_id = st.number_input("Enter Record ID", min_value=1, value=1, key="manage_rec_id")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Get Record"):
                    record = api_request("medical", f"/medical-records/{record_id}", "GET")
                    
                    if record:
                        st.json(record)
            
            with col2:
                if st.button("Delete Record"):
                    result = api_request("medical", f"/medical-records/{record_id}", "DELETE")
                    
                    if result is not None:
                        st.success("Record deleted successfully!")

def show_appointments_page(user_type="patient"):
    st.header("📅 Appointments Management")
    
    # Role-based tabs
    if user_type == "patient":
        tab1, tab2 = st.tabs(["My Appointments", "Book Appointment"])
    elif user_type == "doctor":
        tab1, tab2, tab3 = st.tabs(["My Schedule", "Patient Appointments", "Manage Appointments"])
    else:  # admin
        tab1, tab2, tab3 = st.tabs(["All Appointments", "Create Appointment", "Manage"])
    
    with tab1:
        if user_type == "patient":
            st.subheader("My Appointments")
        elif user_type == "doctor":
            st.subheader("My Schedule")
        else:
            st.subheader("All Appointments")
        
        status_filter = st.selectbox("Filter by Status", ["all", "scheduled", "completed", "cancelled"])
        
        if st.button("Load Appointments"):
            params = {}
            if status_filter != "all":
                params["status"] = status_filter
            
            appointments = api_request("scheduling", "/appointments", "GET", params=params)
            
            if appointments and appointments.get("appointments"):
                st.write(f"Total Appointments: {appointments['total']}")
                for apt in appointments["appointments"]:
                    with st.expander(f"Appointment #{apt['appointment_id']} - {apt.get('status')}"):
                        st.write(f"**Appointment ID:** {apt['appointment_id']}")
                        st.write(f"**Status:** {apt.get('status')}")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button(f"Cancel Appointment", key=f"cancel_{apt['appointment_id']}"):
                                result = api_request("scheduling", f"/appointments/{apt['appointment_id']}/cancel", "PATCH")
                                if result:
                                    st.success("Appointment cancelled!")
                                    st.rerun()
                        
                        # Only admins can delete
                        if user_type == "admin":
                            with col_b:
                                if st.button(f"Delete", key=f"del_{apt['appointment_id']}"):
                                    result = api_request("scheduling", f"/appointments/{apt['appointment_id']}", "DELETE")
                                    if result is not None:
                                        st.success("Appointment deleted!")
                                        st.rerun()
            else:
                st.info("No appointments found")
    
    with tab2:
        if user_type == "patient":
            st.subheader("Book New Appointment")
        elif user_type == "doctor":
            st.subheader("View Patient Appointments")
            doctor_id = st.number_input("Enter Doctor ID", min_value=1, value=1, key="doc_apt_id")
            
            if st.button("Load Doctor Appointments"):
                appointments = api_request("scheduling", f"/doctors/{doctor_id}/appointments", "GET")
                if appointments:
                    for apt in appointments:
                        st.write(f"Appointment ID: {apt.get('appointment_id')}")
                        st.write(f"Patient ID: {apt.get('patient_id')}")
                        st.divider()
        else:
            st.subheader("Create New Appointment")
        
        if user_type in ["patient", "admin"]:
            doctor_id = st.number_input("Doctor ID", min_value=1, value=1, key="apt_doctor")
            hospital_id = st.number_input("Hospital ID", min_value=1, value=1, key="apt_hospital")
            apt_date = st.date_input("Appointment Date", min_value=date.today())
            apt_time = st.time_input("Appointment Time")
            reason = st.text_area("Reason for Visit")
            notes = st.text_area("Patient Notes")
            
            if st.button("Book Appointment"):
                datetime_str = f"{apt_date}T{apt_time}:00Z"
                data = {
                    "doctor_id": doctor_id,
                    "hospital_id": hospital_id,
                    "appointment_datetime": datetime_str,
                    "reason_for_visit": reason,
                    "patient_notes": notes
                }
                result = api_request("scheduling", "/appointments", "POST", data)
                
                if result:
                    st.success(f"Appointment created! ID: {result['appointment_id']}")
    
    if user_type != "patient":
        with tab3:
            st.subheader("Manage Specific Appointment")
            
            apt_id = st.number_input("Appointment ID", min_value=1, value=1, key="manage_apt")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Get Details"):
                    apt = api_request("scheduling", f"/appointments/{apt_id}", "GET")
                    
                    if apt:
                        st.json(apt)
            
            with col2:
                if st.button("Cancel"):
                    result = api_request("scheduling", f"/appointments/{apt_id}/cancel", "PATCH")
                    if result:
                        st.success("Appointment cancelled!")
            
            with col3:
                if user_type == "admin":
                    if st.button("Delete"):
                        result = api_request("scheduling", f"/appointments/{apt_id}", "DELETE")
                        
                        if result is not None:
                            st.success("Appointment deleted!")

def show_chatbot_page():
    st.header("🤖 Healthcare AI Assistant")
    
    # Auto-create or load session
    if 'chat_session_id' not in st.session_state:
        # Try to get existing sessions
        try:
            sessions = api_request("chatbot", "/sessions", "GET")
            
            if sessions and len(sessions) > 0:
                # Use the most recent session
                st.session_state.chat_session_id = sessions[0]['session_id']
            else:
                # Create a new session automatically
                data = {"session_title": "Healthcare Chat"}
                result = api_request("chatbot", "/sessions", "POST", data)
                
                if result and result.get('session_id'):
                    st.session_state.chat_session_id = result['session_id']
                else:
                    st.error("Failed to create chat session. Please check if the chatbot service is running properly.")
                    return
        except Exception as e:
            st.error(f"Chatbot service error: {str(e)}")
            st.info("The chatbot service may not be configured correctly. Please check the backend logs.")
            return
    
    session_id = st.session_state.chat_session_id
    
    # Add a small info bar with option to start new chat
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption(f"💬 Chat Session #{session_id}")
    with col2:
        if st.button("🔄 New Chat", use_container_width=True):
            # Create new session
            data = {"session_title": "Healthcare Chat"}
            result = api_request("chatbot", "/sessions", "POST", data)
            
            if result and result.get('session_id'):
                st.session_state.chat_session_id = result['session_id']
                if 'chat_messages' in st.session_state:
                    del st.session_state.chat_messages
                st.rerun()
    
    st.divider()
    
    # Initialize messages in session state if not exists
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
        # Load existing messages from backend
        try:
            messages = api_request("chatbot", f"/sessions/{session_id}/messages", "GET")
            if messages:
                st.session_state.chat_messages = messages
        except Exception as e:
            st.warning("Could not load previous messages")
    
    # Display chat messages
    for msg in st.session_state.chat_messages:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.write(msg['content'])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your health...")
    
    if user_input:
        # Add user message to display
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Send to API and get response
        with st.spinner("AI is thinking..."):
            try:
                # Send only content, no attachments field
                data = {"content": user_input}
                result = api_request("chatbot", f"/sessions/{session_id}/messages", "POST", data)
                
                if result and result.get('assistant_message'):
                    # Add assistant response to display
                    assistant_msg = result['assistant_message']['content']
                    st.session_state.chat_messages.append({
                        'role': 'assistant',
                        'content': assistant_msg
                    })
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.write(assistant_msg)
                    
                    st.rerun()
                else:
                    # Show error in chat
                    error_msg = "I apologize, but I'm having trouble processing your request. Please try again."
                    st.session_state.chat_messages.append({
                        'role': 'assistant',
                        'content': error_msg
                    })
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                        if result:
                            st.json(result)  # Show the actual response for debugging
            except Exception as e:
                error_msg = f"Error communicating with AI: {str(e)}"
                st.session_state.chat_messages.append({
                    'role': 'assistant',
                    'content': error_msg
                })
                with st.chat_message("assistant"):
                    st.error(error_msg)

def show_profile_page():
    st.header("👤 My Profile")
    
    if st.session_state.user:
        user = st.session_state.user
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**User ID:**", user.get('user_id'))
            st.write("**Email:**", user.get('email'))
            st.write("**Full Name:**", user.get('full_name'))
        
        with col2:
            st.write("**User Type:**", user.get('user_type', 'N/A'))
            st.write("**Created At:**", user.get('created_at', 'N/A'))
        
        st.divider()
        
        if st.button("Refresh Profile"):
            user_info = api_request("auth", "/me", "GET")
            if user_info:
                st.session_state.user = user_info
                st.success("Profile refreshed!")
                st.rerun()

def show_doctor_profile_page():
    st.header("👨‍⚕️ My Doctor Profile")
    
    tab1, tab2 = st.tabs(["View Profile", "Update Profile"])
    
    with tab1:
        st.subheader("Doctor Profile Information")
        doctor_id = st.number_input("Your Doctor ID", min_value=1, value=1)
        
        if st.button("Load My Profile"):
            doctor = api_request("medical", f"/doctors/{doctor_id}", "GET")
            
            if doctor:
                st.json(doctor)
    
    with tab2:
        st.subheader("Update Doctor Profile")
        st.info("Update your professional information")
        
        doctor_id = st.number_input("Your Doctor ID", min_value=1, value=1, key="update_doc_id")
        specialization = st.text_input("Specialization")
        hospital_id = st.number_input("Hospital ID", min_value=1, value=1)
        qualifications = st.text_area("Qualifications")
        online_available = st.checkbox("Available Online")
        
        if st.button("Update Profile"):
            data = {
                "specialization": specialization,
                "hospital_id": hospital_id,
                "qualifications": qualifications,
                "is_available_online": online_available
            }
            result = api_request("medical", f"/doctors/{doctor_id}", "PUT", data)
            
            if result:
                st.success("Profile updated successfully!")

def show_patients_page():
    st.header("👥 Patients")
    st.info("View and manage patient information")
    
    st.subheader("Search Patients")
    st.write("Patient search functionality - requires backend support")
    
    # For now, show medical records which contain patient information
    st.subheader("Recent Patient Records")
    if st.button("Load Patient Records"):
        records = api_request("medical", "/medical-records/my-records", "GET")
        
        if records and records.get("records"):
            for rec in records["records"]:
                with st.expander(f"Patient Record #{rec['record_id']}"):
                    st.json(rec)

def show_system_management():
    st.header("⚙️ System Management")
    st.info("Admin-only system management tools")
    
    tab1, tab2, tab3 = st.tabs(["Statistics", "User Management", "System Health"])
    
    with tab1:
        st.subheader("System Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            doctors = api_request("medical", "/doctors", "GET")
            st.metric("Total Doctors", doctors.get("total", 0) if doctors else 0)
        
        with col2:
            hospitals = api_request("medical", "/hospitals", "GET")
            st.metric("Total Hospitals", hospitals.get("total", 0) if hospitals else 0)
        
        with col3:
            appointments = api_request("scheduling", "/appointments", "GET")
            st.metric("Total Appointments", appointments.get("total", 0) if appointments else 0)
    
    with tab2:
        st.subheader("User Management")
        st.write("Manage users, roles, and permissions")
        st.info("User management features require backend support")
    
    with tab3:
        st.subheader("System Health")
        st.write("Monitor system services and performance")
        
        # Test each service
        services = {
            "Auth Service": "/auth/",
            "Medical Service": "/medical/",
            "Scheduling Service": "/scheduling/",
            "Chatbot Service": "/chatbot/"
        }
        
        for service_name, endpoint in services.items():
            try:
                # Extract service key from endpoint
                service_key = endpoint.strip("/")
                result = api_request(service_key, "/", "GET")
                if result is not None:
                    st.success(f"✅ {service_name}: Online")
                else:
                    st.error(f"❌ {service_name}: Error")
            except:
                st.error(f"❌ {service_name}: Offline")

# Main app
def main():
    st.set_page_config(
        page_title="SEHA+",
        page_icon="🏥",
        layout="wide"
    )
    
    if st.session_state.page == 'login' and not st.session_state.token:
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    else:
        if st.session_state.token:
            dashboard_page()
        else:
            st.session_state.page = 'login'
            st.rerun()

if __name__ == "__main__":
    main()