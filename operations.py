import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="Hospital_management"
    
)
mycursor=mydb.cursor()
print("Connection Established")


def delete_appointments():
    mycursor.execute

def get_available_doctors():
    mycursor.execute("SELECT * FROM Doctors")
    return mycursor.fetchall()


def get_available_patients():
    mycursor.execute("SELECT * FROM Patients")
    return mycursor.fetchall()


def get_patient_by_id(patient_id):
    mycursor.execute('SELECT * FROM Patients WHERE patientID=%s', (patient_id,))
    patient = mycursor.fetchone()
    return patient

def get_doctor_by_id(doctor_id):
    mycursor.execute('SELECT * FROM doctors WHERE doctorID=%s', (doctor_id,))
    doctor = mycursor.fetchone()
    return doctor

def get_doctor_by_name(doctor_name):
    mycursor.execute('SELECT * FROM doctors WHERE Name=%s', (doctor_name,))
    doctor = mycursor.fetchall()
    return doctor

def get_patient_by_name(patient_name):
    mycursor.execute('SELECT * FROM patients WHERE Name=%s', (patient_name,))
    patient = mycursor.fetchall()
    return patient

def update_doctor(doctor_id, new_name, new_specialization, new_contact):
    mycursor.execute('''UPDATE Doctors
                        SET name=%s, specialization=%s, contactinformation=%s
                        WHERE doctorid=%s''', (new_name, new_specialization, new_contact, doctor_id))
    mydb.commit()

# Function to update patient information
def update_patient(patient_id, name, gender, dob, address, phone):
    mycursor.execute('''UPDATE Patients
                      SET name=%s, gender=%s, DateOfBirth=%s, address=%s, phonenumber=%s
                      WHERE Patientid=%s''', (name, gender, dob, address, phone, patient_id))
    mydb.commit()

def book_appointment(patient_id,doctor_id,date_slot, time_slot):
    sql = "INSERT INTO appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) VALUES (%s, %s,%s, %s)"
    val = (patient_id, doctor_id,date_slot, time_slot)
    mycursor.execute(sql, val)
    mydb.commit()

    history_sql = "INSERT INTO AppointmentHist (AppointmentID, PatientID, DoctorID, AppointmentDate, AppointmentTime) VALUES (LAST_INSERT_ID(), %s, %s, %s, %s)"
    history_val = (patient_id, doctor_id, date_slot, time_slot)
    mycursor.execute(history_sql, history_val)
    mydb.commit()

def get_doctor_appointments(doctor_id):
    mycursor.execute("SELECT AppointmentDate, AppointmentTime FROM Appointments WHERE DoctorID = %s", (doctor_id,))
    return mycursor.fetchall()

def get_appointments_by_doctor(doctor_id):
    mycursor.execute('SELECT * FROM appointments WHERE DoctorID = %s', (doctor_id,))
    appointments = mycursor.fetchall()
    return appointments

# Function to delete appointment by appointment ID
def delete_appointment(appointment_id):
    mycursor.execute('DELETE FROM appointments WHERE AppointmentID = %s', (appointment_id,))
    mydb.commit()

def get_appointment_history(patient_id):
    sql = "SELECT * FROM AppointmentHist WHERE PatientID = %s"
    val = (patient_id,)
    mycursor.execute(sql, val)
    appointment_history = mycursor.fetchall()
    return appointment_history