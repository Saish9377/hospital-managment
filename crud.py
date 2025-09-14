import streamlit as st
import sqlite3
import datetime

# -------------------------------
# Database Setup (Temporary SQLite)
# -------------------------------
def create_connection():
    conn = sqlite3.connect("hospital_temp.db", check_same_thread=False)
    c = conn.cursor()
    
    # Create tables if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS Patients (
                    PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT,
                    Gender TEXT,
                    DateOfBirth TEXT,
                    Address TEXT,
                    PhoneNumber TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Doctors (
                    DoctorID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT,
                    Specialization TEXT,
                    ContactInformation TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Appointments (
                    AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    DoctorID INTEGER,
                    AppointmentDate TEXT,
                    AppointmentTime TEXT,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
                    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID))''')

    c.execute('''CREATE TABLE IF NOT EXISTS AppointmentHist (
                    HistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    AppointmentID INTEGER,
                    PatientID INTEGER,
                    DoctorID INTEGER,
                    AppointmentDate TEXT,
                    AppointmentTime TEXT)''')
    
    conn.commit()
    return conn, c

conn, cursor = create_connection()

# -------------------------------
# Helper Functions
# -------------------------------
def get_available_doctors():
    cursor.execute("SELECT * FROM Doctors")
    return cursor.fetchall()

def get_available_patients():
    cursor.execute("SELECT * FROM Patients")
    return cursor.fetchall()

def get_patient_by_name(name):
    cursor.execute("SELECT * FROM Patients WHERE Name=?", (name,))
    return cursor.fetchall()

def get_doctor_by_name(name):
    cursor.execute("SELECT * FROM Doctors WHERE Name=?", (name,))
    return cursor.fetchall()

def book_appointment(patient_id, doctor_id, date_slot, time_slot):
    cursor.execute("""INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) 
                      VALUES (?, ?, ?, ?)""", (patient_id, doctor_id, date_slot, time_slot))
    conn.commit()
    last_id = cursor.lastrowid

    cursor.execute("""INSERT INTO AppointmentHist (AppointmentID, PatientID, DoctorID, AppointmentDate, AppointmentTime) 
                      VALUES (?, ?, ?, ?, ?)""", (last_id, patient_id, doctor_id, date_slot, time_slot))
    conn.commit()

def get_appointments_by_doctor(doctor_id):
    cursor.execute("SELECT * FROM Appointments WHERE DoctorID=?", (doctor_id,))
    return cursor.fetchall()

def delete_appointment(appointment_id):
    cursor.execute("DELETE FROM Appointments WHERE AppointmentID=?", (appointment_id,))
    conn.commit()

def get_appointment_history(patient_id):
    cursor.execute("SELECT * FROM AppointmentHist WHERE PatientID=?", (patient_id,))
    return cursor.fetchall()

# -------------------------------
# Streamlit App
# -------------------------------
def main():
    st.title("🏥 Hospital Management System ")

    option = st.sidebar.selectbox(
        "Select an Operation",
        ("Book Appointment", "Manage Appointment", "Search", "Create Details",
         "Patient History", "List Patients And Doctors", "Delete")
    )

    # ✅ Create Details
    if option == "Create Details":
        select_option = st.radio("Select Type", ["Patient", "Doctor"])
        
        if select_option == "Patient":
            st.subheader("➕ Create Patient")
            name = st.text_input("Name")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth")
            address = st.text_input("Address")
            phone = st.text_input("Phone Number")
            if st.button("Save Patient"):
                cursor.execute("INSERT INTO Patients (Name, Gender, DateOfBirth, Address, PhoneNumber) VALUES (?, ?, ?, ?, ?)",
                               (name, gender, dob.strftime("%Y-%m-%d"), address, phone))
                conn.commit()
                st.success("✅ Patient Added Successfully!")

        else:
            st.subheader("➕ Create Doctor")
            name = st.text_input("Name")
            spec = st.text_input("Specialization")
            cont = st.text_input("Contact Info")
            if st.button("Save Doctor"):
                cursor.execute("INSERT INTO Doctors (Name, Specialization, ContactInformation) VALUES (?, ?, ?)",
                               (name, spec, cont))
                conn.commit()
                st.success("✅ Doctor Added Successfully!")

    # ✅ List Records
    elif option == "List Patients And Doctors":
        st.subheader("📋 Patients")
        st.table(get_available_patients())

        st.subheader("📋 Doctors")
        st.table(get_available_doctors())

    # ✅ Delete
    elif option == "Delete":
        st.subheader("🗑️ Delete Patient")
        pid = st.number_input("Enter Patient ID", min_value=1)
        if st.button("Delete Patient"):
            cursor.execute("DELETE FROM Patients WHERE PatientID=?", (pid,))
            conn.commit()
            st.success("✅ Patient Deleted!")

        st.subheader("🗑️ Delete Doctor")
        did = st.number_input("Enter Doctor ID", min_value=1)
        if st.button("Delete Doctor"):
            cursor.execute("DELETE FROM Doctors WHERE DoctorID=?", (did,))
            conn.commit()
            st.success("✅ Doctor Deleted!")

    # ✅ Book Appointment
    elif option == "Book Appointment":
        st.subheader("📅 Book Appointment")
        patients = get_available_patients()
        doctors = get_available_doctors()

        if patients and doctors:
            patient_map = {p[0]: p[1] for p in patients}
            doctor_map = {d[0]: d[1] for d in doctors}

            selected_patient = st.selectbox("Select Patient", list(patient_map.keys()), format_func=lambda x: patient_map[x])
            selected_doctor = st.selectbox("Select Doctor", list(doctor_map.keys()), format_func=lambda x: doctor_map[x])

            date_slot = st.date_input("Date")
            time_input = st.text_input("Time (HH:MM)")

            if st.button("Book"):
                if time_input:
                    book_appointment(selected_patient, selected_doctor, date_slot.strftime("%Y-%m-%d"), time_input)
                    st.success("✅ Appointment Booked!")
                else:
                    st.error("Please enter a valid time.")
        else:
            st.warning("⚠️ Add at least one patient and doctor first.")

    # ✅ Manage Appointment
    elif option == "Manage Appointment":
        st.subheader("🗂️ Manage Appointments")
        doctors = get_available_doctors()
        if doctors:
            doctor_map = {d[0]: d[1] for d in doctors}
            selected_doctor = st.selectbox("Select Doctor", list(doctor_map.keys()), format_func=lambda x: doctor_map[x])
            appointments = get_appointments_by_doctor(selected_doctor)

            if appointments:
                for appt in appointments:
                    st.write(appt)
                    if st.button(f"Delete Appointment {appt[0]}"):
                        delete_appointment(appt[0])
                        st.success("✅ Appointment Deleted!")
            else:
                st.info("No appointments found for this doctor.")
        else:
            st.warning("⚠️ No doctors available.")

    # ✅ Patient History
    elif option == "Patient History":
        st.subheader("📜 Patient Appointment History")
        patients = get_available_patients()
        if patients:
            patient_map = {p[0]: p[1] for p in patients}
            selected_patient = st.selectbox("Select Patient", list(patient_map.keys()), format_func=lambda x: patient_map[x])
            history = get_appointment_history(selected_patient)
            st.table(history)
        else:
            st.warning("⚠️ No patients available.")

    # ✅ Search
    elif option == "Search":
        st.subheader("🔍 Search Records")
        choice = st.radio("Search by", ["Doctor", "Patient"])
        name = st.text_input("Enter Name")
        if st.button("Search"):
            if choice == "Doctor":
                st.table(get_doctor_by_name(name))
            else:
                st.table(get_patient_by_name(name))


if __name__ == "__main__":
    main()

