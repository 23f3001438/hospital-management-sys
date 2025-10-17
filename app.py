import os
from flask import Flask, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, Patient, Doctor, Admin, Department, Appointment, MedicalRecord, Treatment, DoctorAvailability
from datetime import datetime, date, timedelta, time


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

    # When search is performed
    if query:
        q = f"%{query}%"

        # Doctor search
        if category == 'doctor':
            doctors = doctors.filter(
                (Doctor.name.ilike(q)) |
                (Doctor.username.ilike(q)) |
                (Doctor.email.ilike(q)) |
                (Doctor.specialization.ilike(q)) |
                (Doctor.contact.ilike(q))
            ).all()
            patients, departments = [], []

        # Patient search
        elif category == 'patient':
            patients = patients.filter(
                (Patient.first_name.ilike(q)) |
                (Patient.last_name.ilike(q)) |
                (Patient.username.ilike(q)) |
                (Patient.email.ilike(q)) |
                (Patient.contact.ilike(q)) |
                (Patient.id.cast(db.String).ilike(q))
            ).all()
            doctors, departments = [], []

        # Search across all
        else:
            doctors = doctors.filter(
                (Doctor.name.ilike(q)) |
                (Doctor.username.ilike(q)) |
                (Doctor.email.ilike(q)) |
                (Doctor.specialization.ilike(q)) |
                (Doctor.contact.ilike(q))
            ).all()

            patients = patients.filter(
                (Patient.first_name.ilike(q)) |
                (Patient.last_name.ilike(q)) |
                (Patient.username.ilike(q)) |
                (Patient.email.ilike(q)) |
                (Patient.contact.ilike(q)) |
                (Patient.id.cast(db.String).ilike(q))
            ).all()

            departments = departments.filter(
                (Department.name.ilike(q)) |
                (Department.description.ilike(q))
            ).all()

    # If no query, fetch everything normally
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

@app.route('/patientdb/<int:patient_id>')
def patientdb(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    today = date.today()

    # Upcoming appointments: Scheduled and future dates
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.status == 'Scheduled',
        Appointment.date >= today
    ).order_by(Appointment.date).all()

    # Past appointments: Completed or Cancelled or date in past
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        ((Appointment.status == 'Completed') | (Appointment.status == 'Cancelled') | (Appointment.date < today))
    ).order_by(Appointment.date.desc()).all()

    departments = Department.query.all()

    return render_template(
        'patientdb.html',
        patient=patient,
        upcoming_appointments=upcoming_appointments,
        past_appointments=past_appointments,
        departments=departments
    )


@app.route('/docdb/<int:doctor_id>')
def docdb(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    today = date.today()
    next_week = [today + timedelta(days=i) for i in range(7)]

    # All upcoming appointments for this doctor (next 7 days)
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date.between(today, today + timedelta(days=7)),
        Appointment.status == 'Scheduled'
    ).all()

    # Unique patients assigned
    assigned_patients = {appt.patient for appt in appointments}

    # Availability for next 7 days
    availability = {d: DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=d).all() for d in next_week}

    return render_template(
        'docdb.html',
        doctor=doctor,
        appointments=appointments,  # list of appointments
        assigned_patients=assigned_patients,
        availability=availability,
        dates=next_week
    )


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

    patient_id = request.args.get("patient_id")
    patient = Patient.query.get(patient_id) if patient_id else None

    upcoming_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Scheduled').all()
    assigned_patients = Patient.query.join(Appointment).filter(Appointment.doctor_id == doctor.id).all()
        
    return render_template(
    'docprofile.html',
    doctor=doctor,
    appointments=upcoming_appointments,
    assigned_patients=assigned_patients,
    patient=patient  # pass the current patient here
)


@app.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admindb'))



@app.route('/appointment/<int:appointment_id>/complete')
def mark_complete(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'Completed'
    db.session.commit()
    flash("Appointment marked as completed.", "success")
    return redirect(url_for('docdb', doctor_id=appointment.doctor_id))


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
    department = Department.query.get_or_404(dept_id)
    doctors = Doctor.query.filter_by(specialization=department.name).all()
    
    for doctor in doctors:
        doctor.num_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Scheduled').count()
    
    # Get patient_id from query string
    patient_id = request.args.get("patient_id")
    patient = Patient.query.get(patient_id) if patient_id else None

    return render_template(
        'viewdep.html',
        department=department,
        doctors=doctors,
        patient=patient   # ✅ pass patient
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

@app.route('/appointment/<int:appointment_id>/record', methods=['GET', 'POST'])
def record_details(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == 'POST':
        # Update appointment status if needed
        appointment.status = 'Completed'  # or let the doctor choose separately

        # Update medical record
        record = MedicalRecord.query.filter_by(appointment_id=appointment.id).first()
        if not record:
            record = MedicalRecord(appointment_id=appointment.id)
        
        record.patient_id = appointment.patient_id
        record.date = appointment.date
        record.description = f"Visit with Dr. {appointment.doctor.name}"
        record.diagnosis = request.form['diagnosis']
        record.treatment = request.form['treatment']
        record.prescription = request.form['prescription']

        db.session.add(record)
        db.session.commit()
        flash("Appointment details saved successfully", "success")
        return redirect(url_for('docdb', doctor_id=appointment.doctor_id))

    # GET request: show form prefilled if record exists
    record = MedicalRecord.query.filter_by(appointment_id=appointment.id).first()
    return render_template('medical_history.html', appointment=appointment, record=record)


@app.route('/doctor/<int:doctor_id>/availability', methods=['GET', 'POST'])
def doctor_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    today = date.today()
    next_week = [today + timedelta(days=i) for i in range(7)]

    # Handle POST: save availability
    if request.method == 'POST':
        date_str = request.form.get('date')
        selected_hours = request.form.getlist('times')

        if not date_str or not selected_hours:
            flash('Please select a date and at least one time slot.', 'warning')
            return redirect(url_for('doctor_availability', doctor_id=doctor_id))

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Ensure all slots from 10-18 exist
        for hour in range(10, 18):
            slot_time = time(hour, 0)
            slot = DoctorAvailability.query.filter_by(
                doctor_id=doctor.id, date=date_obj, time=slot_time
            ).first()

            # Slot selected by doctor
            if str(hour) in selected_hours:
                if slot:
                    # Only mark available if not already booked
                    if not Appointment.query.filter_by(
                        doctor_id=doctor.id, date=date_obj, time=slot_time, status='Scheduled'
                    ).first():
                        slot.is_available = True
                else:
                    db.session.add(DoctorAvailability(
                        doctor_id=doctor.id,
                        date=date_obj,
                        time=slot_time,
                        is_available=True
                    ))
            else:
                # Unselected: mark unavailable only if not booked
                if slot and not Appointment.query.filter_by(
                    doctor_id=doctor.id, date=date_obj, time=slot_time, status='Scheduled'
                ).first():
                    slot.is_available = False

        db.session.commit()
        flash('Availability updated successfully!', 'success')
        return redirect(url_for('doctor_availability', doctor_id=doctor_id))

    # GET: prepare availability dictionary
    availability = {}
    for d in next_week:
        all_slots = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id, date=d
        ).all()
        booked_times = [a.time for a in Appointment.query.filter_by(
            doctor_id=doctor.id, date=d, status='Scheduled'
        ).all()]
        availability[d] = {slot.time: slot.is_available and slot.time not in booked_times for slot in all_slots}

    # Optional: track selected_date if coming from query parameter
    selected_date_str = request.args.get('date')
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else None

    return render_template(
        'availability.html',
        doctor=doctor,
        doctor_id=doctor.id,
        dates=next_week,
        availability=availability,
        selected_date=selected_date
    )

@app.route("/book_appointment/<int:doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):
    patient_id = request.args.get("patient_id") or request.form.get("patient_id")
    if not patient_id:
        flash("Patient not selected!", "danger")
        return redirect(url_for("home"))
    patient_id = int(patient_id)

    doctor = Doctor.query.get_or_404(doctor_id)
    selected_date_str = request.form.get("date") or request.args.get("date")
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else None

    # Fetch all available slots for selected date
    available_times = []
    if selected_date:
        slots = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=selected_date,
            is_available=True
        ).all()

        booked_times = [a.time for a in Appointment.query.filter_by(
            doctor_id=doctor.id,
            date=selected_date,
            status='Scheduled'
        ).all()]

        # Only include times that are available and not booked
        available_times = [s.time for s in slots if s.time not in booked_times]

    # Prepare unique available dates
    dates_query = DoctorAvailability.query.filter_by(
        doctor_id=doctor.id,
        is_available=True
    ).with_entities(DoctorAvailability.date).distinct().all()
    available_dates = sorted([d[0] for d in dates_query])

    # Handle booking POST
    if request.method == "POST" and "time" in request.form:
        time_str = request.form["time"]
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        # Verify slot is still available
        slot = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=selected_date,
            time=time_obj,
            is_available=True
        ).first()

        if not slot or Appointment.query.filter_by(
            doctor_id=doctor.id,
            date=selected_date,
            time=time_obj,
            status='Scheduled'
        ).first():
            flash("This time slot is already booked. Please select another.", "danger")
            return redirect(url_for("book_appointment", doctor_id=doctor.id, patient_id=patient_id, date=selected_date))

        # Mark slot unavailable immediately
        slot.is_available = False

        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor.id,
            date=selected_date,
            time=time_obj,
            status="Scheduled"
        )
        db.session.add(appointment)
        db.session.commit()

        flash("Appointment booked successfully!", "success")
        return redirect(url_for("patientdb", patient_id=patient_id))

    return render_template(
        "book_appointment.html",
        doctor=doctor,
        available_dates=available_dates,
        selected_date=selected_date,
        available_times=available_times,
        patient_id=patient_id
    )


@app.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Free up that slot
    availability = DoctorAvailability.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        time=appointment.time
    ).first()
    
    if availability:
        availability.is_available = True

    appointment.status = 'Cancelled'
    db.session.commit()
    flash("Appointment cancelled successfully!", "info")
    
    # Pass patient_id in redirect
    return redirect(url_for('patientdb', patient_id=appointment.patient_id))


@app.route('/appointment/<int:appointment_id>/reschedule', methods=['GET', 'POST'])
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = appointment.doctor

    selected_date_str = request.form.get('date') or request.args.get('date')
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else None

    # Fetch distinct available dates for this doctor
    available_dates_query = DoctorAvailability.query.filter_by(
        doctor_id=doctor.id, is_available=True
    ).with_entities(DoctorAvailability.date).distinct().all()
    available_dates = [d[0] for d in available_dates_query]

    # Fetch available times for selected date
    available_times = []
    if selected_date:
        slots = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=selected_date,
            is_available=True
        ).all()

        # Remove times already booked
        booked_times = [a.time for a in Appointment.query.filter_by(
            doctor_id=doctor.id,
            date=selected_date,
            status='Scheduled'
        ).all() if a.id != appointment.id]  # exclude current appointment

        available_times = [s.time for s in slots if s.time not in booked_times]

    # Handle POST booking
    if request.method == 'POST' and 'time' in request.form:
        new_date_str = request.form['date']
        new_time_str = request.form['time']

        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        new_time = datetime.strptime(new_time_str, "%H:%M").time()

        # Check if new slot is still available and not booked
        slot = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=new_date,
            time=new_time,
            is_available=True
        ).first()
        if not slot or Appointment.query.filter_by(
            doctor_id=doctor.id,
            date=new_date,
            time=new_time,
            status='Scheduled'
        ).first():
            flash("Selected slot is no longer available.", "danger")
            return redirect(url_for('reschedule_appointment', appointment_id=appointment.id, date=new_date_str))

        # Free old slot
        old_slot = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=appointment.date,
            time=appointment.time
        ).first()
        if old_slot:
            old_slot.is_available = True

        # Assign new slot
        appointment.date = new_date
        appointment.time = new_time
        slot.is_available = False

        db.session.commit()
        flash("Appointment rescheduled successfully!", "success")
        return redirect(url_for('patientdb', patient_id=appointment.patient_id))

    return render_template(
        'reschedule_appointment.html',
        appointment=appointment,
        doctor=doctor,
        available_dates=available_dates,
        selected_date=selected_date,
        available_times=available_times
    )


@app.route('/appointment/<int:id>/update_status', methods=['POST'])
def update_appointment_status(id):
    appointment = Appointment.query.get_or_404(id)
    new_status = request.form.get('status')
    appointment.status = new_status
    db.session.commit()
    flash('Appointment status updated.', 'success')
    return redirect(url_for('docdb', doctor_id=appointment.doctor_id))


@app.route('/doctors')
def view_doctors():
    search_name = request.args.get('name', '').strip()
    search_specialization = request.args.get('specialization', '').strip()

    # Base query
    doctors = Doctor.query

    # Apply filters if provided
    if search_name:
        doctors = doctors.filter(Doctor.name.ilike(f'%{search_name}%'))
    if search_specialization:
        doctors = doctors.filter(Doctor.specialization.ilike(f'%{search_specialization}%'))

    doctors = doctors.all()
    return render_template('doctors.html', doctors=doctors, search_name=search_name, search_specialization=search_specialization)

@app.route("/search_doctors/<int:patient_id>")
def search_doctors(patient_id):
    query = request.args.get("query", "").strip()
    patient = Patient.query.get_or_404(patient_id)

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for("patientdb", patient_id=patient_id))

    q = f"%{query}%"
    doctors = Doctor.query.filter(
        (Doctor.name.ilike(q)) | (Doctor.specialization.ilike(q))
    ).all()

    for doctor in doctors:
        doctor.num_appointments = Appointment.query.filter_by(doctor_id=doctor.id, status='Scheduled').count()

    return render_template(
        "search_results.html",
        doctors=doctors,
        query=query,
        patient=patient
    )


@app.route('/admin/appointments')
def admin_appointments():
    from datetime import date
    today = date.today()
    appointments = Appointment.query.all()

    upcoming_appointments = [a for a in appointments if a.date >= today and a.status != 'Cancelled']
    past_appointments = [a for a in appointments if a.date < today or a.status in ['Cancelled', 'Completed']]

    return render_template(
        'admin_appointments.html',
        upcoming_appointments=upcoming_appointments,
        past_appointments=past_appointments
    )



if __name__ == '__main__':
    adm()
    app.run(debug=True, port=5001)
