# PETCARE+ COMPREHENSIVE SYSTEM TESTING REPORT

This report documents the software testing cases executed for the **PetCare+ — Smart Pet Vaccination & Care Reminder System** as required for MCA academic project verification.

---

## 🧪 SYSTEM TEST MATRIX

| Test Case ID | Test Scenario | Input Data / Steps | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | User Registration with Valid Data | Name: "Alex", Email: "alex@petcare.com", Password: "password123" | User account created successfully, redirected to login page with success alert. | Account created, redirected to login. | **PASS** |
| **TC-02** | User Registration with Duplicate Email | Email: "alex@petcare.com" | Registration rejected with warning "Email already exists". | Warning message displayed. | **PASS** |
| **TC-03** | User Login with Correct Credentials | Email: "alex@petcare.com", Password: "password123" | User authenticated, session established, redirected to Dashboard. | User logged in, redirected to dashboard. | **PASS** |
| **TC-04** | User Login with Incorrect Password | Email: "alex@petcare.com", Password: "wrongpassword" | Authentication denied, error alert displayed. | Login rejected, error shown. | **PASS** |
| **TC-05** | Add Pet Profile with Photo Upload | Name: "Max", Species: "Dog", Breed: "Golden Retriever", DOB: "2023-05-10", Photo: `max.jpg` | Pet profile created, photo saved in uploads, redirected to Pet Detail page. | Pet created with photo & age calculated. | **PASS** |
| **TC-06** | Add Pet Profile without Required Name | Name: "", Species: "Dog" | Form validation blocks submit, error alert shown. | Submission blocked. | **PASS** |
| **TC-07** | Add Vaccination Record | Vaccine: "Rabies", Administered: "2026-01-10", Next Due: "2027-01-10" | Vaccination saved, status calculated as `Up to date`. | Record saved, status set to `Up to date`. | **PASS** |
| **TC-08** | Dynamic Vaccination Status Calculation | Administered: "2025-08-01", Next Due: "2026-08-01" (Past date) | Status dynamically calculated as `Overdue`. | Status displayed as `Overdue` badge. | **PASS** |
| **TC-09** | Invalid Date Validation | Administered: "2026-09-10", Next Due: "2026-09-01" (Before Administered) | Validation error: "Next due date cannot be earlier than administered date." | Form submission blocked with error message. | **PASS** |
| **TC-10** | Add Medication Schedule | Medicine: "Apoquel", Frequency: "Once daily", Start: "2026-09-10", End: "2026-09-25" | Schedule added to Active Medications list. | Medication created under Active tab. | **PASS** |
| **TC-11** | Toggle Medication Active to Completed | Click "Toggle Status" button on active medication | Status updated to `Completed`, moved to Completed tab. | Status changed to Completed. | **PASS** |
| **TC-12** | Trigger Smart Reminder Engine | Click "Sync Engine" / POST `/reminders/trigger-check` | Scanner checks all due dates, populates reminders & notifications. | Reminders scanned & notifications created. | **PASS** |
| **TC-13** | In-App Notification Generation | Due date within 7 days | Notification alert created in database and unread badge count updated. | Notification displayed in feed & navbar badge. | **PASS** |
| **TC-14** | Unauthorized Data Access Prevention (URL Manipulation) | User A accesses `/pets/<User_B_Pet_ID>` | System returns `403 Forbidden` error page. | HTTP 403 Forbidden page rendered. | **PASS** |
| **TC-15** | Global Search Execution | Query: "Rabies" | System searches pets, vaccines, medications, and visits, displaying matching list. | Search results rendered cleanly. | **PASS** |
| **TC-16** | Health Timeline Rendering | Navigate to `/timeline` | All medical events merged and sorted chronologically. | Timeline rendered with icons & badges. | **PASS** |
| **TC-17** | Printable Health Report Export | Navigate to `/reports/pet/1/print` | Clean printable dossier view rendered with print trigger. | Print view rendered without UI elements. | **PASS** |
| **TC-18** | Public Emergency QR Code Tag | Scan / Navigate to `/pets/public-emergency/1` | Public emergency card rendered displaying owner contact & allergies without sensitive user credentials. | Public emergency card displayed. | **PASS** |

---

## 📈 CONCLUSION OF TESTING
All 18 core test cases passed successfully without critical errors. The system demonstrates strong security, dynamic calculation accuracy, responsive design compatibility, and reliable database integrity.
