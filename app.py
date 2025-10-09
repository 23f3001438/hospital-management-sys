import os
from flask import Flask, render_template
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

if __name__ == '__main__':
    adm()
    app.run(debug=True, port=5001)
