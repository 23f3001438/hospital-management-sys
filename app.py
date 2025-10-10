import os
from flask import Flask, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, Patient, Doctor, Admin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'archimangla'


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'hms_am.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # create instance folder if it doesn't exist

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def adm():
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        admin = Admin.query.filter_by(username='archimangla1409').first()
        if not admin:
            admin = Admin(username='archimangla1409', contact=1234567890, password='archi123', name='Archi Mangla')
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
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        email = request.form.get('email')
        address = request.form.get('address')
        password = request.form.get('password')
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        existing_user = Patient.query.filter(
            Patient.username == username | Patient.email == email | Patient.contact == contact
        ).first()

        if existing_user:
            flash('User with this username, email, or contact already exists.', 'danger')
            return redirect('/register')
        
        new_patient = Patient(
            name=f"{firstName} {lastName}",
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

        if role == 'patient':
            user = Patient.query.filter_by(username=username).first()
        elif role == 'doctor':
            user = Doctor.query.filter_by(username=username).first()
        elif role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        else:
            flash('Invalid role selected.', 'danger')
            return redirect('/login')

        if user and check_password_hash(user.password, password):
            flash(f'Login successful as {role}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect('/login')

    return render_template('login.html')

@app.route('/admindb')
def admindb():
    doctors = Doctor.query.all()
    admins = Admin.query.all()
    return render_template('admindb.html', doctors=doctors, admins=admins)

@app.route('/patientdb')
def patientdb():
    patients = Patient.query.all()
    return render_template('patientdb.html', patients=patients)

@app.route('/docdb')
def docdb():
    doctors = Doctor.query.all()
    return render_template('docdb.html', doctors=doctors)

@app.route('/createdoc', methods=['GET', 'POST'])
def createdoc():
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
            flash('Doctor with this username or contact already exists.', 'danger')
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

    return render_template('createdoc.html')

@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.username = request.form.get('username')
        specialization = request.form.get('specialization')
        contact = request.form.get('contact')
        email = request.form.get('email')

        existing_user = Doctor.query.filter(
            ((Doctor.username == doctor.username) | 
            (Doctor.contact == contact) | 
            (Doctor.email == email)) & 
            (Doctor.id != doctor.id)
        ).first()

        if existing_user:
            flash('Another doctor with this username, email, or contact already exists.', 'danger')
            return redirect(f'/edit_doctor/{doctor_id}')

        doctor.specialization = specialization
        doctor.contact = contact
        doctor.email = email

        db.session.commit()
        flash('Doctor details updated successfully!', 'success')
        return redirect(url_for('admindb'))

    return render_template('editdoc.html', doctor=doctor)


@app.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admindb'))
if __name__ == '__main__':
    adm()
    app.run(debug=True, port=5001)
