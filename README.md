# hospital-management-sys
MAD I project; Sept term

**HealthSync: Bridging the Gap in Healthcare Management**

HealthSync is a full-stack Hospital Management System (HMS) designed to simplify the often chaotic workflows between patients, doctors, and administrators. Built with Flask, this project focuses on role-based logic and seamless appointment scheduling, ensuring that the right people get the right information at the right time.

**Why HealthSync?**

Most healthcare systems struggle with fragmented data. HealthSync addresses this by centralizing department management, doctor availability, and patient medical histories into one intuitive dashboard. Whether it's a doctor updating a prescription or a patient booking their next check-up, the platform handles the heavy lifting of backend validation and session security.

**Key Features**

->Security & Access Control
Role-Specific Portals: Distinct interfaces for Admins, Doctors, and Patients.

Secure Authentication: Powered by Flask sessions and robust password hashing to keep user data private.

-> The Control Center (Admin)
Manage the hospital’s backbone by adding departments and onboarding doctors.

Get a bird's-eye view of hospital activity with appointment statistics.

-> The Clinical Suite (Doctor)
Smart Scheduling: Define availability slots to prevent overbooking.

Patient Care: Access and update medical records and prescriptions in real-time.

-> The Patient Experience
Easy Discovery: Filter doctors by name or specialization.

Flexible Booking: Book, reschedule, or cancel appointments with instant updates.

History at a Glance: Access past medical records and prescriptions anytime.

-> The Tech Stack
Backend: Python & Flask (The engine)

Database: SQLite via SQLAlchemy (Reliable data modeling)

Frontend: HTML5, CSS3, and Jinja2 (Clean, server-side rendered templates)

**Deployment: Render**

**🗄 A Note on Data Persistence**
Currently, HealthSync is deployed on Render’s Free Tier using SQLite.

Heads up: Because Render’s free storage is ephemeral, the database resets whenever the instance restarts. While this is perfect for a quick demo and learning, the system is designed to be "plug-and-play" with PostgreSQL for production environments.

**⚙️ Getting Started Locally**
Ready to explore the code? Follow these steps to get a local instance running:

Clone the Repo:

Bash

git clone https://github.com/23f3001438/hospital-management-sys.git
cd hospital-management-sys
Set Up Your Environment:

Bash

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Launch:

Bash

python app.py
Visit http://127.0.0.1:5000/ and you're good to go!

**📈 What’s Next for HealthSync?**
Persistent Storage: Migrating to PostgreSQL for long-term data retention.

Automated Alerts: Email and SMS notifications for appointment reminders.

Modern UI: Transitioning to a React or Vue frontend for a more dynamic feel.

Mobile API: Building out RESTful endpoints for mobile integration.

**👩‍💻 About the Author**
Archi Mangla B.Tech in Computer Science & Technology. Also pursuing BS in Data Science from IIT Madras. Passionate about building functional, user-centric backend systems and exploring the intersection of UI/UX and data.
