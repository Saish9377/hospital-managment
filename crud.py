import streamlit as st
import datetime
import mysql.connector

# -------------------------------
# Database Connection
# -------------------------------
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="Hospital_management"
)
mycursor = mydb.cursor()
print("Connection Established")

# -------------------------------
# Helper Functions
# -------------------------------
def get_available_doctors():
    mycursor.execute("SELECT * FROM Doctors")
    return mycursor.fetchall()

def get_available_patients():
    mycursor.execute("SELECT * FROM Patients")
    return mycursor.fetchall()

def get_patient_by_id(patient_id):
    mycursor.execute('SELECT * FROM Patients WHERE patientID=%s', (patient_id,))
    return mycursor.fetchone()

def get_doctor_by_id(doctor_id):
    mycursor.execute('SELECT * FROM Doctors WHERE doctorID=%s', (doctor_id,))
    return mycursor.fetchone()

def get_doctor_by_name(doctor_name):
    mycursor.execute('SELECT * FROM Doctors WHERE Name=%s', (doctor_name,))
    return mycursor.fetchall()

def get_patient_by_name(patient_name):
    mycursor.execute('SELECT * FROM Patients WHERE Name=%s', (patient_name,))
    return mycursor.fetchall()

def update_doctor(doctor_id, new_name, new_specialization, new_contact):
    mycursor.execute(
        '''UPDATE Doctors
           SET Name=%s, Specialization=%s, ContactInformation=%s
           WHERE DoctorID=%s''',
        (new_name, new_specialization, new_contact, doctor_id)
    )
    mydb.commit()

def update_patient(patient_id, name, gender, dob, address, phone):
    mycursor.execute(
        '''UPDATE Patients
           SET Name=%s, Gender=%s, DateOfBirth=%s, Address=%s, PhoneNumber=%s
           WHERE PatientID=%s''',
        (name, gender, dob, address, phone, patient_id)
    )
    mydb.commit()

def book_appointment(patient_id, doctor_id, date_slot, time_slot):
    sql = """INSERT INTO Appointments 
             (PatientID, DoctorID, AppointmentDate, AppointmentTime) 
             VALUES (%s, %s, %s, %s)"""
    val = (patient_id, doctor_id, date_slot, time_slot)
    mycursor.execute(sql, val)
    mydb.commit()

    history_sql = """INSERT INTO AppointmentHist 
                     (AppointmentID, PatientID, DoctorID, AppointmentDate, AppointmentTime) 
                     VALUES (LAST_INSERT_ID(), %s, %s, %s, %s)"""
    history_val = (patient_id, doctor_id, date_slot, time_slot)
    mycursor.execute(history_sql, history_val)
    mydb.commit()

def get_doctor_appointments(doctor_id):
    mycursor.execute(
        "SELECT AppointmentDate, AppointmentTime FROM Appointments WHERE DoctorID=%s",
        (doctor_id,)
    )
    return mycursor.fetchall()

def get_appointments_by_doctor(doctor_id):
    mycursor.execute('SELECT * FROM Appointments WHERE DoctorID=%s', (doctor_id,))
    return mycursor.fetchall()

def delete_appointment(appointment_id):
    mycursor.execute('DELETE FROM Appointments WHERE AppointmentID=%s', (appointment_id,))
    mydb.commit()

def get_appointment_history(patient_id):
    mycursor.execute("SELECT * FROM AppointmentHist WHERE PatientID=%s", (patient_id,))
    return mycursor.fetchall()

# -------------------------------
# Streamlit App
# -------------------------------
def main():
    st.title("🏥 Hospital Management System")

    option = st.sidebar.selectbox(
        "Select an Operation",
        ("Book Appointment","Manage Appointment","Search","Create Details",
         "Patient History","Edit Details","List Patients And Doctors","Delete")
    )

    # ✅ Create Patient/Doctor
    if option == "Create Details":
        select_option = st.sidebar.selectbox("Select:", ["Doctor", "Patient"])
        
        if select_option == "Patient":
            st.subheader("➕ Create Patient Details")
            name = st.text_input("Enter Patient Name")
            gender = st.text_input("Enter Patient Gender")
            dob = st.date_input("Select Patient's Date of Birth")
            address = st.text_input("Enter Patient Address")
            phone = st.text_input("Enter Patient Phone Number")
            if st.button("Create Patient"):
                sql = "INSERT INTO Patients (Name, Gender, DateOfBirth, Address, PhoneNumber) VALUES (%s, %s, %s, %s, %s)"
                val = (name, gender, dob, address, phone)
                mycursor.execute(sql, val)
                mydb.commit()
                st.success("✅ Patient Record Created Successfully!")

        elif select_option == "Doctor":
            st.subheader("➕ Create Doctor Details")
            name1 = st.text_input("Enter Doctor's Name")
            spec = st.text_input("Enter Doctor's Specialization")
            cont = st.text_input("Enter Doctor's Contact Information")
            if st.button("Create Doctor"):
                sql = "INSERT INTO Doctors (Name, Specialization, ContactInformation) VALUES (%s, %s, %s)"
                val = (name1, spec, cont)
                mycursor.execute(sql, val)
                mydb.commit()
                st.success("✅ Doctor Record Created Successfully!")

    # ✅ List Patients and Doctors
    elif option == "List Patients And Doctors":
        st.subheader("📋 Patients List")
        mycursor.execute("SELECT * FROM Patients")
        for row in mycursor.fetchall():
            st.write(row)

        st.subheader("📋 Doctors List")
        mycursor.execute("SELECT * FROM Doctors")
        for row in mycursor.fetchall():
            st.write(row)

    # ✅ Delete Records
    elif option == "Delete":
        st.subheader("🗑️ Delete a Patient Record")
        iddd = st.number_input("Enter Patient ID", min_value=1)
        if st.button("Delete Patient Record"):
            sql = "DELETE FROM Patients WHERE PatientID=%s"
            mycursor.execute(sql, (iddd,))
            mydb.commit()
            st.success("✅ Patient Record Deleted Successfully!")

        st.subheader("🗑️ Delete a Doctor Record")
        idd = st.number_input("Enter Doctor ID", min_value=1)
        if st.button("Delete Doctor Record"):
            sql = "DELETE FROM Doctors WHERE DoctorID=%s"
            mycursor.execute(sql, (idd,))
            mydb.commit()
            st.success("✅ Doctor Record Deleted Successfully!")

    # ✅ Book Appointment
    elif option == "Book Appointment":
        st.subheader("📅 Book Appointment with Doctor")
        available_patients = get_available_patients()
        patient_options = {p[0]: p[1] for p in available_patients}
        selected_patient_id = st.selectbox("Select Patient", options=list(patient_options.keys()), format_func=lambda x: patient_options[x])

        available_doctors = get_available_doctors()
        doctor_options = {d[0]: d[1] for d in available_doctors}
        selected_doctor_id = st.selectbox("Select Doctor", options=list(doctor_options.keys()), format_func=lambda x: doctor_options[x])

        selected_date_slot = st.date_input("Select Date")
        selected_time_slot = st.text_input("Enter Time (e.g., '10:00 AM')")

        if st.button("Book Appointment"):
            time_slot = datetime.datetime.strptime(selected_time_slot, "%I:%M %p").strftime("%H:%M:%S")
            book_appointment(selected_patient_id, selected_doctor_id, selected_date_slot, time_slot)
            st.success("✅ Appointment booked successfully!")

    # ✅ Manage Appointments
    elif option == "Manage Appointment":
        doctors = get_available_doctors()
        doctor_options = {d[0]: d[1] for d in doctors}
        selected_doctor = st.sidebar.selectbox("Select Doctor:", options=list(doctor_options.keys()), format_func=lambda x: doctor_options[x])

        appointments = get_appointments_by_doctor(selected_doctor)
        for appointment in appointments:
            st.write(f"Appointment ID: {appointment[0]}, Patient ID: {appointment[2]}, Date: {appointment[3]}")
            if st.button(f"Delete Appointment {appointment[0]}"):
                delete_appointment(appointment[0])
                st.success("✅ Appointment deleted successfully!")

    # ✅ Edit Details
    elif option == "Edit Details":
        edit_option = st.sidebar.selectbox("Edit:", ["Doctor", "Patient"])

        if edit_option == "Patient":
            st.subheader("✏️ Edit Patient Information")
            patient_id = st.number_input("Enter Patient ID", min_value=1)
            patient = get_patient_by_id(patient_id)
            if patient:
                new_name = st.text_input("Name", value=patient[1])
                new_gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(patient[2]))
                new_dob = st.date_input("Date of Birth", value=patient[3])
                new_address = st.text_area("Address", value=patient[4])
                new_phone = st.text_input("Phone", value=patient[5])
                if st.button("Update Patient"):
                    update_patient(patient_id, new_name, new_gender, new_dob, new_address, new_phone)
                    st.success("✅ Patient updated successfully!")
            else:
                st.warning("⚠️ Patient not found!")

        elif edit_option == "Doctor":
            st.subheader("✏️ Edit Doctor Details")
            doctor_id = st.number_input("Enter Doctor ID", min_value=1)
            doctor = get_doctor_by_id(doctor_id)
            if doctor:
                edit_name = st.text_input("Name", value=doctor[1])
                edit_specialization = st.text_input("Specialization", value=doctor[2])
                edit_contact = st.text_input("Contact", value=doctor[3])
                if st.button("Update Doctor"):
                    update_doctor(doctor_id, edit_name, edit_specialization, edit_contact)
                    st.success("✅ Doctor updated successfully!")
            else:
                st.warning("⚠️ Doctor not found!")

    # ✅ Search Functionality
    elif option == "Search":
        st.sidebar.title("🔍 Search Database")
        search_option = st.sidebar.selectbox("Search:", ["Doctor", "Patient"])

        if search_option == "Doctor":
            st.subheader("Search Doctor by ID")
            search_id = st.number_input("Doctor ID", min_value=1)
            if st.button("Search Doctor by ID"):
                doctor = get_doctor_by_id(search_id)
                st.write(doctor if doctor else "⚠️ Doctor not found")

            st.subheader("Search Doctor by Name")
            search_name = st.text_input("Enter Doctor Name")
            if st.button("Search Doctor by Name"):
                doctors = get_doctor_by_name(search_name)
                st.write(doctors if doctors else "⚠️ Doctor not found")

        elif search_option == "Patient":
            st.subheader("Search Patient by ID")
            search_id = st.number_input("Patient ID", min_value=1)
            if st.button("Search Patient by ID"):
                patient = get_patient_by_id(search_id)
                st.write(patient if patient else "⚠️ Patient not found")

            st.subheader("Search Patient by Name")
            search_name = st.text_input("Enter Patient Name")
            if st.button("Search Patient by Name"):
                patients = get_patient_by_name(search_name)
                st.write(patients if patients else "⚠️ Patient not found")

    # ✅ Patient History
    elif option == "Patient History":
        st.subheader("📜 Appointment History")
        patients = get_available_patients()
        patient_options = {p[0]: p[1] for p in patients}
        selected_patient = st.sidebar.selectbox("Select Patient:", options=list(patient_options.keys()), format_func=lambda x: patient_options[x])

        history = get_appointment_history(selected_patient)
        if history:
            for appointment in history:
                doctor = get_doctor_by_id(appointment[2])
                st.write(f"Appointment ID: {appointment[0]}, Doctor: {doctor[1]}, Date: {appointment[3]}")
        else:
            st.write("⚠️ No appointment history found.")

# -------------------------------
# Run Streamlit App
# -------------------------------
if __name__ == "__main__":
    main()
