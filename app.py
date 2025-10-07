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

with app.app_context():
    db.create_all()  

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
