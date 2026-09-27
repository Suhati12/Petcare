# PetCare+ — Smart Pet Vaccination & Care Reminder System

![PetCare+ Banner](https://img.shields.io/badge/Project-PetCare%2B-10b981?style=for-the-badge&logo=shield&logoColor=white)
![Flask](https://img.shields.io/badge/Backend-Python_Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap 5](https://img.shields.io/badge/Frontend-Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![MySQL](https://img.shields.io/badge/Database-MySQL_%2F_SQLite-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

**PetCare+** is a professional, full-featured web application designed to help pet owners manage pet care schedules, vaccinations, deworming, medication, grooming, and veterinary check-ups. Built with Python Flask, Flask-SQLAlchemy, Flask-Login, APScheduler, MySQL/SQLite, Bootstrap 5, and Chart.js, it serves as an exemplary showcase final-year **MCA Academic Project**.

---

## 🌟 Key Features

1. **User Authentication & Authorization**
   - Secure registration, login, logout, profile update, and password reset flow.
   - Strict owner data isolation — users can only view and manage their own pet records.

2. **Pet Profile Management**
   - Multiple pets per owner with species, breed, gender, DOB, weight, color, microchip ID, profile photo upload, allergies, medical conditions, and emergency notes.
   - Dynamic age calculation (`X yrs Y mos`).
   - Unique Emergency QR Code generation per pet.

3. **Vaccination Module**
   - Complete tracking of core/non-core vaccines, administered dates, next due dates, veterinarian, clinic, and attached certificate documents.
   - Dynamic status calculation (`Up to date`, `Due soon` [Within 7 days], `Overdue`).

4. **Deworming & Parasite Care**
   - Record deworming date, medicine, dose, and next due date with auto-generated reminders.

5. **Medication Schedule**
   - Track dosage, purpose, frequency (`Once daily`, `Twice daily`, `Weekly`, `Custom`), time slots, and administration instructions.
   - Separate view for **Active** vs **Completed** medication courses.

6. **Grooming & Hygiene Care**
   - Scheduled reminders for baths, nail trimming, hair trimming, ear cleaning, and dental care.

7. **Veterinary Consultations & Visits**
   - Record upcoming & past clinic visits, reason, diagnosis, treatment, prescription, and attached report files.

8. **Smart Reminder Engine & APScheduler**
   - Automated background daemon scanning due dates every 6 hours.
   - Live **"Run Reminder Engine Now"** button in UI for viva demo convenience.
   - Auto-generates deduplicated in-app notifications.

9. **In-App Notification Center**
   - Navbar unread notification count badge, mark-as-read, and browser push notification support.

10. **Interactive Analytics Dashboard**
    - Stat cards for total pets, vaccines due soon, overdue tasks, active meds, and vet visits.
    - Chart.js visual charts: Care Tasks by Category (Doughnut) & Health Progress Status (Bar).
    - Widgets for Today's Tasks, Upcoming Reminders, and Overdue Alert Banners.

11. **Unified Health Timeline**
    - Combined vertical chronological timeline of all medical events across vaccinations, medications, deworming, grooming, and vet visits.

12. **Printable Medical Dossier & Export**
    - One-click print-ready pet medical summary report formatted for veterinary visits.

13. **RESTful API Endpoints**
    - Structured JSON endpoints for `/api/pets`, `/api/reminders`, and `/api/notifications`.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Custom Emerald Pet Care Theme), JavaScript (ES6+), Bootstrap 5, FontAwesome 6, Chart.js.
- **Backend**: Python 3.13, Flask 3.0, Flask-SQLAlchemy, Flask-Login, APScheduler, Werkzeug, PyMySQL.
- **Database**: MySQL (Default schema provided) with seamless **SQLite** fallback for zero-setup local runs.

---

## 🚀 Step-by-Step Installation & Setup Guide (Windows + VS Code)

### Prerequisites
- Python 3.8+ installed
- VS Code editor installed

### Step 1: Clone / Open Project in VS Code
Open VS Code, navigate to `File > Open Folder`, and select the `petcare` directory.

### Step 2: Open Terminal & Setup Virtual Environment
```bash
# Open PowerShell or Command Prompt in VS Code (Ctrl + ~)
py -m venv venv

# Activate Virtual Environment (Windows)
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup Options

#### Option A: Quick Run with SQLite (Zero Configuration)
By default, PetCare+ runs instantly with SQLite (`petcare.db`). No database installation is required!

#### Option B: Run with MySQL Database
If you wish to use MySQL for production or viva presentation:
1. Open your MySQL client (XAMPP, MySQL Workbench, or Command Line).
2. Execute the raw SQL schema provided in `database/schema.sql`:
   ```sql
   SOURCE database/schema.sql;
   ```
3. Set environment variable or toggle in `config.py`:
   ```env
   USE_MYSQL=True
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_HOST=localhost
   MYSQL_DB=petcare_db
   ```

### Step 5: Seed Realistic Demo Data
Run the seed script to populate demo users, pets, vaccination history, medication schedules, and notifications:
```bash
py seed.py
```

### Step 6: Start Flask Server
```bash
py app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🔑 Demo Login Credentials

| Role | Email Address | Password | Sample Pets |
| :--- | :--- | :--- | :--- |
| **Primary User** | `alex@petcare.com` | `password123` | Max (Golden Retriever), Bella (Persian Cat) |
| **Secondary User** | `sarah@petcare.com` | `password123` | Charlie (Beagle), Luna (Siamese Cat) |
| **Tertiary User** | `david@petcare.com` | `password123` | Coco (Holland Lop Rabbit) |

---

## 📡 REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/pets` | `GET` | List all pets for authenticated user |
| `/api/pets/<id>` | `GET` | Get detailed JSON object of a single pet |
| `/api/pets` | `POST` | Create a new pet via JSON payload |
| `/api/pets/<id>` | `PUT` | Update pet profile |
| `/api/pets/<id>` | `DELETE` | Delete pet profile |
| `/api/reminders` | `GET` | List active care reminders |
| `/api/notifications` | `GET` | Fetch notification history |

---

## 📁 Project Structure

```
petcare/
├── app.py                   # Application Factory & Entry Point
├── config.py                # Environment & Database Configurations
├── seed.py                  # Seed Data Populator
├── requirements.txt         # Project Dependencies
├── README.md                # Installation & API Documentation
├── COLLEGE_PROJECT_DOCS.md  # Academic MCA System Documentation
├── TESTING_REPORT.md        # Comprehensive Test Cases Table
│
├── models/                  # SQLAlchemy ORM Data Models
│   ├── user.py
│   ├── pet.py
│   ├── vaccination.py
│   ├── deworming.py
│   ├── medication.py
│   ├── grooming.py
│   ├── vet_visit.py
│   ├── reminder.py
│   └── notification.py
│
├── routes/                  # Controller Blueprints
│   ├── auth.py
│   ├── main.py
│   ├── pets.py
│   ├── vaccinations.py
│   ├── dewormings.py
│   ├── medications.py
│   ├── groomings.py
│   ├── vet_visits.py
│   ├── reminders.py
│   ├── notifications.py
│   ├── timeline.py
│   ├── reports.py
│   └── api.py
│
├── services/                # Business Logic & Engine Services
│   ├── reminder_engine.py
│   ├── notification_service.py
│   └── qr_generator.py
│
├── static/                  # Custom CSS, JS & Upload Directories
│   ├── css/style.css
│   ├── js/dashboard.js
│   ├── js/notifications.js
│   └── js/main.js
│
├── templates/               # Jinja2 Modular HTML Templates
└── database/
    └── schema.sql           # MySQL DDL Schema
```
