from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String())
    username = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String())
    username = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    contact = db.Column(db.String, nullable=False)
    specialisation = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String, nullable=False)
    name = db.Column(db.String(), nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')

    patient = db.relationship('Patient', backref=db.backref('applications', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('applications', lazy=True))

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    medications = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)

    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('prescriptions', lazy=True))

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text)

    patient = db.relationship('Patient', backref=db.backref('medical_records', lazy=True))

class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_date = db.Column(db.Date, nullable=False)
    details = db.Column(db.Text)

    patient = db.relationship('Patient', backref=db.backref('billings', lazy=True))

class HospitalAccounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_revenue = db.Column(db.Float, nullable=False, default=0.0)
    total_expenses = db.Column(db.Float, nullable=False, default=0.0)

    def update_revenue(self, amount):
        self.total_revenue += amount

    def update_expenses(self, amount):
        self.total_expenses += amount

