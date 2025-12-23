# 🔴 RedConnect – Blood Donation Management System

RedConnect is a web-based blood donation management system developed as an academic project for the BSc in Computer Science & Engineering program at Port City International University.

## Features
- User registration and authentication
- Blood donor search by blood group and location
- Blood request management system
- Donation history tracking
- Admin dashboard and notifications
- Role-based access control (Admin / User)

## Technology Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, Jinja2
- **Database:** SQLite

## Database Design
The system uses a normalized relational database with entities:
- Users
- Blood Requests
- Donations
- Blood Stock
- Notifications

(ER Diagram available in `/docs` folder)

## How to Run the Project

```bash
pip install -r requirements.txt
python app.py

## License

This project is licensed under the MIT License.
