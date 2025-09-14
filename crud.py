import streamlit as st
import datetime

# -------------------------------
# In-memory storage
# -------------------------------
patients = []
doctors = []
appointments = []
appointment_history = []

patient_id_counter = 1
doctor_id_counter = 1
appointment_id_counter = 1

# -------------------------------
# Helper Functions
# -------------------------------
def add_patient(name, gender, dob, address, phone):
    global patient_id_counter
    patient = {
        "id": patient_id_counter,
        "name": name,
        "gender": gender,
        "dob": dob,
        "address": address,
        "phone": phone
    }
    patients.append(patient)
    patient_id_counter += 1
    return patient

def add_doctor(name, specialization, contact):
    global doctor_id_counter
    doctor = {
        "id": doctor_id_counter,
        "name": name,
        "specialization": specialization,
        "contact": contact
    }
    doctors.append(doctor)
    doctor_id_counter += 1
    return doctor

def book_appointment(patient_id, doctor_id, date_slot, time_slot):
    global appointment_id_counter
    appointment = {
        "id": appointment_id_counter,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "date": date_slot,
        "time": time_slot
    }
    appointments.append(appointment)
    appointment_history.append(appointment.copy())
    appointment_id_counter += 1
    return appointment

def get_patient_by_id(pid):
    return next((p for p in patients if p["id"] == pid), None)

def get_doctor_by_id(did):
    return next((d for d in doctors if d["id"] == did), None)

def delete_patient(pid):
    global patients
    patients = [p for p in patients if p["id"] != pid]

def delete_doctor(did):
    global doctors
    doctors = [d for d in doctors if d["id"] != did]

def delete_appointment(aid):
    global appointments
    appointments = [a for a in appointments if a["id"] != aid]

# -------------------------------
# Streamlit App
# -------------------------------
def main():
    st.title("🏥 Hospital Management System (No Database)")

    option = st.sidebar.selectbox(
        "Select an Operation",
        ("Book Appointment", "Manage Appointment", "Search", "Create Details",
         "Patient History", "Edit Details", "List Patients And Doctors", "Delete")
    )

    # ✅ Create Patient / Doctor
    if option == "Create Details":
        select_option = st.sidebar.selectbox("Select:", ["Doctor", "Patient"])
        
        if select_option == "Patient":
            st.subheader("➕ Create Patient")
            name = st.text_input("Name")
            gender = st.text_input("Gender")
            dob = st.date_input("Date of Birth")
            address = st.text_input("Address")
            phone = st.text_input("Phone")
            if st.button("Add Patient"):
                patient = add_patient(name, gender, dob, address, phone)
                st.success(f"Patient Added: {patient}")

        elif select_option == "Doctor":
            st.subheader("➕ Create Doctor")
            name = st.text_input("Name")
            spec = st.text_input("Specialization")
            cont = st.text_input("Contact Info")
            if st.button("Add Doctor"):
                doctor = add_doctor(name, spec, cont)
                st.success(f"Doctor Added: {doctor}")

    # ✅ List Patients & Doctors
    elif option == "List Patients And Doctors":
        st.subheader("📋 Patients")
        st.table(patients)
        st.subheader("📋 Doctors")
        st.table(doctors)

    # ✅ Delete
    elif option == "Delete":
        st.subheader("🗑️ Delete Patient")
        pid = st.number_input("Enter Patient ID", min_value=1, step=1)
        if st.button("Delete Patient"):
            delete_patient(pid)
            st.success("Patient deleted")

        st.subheader("🗑️ Delete Doctor")
        did = st.number_input("Enter Doctor ID", min_value=1, step=1)
        if st.button("Delete Doctor"):
            delete_doctor(did)
            st.success("Doctor deleted")

    # ✅ Book Appointment
    elif option == "Book Appointment":
        st.subheader("📅 Book Appointment")
        if not patients or not doctors:
            st.warning("Add patients and doctors first!")
        else:
            patient_id = st.selectbox("Select Patient", [p["id"] for p in patients], format_func=lambda x: get_patient_by_id(x)["name"])
            doctor_id = st.selectbox("Select Doctor", [d["id"] for d in doctors], format_func=lambda x: get_doctor_by_id(x)["name"])
            date_slot = st.date_input("Date")
            time_input = st.text_input("Time (e.g., 10:00 AM)")
            if st.button("Book"):
                time_slot = datetime.datetime.strptime(time_input, "%I:%M %p").strftime("%H:%M")
                appt = book_appointment(patient_id, doctor_id, date_slot, time_slot)
                st.success(f"Appointment Booked: {appt}")

    # ✅ Manage Appointment
    elif option == "Manage Appointment":
        st.subheader("📂 Manage Appointments")
        if not appointments:
            st.info("No appointments found")
        else:
            for appt in appointments:
                st.write(appt)
                if st.button(f"Delete Appointment {appt['id']}"):
                    delete_appointment(appt["id"])
                    st.success("Appointment deleted")

    # ✅ Patient History
    elif option == "Patient History":
        st.subheader("📜 Patient History")
        pid = st.number_input("Enter Patient ID", min_value=1, step=1)
        hist = [a for a in appointment_history if a["patient_id"] == pid]
        if hist:
            st.table(hist)
        else:
            st.info("No history found")

    # ✅ Search
    elif option == "Search":
        search_option = st.sidebar.selectbox("Search:", ["Doctor", "Patient"])
        name = st.text_input("Enter Name")
        if st.button("Search"):
            if search_option == "Doctor":
                results = [d for d in doctors if d["name"].lower() == name.lower()]
            else:
                results = [p for p in patients if p["name"].lower() == name.lower()]
            st.table(results if results else [])

if __name__ == "__main__":
    main()
