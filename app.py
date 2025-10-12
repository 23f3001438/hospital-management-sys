import os
from flask import Flask, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, Patient, Doctor, Admin, Department, Appointment, MedicalRecord, Treatment
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'archimangla'


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'hms_am.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # create instance folder if it doesn't exist
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from werkzeug.security import generate_password_hash

def adm():
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        admin = Admin.query.filter_by(username='archimangla1409').first()
        if not admin:
            hashed_pw = generate_password_hash('archi123', method='pbkdf2:sha256')
            admin = Admin(username='archimangla1409', contact=1234567890, password=hashed_pw, name='Archi Mangla')
            db.session.add(admin)
            db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        username = request.form.get('username')
        dob_str = request.form['dob'] 
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        email = request.form.get('email')
        address = request.form.get('address')
        password = request.form.get('password')
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        existing_user = Patient.query.filter(
    (Patient.username == username) |
    (Patient.email == email) |
    (Patient.contact == contact)
).first()


        if existing_user:
            flash('User with this username, email, or contact already exists.', 'danger')
            return redirect('/register')
        
        
        new_patient = Patient(
            first_name=firstName,
            last_name=lastName,
            username=username,
            dob=dob,
            gender=gender,
            contact=contact,
            email=email,
            address=address,
            password=hashed_password
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('Registration successful!, Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        # Identify user by role
        if role == 'patient':
            user = Patient.query.filter_by(username=username).first()
        elif role == 'doctor':
            user = Doctor.query.filter_by(username=username).first()
        elif role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        else:
            flash('Invalid role selected.', 'danger')
            return redirect('/login')

        # Check if user exists
        if not user:
            flash('Invalid username or password.', 'danger')
            return redirect('/login')

        # Check if user is blacklisted
        if role in ['patient', 'doctor'] and getattr(user, 'status', '').lower() == 'blacklisted':
            flash('Login prohibited: You are blacklisted by admin.', 'danger')
            return redirect('/login')

        # Validate password
        if check_password_hash(user.password, password):
            flash(f'Login successful as {role}!', 'success')

            # Redirect based on role
            if role == 'patient':
                return redirect(url_for('patientdb', patient_id=user.id))
            elif role == 'doctor':
                return redirect(url_for('docdb', doctor_id=user.id))
            elif role == 'admin':
                return redirect(url_for('admindb'))

        else:
            flash('Invalid username or password.', 'danger')
            return redirect('/login')

    return render_template('login.html')





@app.route('/admindb')
def admindb():
    query = request.args.get('query', '').strip()
    category = request.args.get('category', 'all')

    doctors = Doctor.query
    patients = Patient.query
    departments = Department.query
    admins = Admin.query.all()

    if query:
        q = f"%{query}%"
        if category == 'doctor':
            doctors = doctors.filter(
                (Doctor.name.ilike(q)) |
                (Doctor.username.ilike(q)) |
                (Doctor.email.ilike(q))
            ).all()
            patients = []
            departments = []
        elif category == 'patient':
            patients = patients.filter(
                (Patient.first_name.ilike(q)) |
                (Patient.last_name.ilike(q)) |
                (Patient.username.ilike(q)) |
                (Patient.email.ilike(q))
            ).all()
            doctors = []
            departments = []
        elif category == 'department':
            departments = departments.filter(
                (Department.name.ilike(q)) |
                (Department.description.ilike(q))
            ).all()
            doctors = []
            patients = []
        else:  # all
            doctors = doctors.filter(
                (Doctor.name.ilike(q)) |
                (Doctor.username.ilike(q)) |
                (Doctor.email.ilike(q))
            ).all()
            patients = patients.filter(
                (Patient.first_name.ilike(q)) |
                (Patient.last_name.ilike(q)) |
                (Patient.username.ilike(q)) |
                (Patient.email.ilike(q))
            ).all()
            departments = departments.filter(
                (Department.name.ilike(q)) |
                (Department.description.ilike(q))
            ).all()
    else:
        doctors = doctors.all()
        patients = patients.all()
        departments = departments.all()

    return render_template(
        'admindb.html',
        doctors=doctors,
        admins=admins,
        patients=patients,
        departments=departments,
        search_query=query
    )



@app.route('/patient_dashboard/<int:patient_id>')
def patient_dashboard(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    departments = Department.query.all()
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return render_template(
        'patientdb.html',
        patient=patient,
        departments=departments,
        appointments=appointments
    )

@app.route('/docdb/<int:doctor_id>')
def docdb(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('docdb.html', doctor=doctor)



@app.route('/createdoc', methods=['GET', 'POST'])
def createdoc():
    departments = Department.query.all()
    print("Departments:", departments)  # just to verify data

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        specialization = request.form.get('specialization')
        contact = request.form.get('contact')
        email = request.form.get('email')

        existing_user = Doctor.query.filter(
            (Doctor.username == username) | 
            (Doctor.contact == contact) | 
            (Doctor.email == email)
        ).first()

        if existing_user:
            flash('Doctor with this username, contact, or email already exists.', 'danger')
            return redirect('/createdoc')
        
        new_doctor = Doctor(
            name=name,
            username=username,
            specialization=specialization,
            password=hashed_password,
            contact=contact,
            email=email,
        )
        db.session.add(new_doctor)
        db.session.commit()
        flash('Doctor created successfully!', 'success')
        return redirect(url_for('admindb'))

    # Pass departments to template for the dropdown
    return render_template('createdoc.html', departments=departments)


@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    departments = Department.query.all()  # fetch all departments
    print("Departments:", departments) 

    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.username = request.form.get('username')
        doctor.specialization = request.form.get('specialization')
        doctor.contact = request.form.get('contact')
        doctor.email = request.form.get('email')

        existing_user = Doctor.query.filter(
            ((Doctor.username == doctor.username) | 
             (Doctor.contact == doctor.contact) | 
             (Doctor.email == doctor.email)) &
            (Doctor.id != doctor.id)
        ).first()

        if existing_user:
            flash('Another doctor with this username, email, or contact already exists.', 'danger')
            return redirect(url_for('edit_doctor', doctor_id=doctor.id))

        db.session.commit()
        flash('Doctor details updated successfully!', 'success')
        return redirect(url_for('admindb'))

    return render_template('editdoc.html', doctor=doctor, departments=departments)

@app.route('/view_doctor/<int:doctor_id>')
def view_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    upcoming_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Scheduled').all()
    assigned_patients = Patient.query.join(Appointment).filter(Appointment.doctor_id == doctor.id).all()

    return render_template(
        'docprofile.html',
        doctor=doctor,
        appointments=upcoming_appointments,
        assigned_patients=assigned_patients
    )


@app.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admindb'))



@app.route('/mark_complete/<int:appointment_id>')
def mark_complete(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'Completed'
    db.session.commit()
    flash('Appointment marked as complete.', 'success')
    return redirect(request.referrer or url_for('view_doctor', doctor_id=appointment.doctor_id))

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST', 'GET'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled.', 'success')
        return redirect(request.referrer or url_for('view_doctor', doctor_id=appointment.doctor_id))
    return render_template('confirm_cancel.html', appointment=appointment)

@app.route('/view_patient_profile/<int:patient_id>')
def view_patient_profile(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    # Render a template showing full patient profile
    return render_template('patient_profile.html', patient=patient)


@app.route('/logout')
def logout():
    # Logic for logging out the user
    flash('You have been logged out.', 'success')
    return redirect('/')

@app.route('/patientdb/<int:patient_id>')
def patientdb(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    departments = Department.query.all()
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return render_template(
        'patientdb.html',
        patient=patient,
        departments=departments,
        appointments=appointments
    )


@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.username = request.form.get('username')
        dob_str = request.form.get('dob')
        patient.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        patient.gender = request.form.get('gender')
        patient.contact = request.form.get('contact')
        patient.email = request.form.get('email')
        patient.address = request.form.get('address')

        db.session.commit()
        flash('Patient details updated successfully!', 'success')
        return redirect(url_for('view_patient_profile', patient_id=patient.id))

    return render_template('editp.html', patient=patient)

@app.route('/delete_patient/<int:patient_id>')
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('admindb'))



@app.route('/view_department/<int:dept_id>')
def view_department(dept_id):
    # Get the department
    department = Department.query.get_or_404(dept_id)
    
    # Get doctors in this department
    doctors = Doctor.query.filter_by(specialization=department.name).all()
    
    # Precompute upcoming appointment count for each doctor
    for doctor in doctors:
        doctor.num_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Scheduled').count()
    
    # Render template
    return render_template(
        'viewdep.html',
        department=department,
        doctors=doctors
    )

@app.route('/blacklist_doctor/<int:doctor_id>')
def blacklist_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.status = 'Blacklisted'
    db.session.commit()
    flash(f"Doctor {doctor.name} has been blacklisted.", "success")
    return redirect(url_for('admindb'))

@app.route('/unblacklist_doctor/<int:doctor_id>')
def unblacklist_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.status = 'Active'
    db.session.commit()
    flash(f"Doctor {doctor.name} has been unblocked.", "success")
    return redirect(url_for('admindb'))



@app.route('/blacklist_patient/<int:patient_id>')
def blacklist_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.status = 'Blacklisted'
    db.session.commit()
    return redirect(url_for('admindb'))

@app.route('/unblacklist_patient/<int:patient_id>')
def unblacklist_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.status = 'Active'
    db.session.commit()
    return redirect(url_for('admindb'))



@app.route('/createdep', methods=['GET', 'POST'])
def create_department():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')  # get description from form

        existing_department = Department.query.filter_by(name=name).first()
        if existing_department:
            flash('Department with this name already exists.', 'danger')
            return redirect('/createdep')

        new_department = Department(name=name, description=description)  # save description
        db.session.add(new_department)
        db.session.commit()
        flash('Department created successfully!', 'success')
        return redirect(url_for('admindb'))

    return render_template('createdep.html')


@app.route('/editdep/<int:department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    department = Department.query.get_or_404(department_id)
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.description = request.form.get('description')  # <-- add this
        db.session.commit()
        flash('Department details updated successfully!', 'success')
        return redirect(url_for('admindb'))
    return render_template('editdep.html', department=department)


@app.route('/deletedep/<int:department_id>')
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('admindb'))


if __name__ == '__main__':
    adm()
    app.run(debug=True, port=5001)
