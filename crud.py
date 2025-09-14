import streamlit as st
import datetime
from operations import get_appointment_history,get_appointments_by_doctor,get_doctor_appointments,delete_appointment,book_appointment,update_patient,update_doctor,get_patient_by_name,get_doctor_by_name,get_doctor_by_id,get_patient_by_id,get_available_patients,get_available_doctors
from operations import mycursor,mydb

# Establish a connection to MySQL Server
# Create Streamlit App

def main():
    st.title("Hospital Management ")

    # Display Options for CRUD Operations
    option=st.sidebar.selectbox("Select an Operation",("Book Appointment","Manage Appointment","Search","Create Details","Patient History","Edit Details","List Patients And Doctors","Delete"))
    
    if option=="Create Details":
        select_option = st.sidebar.selectbox("Select:", ["Doctor", "Patient"])
        if select_option=="Patient":
            st.subheader("Create a Patient Details")
            name = st.text_input("Enter Patient Name", key="patient_name")
            gender = st.text_input("Enter Patient Gender", key="patient_gender")
            dob = st.date_input("Select Patient's Date of Birth", key="patient_dob")
            address = st.text_input("Enter Patient Address", key="patient_address")
            phone = st.text_input("Enter Patient Phone Number", key="patient_phone")
            if st.button("Create Patient"):
                sql = "INSERT INTO Patients (Name, Gender, DateofBirth, Address, PhoneNumber) VALUES (%s, %s, %s, %s, %s)"
                val = (name, gender, dob, address, phone)
                mycursor.execute(sql, val)
                mydb.commit()
                st.success("Patient Record Created Successfully!!!")
        elif select_option=="Doctor":
            st.subheader("Create a Doctor Details")
            name1 = st.text_input("Enter Doctor's Name", key="doctor_name")
            spec = st.text_input("Enter Doctor's Specialization", key="doctor_specialization")
            cont = st.text_input("Enter Doctor's Contact Information", key="doctor_contact")
            if st.button("Create Doctor"):
                sql = "INSERT INTO Doctors (Name, Specialization, ContactInformation) VALUES (%s, %s, %s)"
                val = (name1, spec, cont)
                mycursor.execute(sql, val)
                mydb.commit()
                st.success("Doctor Record Created Successfully!!!")
    # elif option=="Create Doctor Details":
        



    elif option=="List Patients And Doctors":
        st.subheader("Patients List")
        mycursor.execute("select * from patients")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)
        st.subheader("Doctors List")
        mycursor.execute("SELECT * FROM doctors")  # Assuming you have a table named "Doctors"
        doctors_result = mycursor.fetchall()
        for row in doctors_result:
            st.write(row)

    elif option=="Delete":
        st.subheader("Delete a Patient Record")
        iddd = st.number_input("Enter ID", min_value=1, key="iddd_patient")
        if st.button("Delete Patient Record"):
            sql = "DELETE FROM patients WHERE PatientID = %s"
            val = (iddd,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Patient Record Deleted Successfully!!!")

        st.subheader("Delete a Doctor Record")
        idd = st.number_input("Enter ID", min_value=1, key="iddd_doctor")
        if st.button("Delete Doctor Record"):
            sql = "DELETE FROM doctors WHERE DoctorID = %s"
            val = (idd,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Doctor Record Deleted Successfully!!!")
    
    elif option=="Book Appointment":
        st.subheader("Book Appointment with Doctor")
        available_patients = get_available_patients()
        patient_options = {patient[0]: patient[1] for patient in available_patients}
        selected_patient_id = st.selectbox("Select Patient", options=list(patient_options.keys()), format_func=lambda x: patient_options[x])
        available_doctors = get_available_doctors()
        doctor_options = {doctor[0]: doctor[1] for doctor in available_doctors}
        selected_doctor_id = st.selectbox("Select Doctor", options=list(doctor_options.keys()), format_func=lambda x: doctor_options[x])
        selected_date_slot = st.date_input("Select preferred Date", key="selected_date_slot")
        selected_time_slot = st.text_input("Enter preferred Time Slot (e.g., '10:00 AM - 11:00 AM')")
        if st.button("Book Appointment"):
            time_slot = datetime.datetime.strptime(selected_time_slot, "%I:%M %p").strftime("%H:%M:%S")
            book_appointment(selected_patient_id,selected_doctor_id,selected_date_slot, time_slot)
            st.success("Appointment booked successfully!")

    elif option=="Manage Appointment":
        doctor = get_available_doctors()
        doctor_options = {doctor[0]: doctor[1] for doctor in doctor}
    # Display list of doctors in sidebar
        selected_doctor = st.sidebar.selectbox("Select Doctor:",  options=list(doctor_options.keys()), format_func=lambda x: doctor_options[x])

        # Get appointments for selected doctor
        appointments = get_appointments_by_doctor(selected_doctor)
        for appointment in appointments:
            st.write(f"Appointment ID: {appointment[0]}")
            st.write(f"Doctor ID: {appointment[1]}")
            st.write(f"Patient ID: {appointment[2]}")
            st.write(f"Appointment Date: {appointment[3]}")
            if st.button(f"Delete Appointment {appointment[0]}"):
                delete_appointment(appointment[0])
                st.success("Appointment deleted successfully!")
                # Refresh appointments after deletion
                appointments = get_appointments_by_doctor(selected_doctor)
        


    elif option=="Edit Details":
        edit_option = st.sidebar.selectbox("Edit:", ["Doctor", "Patient"])
        if edit_option=="Patient":
            st.subheader("Edit Patient Information")
            patient_id = st.number_input("Enter Patient ID to Edit", min_value=1, step=1)
            patient = get_patient_by_id(patient_id)
            if patient:
                    st.write(f"Editing Patient ID: {patient_id}")
                    new_name = st.text_input("Name", value=patient[1])
                    new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient[2]))
                    new_dob = st.date_input("Date of Birth", value=patient[3])
                    new_address = st.text_area("Address", value=patient[4])
                    new_phone = st.text_input("Phone Number", value=patient[5])
                    if st.button("Update Patient"):
                        update_patient(patient_id, new_name, new_gender, new_dob, new_address, new_phone)
                        st.success("Patient information updated successfully!")
            else:
                    st.warning("Patient not found!")

        elif edit_option=="Doctor":
            st.subheader("Edit Doctor Details")
            doctor_id = st.number_input("Enter Doctor ID to Edit", min_value=1, step=1,key="doctor_id")
            doctor = get_doctor_by_id(doctor_id)
            if doctor:
                st.write(f"Editing Doctor ID: {doctor_id}")
                edit_name = st.text_input("Name", value=doctor[1])
                edit_specialization = st.text_input("Specializtion",value=(doctor[2]))
                edit_contact = st.text_input("Contact Information", value=doctor[3])
                if st.button("Update Doctor Details"):
                    update_doctor(doctor_id, edit_name, edit_specialization, edit_contact)
                    st.success("Doctor details updated successfully!")
            else:
                st.warning("Doctor not found!")
    
    elif option=="Search":
        st.sidebar.title("Search Database")

        search_option = st.sidebar.selectbox("Search:", ["Doctor", "Patient"])

        if search_option == "Doctor":
                st.subheader("Search Doctor by ID")
                search_id = st.number_input("Enter Doctor ID to Search", min_value=1, step=1)
                if st.button("Search",key="search_D_by_id"):
                    doctor = get_doctor_by_id(search_id)
                    if doctor:
                        st.write("Doctor Found!")
                        st.write(f"Doctor ID: {doctor[0]}")
                        st.write(f"Name: {doctor[1]}")
                        st.write(f"Specialization: {doctor[2]}")
                        st.write(f"Contact: {doctor[3]}")
                    else:
                        st.warning("Doctor not found!")
                st.subheader("Search Doctor by Name")
                search_name = st.text_input("Enter Doctor Name to Search", key="doctor_name")
                if st.button("Search by Name", key="search_doctor_by_name"):
                    doctors = get_doctor_by_name(search_name)
                    if doctors:
                        st.write(f"{len(doctors)} Doctors Found!")
                        for doctor in doctors:
                            st.write(f"Doctor ID: {doctor[0]}")
                            st.write(f"Name: {doctor[1]}")
                            st.write(f"Specialization: {doctor[2]}")
                            st.write(f"Contact: {doctor[3]}")
                    else:
                        st.warning("Doctor not found!")

        elif search_option == "Patient":
                st.subheader("Search Patient by ID")
                search_id = st.number_input("Enter Patient ID to Search", min_value=1, step=1)
                if st.button("Search",key="search_P_by_id"):
                    patient = get_patient_by_id(search_id)
                    if patient:
                        st.write("Patient Found!")
                        st.write(f"Patient ID: {patient[0]}")
                        st.write(f"Name: {patient[1]}")
                        st.write(f"Gender: {patient[2]}")
                        st.write(f"Date of Birth: {patient[3]}")
                        st.write(f"Address: {patient[4]}")
                        st.write(f"Phone: {patient[5]}")
                    else:
                        st.warning("Patient not found!")
                # st.sidebar.title("Search by Name")
                st.subheader("Search Patient by Name")
                search_name = st.text_input("Enter Patient Name to Search", key="patient_name")
                if st.button("Search by Name", key="search_patient_by_name"):
                    patients = get_patient_by_name(search_name)
                    if patients:
                        st.write(f"{len(patients)} Patients Found!")
                        st.write("-------------------------------------------")
                        for patient in patients:
                            st.write(f"Patient ID: {patient[0]}")
                            st.write(f"Name: {patient[1]}")
                            st.write(f"Gender: {patient[2]}")
                            st.write(f"Date of Birth: {patient[3]}")
                            st.write(f"Address: {patient[4]}")
                            st.write(f"Phone: {patient[5]}")
                            st.write("-------------------------------------------")
                    else:
                        st.warning("Patient not found!")
    elif option=="Patient History":
            st.subheader("Appointment History:")
            patients = get_available_patients()
            patients_options = {patients[0]: patients[1] for patients in patients}
    # Display list of patients in sidebar
            selected_patient = st.sidebar.selectbox("Select Patient:",  options=list(patients_options.keys()), format_func=lambda x: patients_options[x])

            # Get appointment history for selected patient
            appointment_history = get_appointment_history(selected_patient)
            
            if appointment_history:
                for appointment in appointment_history:
                    doct_name=get_doctor_by_id(appointment[2])
                    st.write(f"Appointment ID: {appointment[0]}")
                    st.write(f"Doctor Name: {doct_name[1]}")
                    st.write(f"Appointment Date: {appointment[3]}")
                    st.write("-------------")
            else:
                st.write("No appointment history found for this patient.")
                
if __name__ == "__main__":
    main()








