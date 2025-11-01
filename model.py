from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    role = db.Column(db.String(20), default='Patient', nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    treatments = db.relationship('Treatment', backref='patient', lazy=True)
    
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='Active', server_default='Active', nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    treatments = db.relationship('Treatment', backref='doctor', lazy=True)
    open_dates = db.Column(db.Text)  # Comma-separated dates
    role = db.Column(db.String(20), default='Doctor', nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Scheduled')
    
    medical_record = db.relationship('MedicalRecord', backref='appointment', uselist=False)



class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis = db.Column(db.String(500))
    treatment = db.Column(db.String(500))
    prescription = db.Column(db.String(500))
    date = db.Column(db.Date, nullable=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)  # <-- new description field

class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)


class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    treatment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float, nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String, nullable=False)
    name = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(20), default='Admin', nullable=False)
