<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flet-0.82+-00BCD4?style=for-the-badge&logo=flutter&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/ReportLab-PDF-E53935?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Web-0d1b2a?style=for-the-badge"/>

<br/><br/>

# 🎓 Student Result Management System

### A full-featured, role-based academic management system built with Python & Flet
### Runs as a Desktop App **and** a Web App — no extra setup needed.

<br/>

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [Database Schema](#-database-schema)
- [Grading Scale](#-grading-scale)
- [PDF Reports](#-pdf-reports)
- [Run as Web App](#-run-as-web-app)
- [Build .exe](#-build-exe-for-windows)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Student Result Management System (SRMS)** is a complete academic management platform that handles everything from course creation to multi-subject result entry, attendance tracking, and PDF report generation.

Built with **Python + Flet**, it runs natively on Windows as a desktop app and can be deployed as a web app on any server — same codebase, zero changes needed.

---

## ✨ Features

### 👨‍💼 Admin Panel — 9 Tabs

| Tab | Description |
|-----|-------------|
| 📊 **Dashboard** | Live stats — courses, students, results, subjects, exams. Grade distribution chart + recent results |
| 📚 **Courses** | Add / Edit / Delete / Search courses with duration, charges, description |
| 📖 **Subjects** | Add multiple subjects per course with configurable max marks |
| 📝 **Exams** | Create exam types (Mid-Term, Final, Practical, Assignment) with semester & academic year |
| 👥 **Students** | Full student CRUD — name, email, gender, DOB, contact, course, address |
| 📈 **Results** | Enter marks per student per subject per exam. Auto percentage + grade calculation |
| ✅ **Attendance** | Mark full-class attendance (Present / Absent / Leave) with attendance % summary |
| 🔔 **Notifications** | Send messages to individual students or broadcast to all students |
| 📄 **Reports** | Generate 4 types of PDF reports with one click |

### 🎓 Student Panel — 6 Tabs

| Tab | Description |
|-----|-------------|
| 🏠 **Home** | Subject-wise result cards + attendance summary + notification preview |
| 📊 **Results** | Exam-grouped results with progress bars, overall %, grade per exam |
| 📅 **Attendance** | Date-wise attendance record with Present / Absent / Leave breakdown |
| 🔔 **Notifications** | Admin messages with unread badge indicator |
| 👤 **Profile** | Full personal details view |
| 📄 **Marksheet** | Download PDF marksheet per exam |

### 🔐 Authentication System
- Role-based login — **Admin** and **Student**
- Secure password hashing (SHA-256)
- Self-registration with role selection
- Default admin account pre-created

### 📄 PDF Reports
- Individual student marksheet with full details
- Class topper list ranked by percentage
- Subject-wise / course-wise report with statistics
- Full class result sheet in landscape A4

---

## 🛠 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Core language |
| **Flet** | 0.82+ | Desktop + Web UI framework |
| **SQLite3** | Built-in | Local database (no server needed) |
| **ReportLab** | 4.0+ | PDF generation |
| **Pillow** | 10.0+ | Image handling |
| **hashlib** | Built-in | Password hashing |

---

## 📁 Project Structure

```
Student-Result/
│
├── main.py                 # Entry point — run this file
├── connection.py           # Database schema, queries, auth helpers
├── login_view.py           # Login & Register screen
├── admin_dashboard.py      # Full admin panel (9 tabs)
├── student_dashboard.py    # Student panel (6 tabs)
├── pdf_generator.py        # All PDF export logic
├── requirements.txt        # Python dependencies
├── README.md               # You are here
│
└── Result_Manage.db        # SQLite database (auto-created on first run)
```

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have **Python 3.10 or higher** installed.

```bash
# Check your Python version
python --version
```

Download Python from: https://python.org/downloads

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/NitinDubey780/Student-Result.git
cd Student-Result
```

---

### Step 2 — Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac / Linux
source venv/bin/activate
```

You will see `(venv)` in your terminal — this means it is active.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `flet`, `reportlab`, `Pillow`

---

### Step 4 — Run the App

```bash
python main.py
```

The app opens as a **desktop window** automatically.

> On first run, `Result_Manage.db` is created with the default admin account.

---

## 📖 Usage Guide

### Default Login

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |

---

### First Time Setup Order (Important!)

Always follow this order when setting up fresh data:

```
Step 1 — Login as Admin

Step 2 — Courses tab
         → Add a course (e.g. "B.Tech CSE", "12th Science")

Step 3 — Subjects tab
         → Select the course → Add subjects
         (e.g. Mathematics, Physics, Chemistry, English)

Step 4 — Exams tab
         → Create an exam (e.g. "Mid-Term 2025-26", Type: Theory, Semester: 1)

Step 5 — Students tab
         → Add student details (Roll No. is auto-assigned)

Step 6 — Results tab
         → Select: Student + Subject + Exam → Enter marks → Submit

Step 7 — Attendance tab
         → Select date → Mark attendance for each student → Save All
```

---

### Creating a Student Login Account

After adding a student record in the Students tab:

1. Click **Logout**
2. On the login screen, click **"Don't have an account? Register"**
3. Fill the form:
   - **Username** — any (e.g. `rahul2025`)
   - **Password** — any
   - **Register As** — `Student`
   - **Roll Number** — exact roll number from the Students table (e.g. `1`)
4. Click Register, then login with those credentials

> ⚠️ Roll number must exactly match the number shown in the first column of the Students table.

---

## 🗄 Database Schema

The database is auto-created on first run with these 7 tables:

```
users         → login accounts with role (admin / student)
course        → course details (name, duration, charges, description)
subject       → subjects linked to courses with max marks
student       → student personal info (roll, name, email, address...)
exam          → exam definitions (type, semester, academic year)
result        → marks per student per subject per exam
attendance    → daily attendance records per student
notification  → messages from admin to students
```

No manual database setup is required.

---

## 📊 Grading Scale

| Grade | Percentage | Color |
|-------|-----------|-------|
| **Distinction** | ≥ 75% | 🟢 Green |
| **First Division** | ≥ 60% | 🔵 Blue |
| **Second Division** | ≥ 45% | 🟡 Orange |
| **Pass** | ≥ 33% | 🟣 Purple |
| **Fail** | < 33% | 🔴 Red |

---

## 📄 PDF Reports

All PDFs are generated from the **Reports** tab in the Admin panel.

| Report | Description | Format |
|--------|-------------|--------|
| **Individual Marksheet** | One student's complete result with personal details, marks, grade | Portrait A4 |
| **Class Topper List** | All students ranked by percentage with medals for top 3 | Portrait A4 |
| **Subject-wise Report** | Per-course analysis — avg %, highest score, pass/fail count | Portrait A4 |
| **Full Class Result Sheet** | Complete result of all students | Landscape A4 |

PDFs are saved in the project folder and opened automatically.

Students can also download their own marksheet from the **Marksheet** tab after logging in.

---

## 🌐 Run as Web App

To run the app in a browser (on any device on your network):

**Edit the last line in `main.py`:**

```python
# From:
ft.run(main)

# To:
ft.run(main, view=ft.AppView.WEB_BROWSER, port=8080)
```

Then run:

```bash
python main.py
```

Open: **http://localhost:8080**

To allow access from other devices on the network:

```python
ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8080)
```

---

## 📦 Build .exe for Windows

Package the app as a standalone `.exe` file (no Python required on target machine):

```bash
# Install packaging tool
pip install pyinstaller

# Build the executable
flet pack main.py --name "SRMS"
```

The `.exe` will be generated in the `dist/` folder.

---

## 🚀 Quick Start (All Steps in One)

```bash
# 1. Clone
git clone https://github.com/NitinDubey780/Student-Result.git
cd Student-Result

# 2. Setup
python -m venv venv
venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Run
python main.py
```

Login with: **admin / admin123**

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/NewFeature`
3. Commit your changes: `git commit -m "Add NewFeature"`
4. Push to the branch: `git push origin feature/NewFeature`
5. Open a Pull Request

---

## 👨‍💻 Author

**Nitin Dubey**

[![GitHub](https://img.shields.io/badge/GitHub-NitinDubey780-181717?style=flat&logo=github)](https://github.com/NitinDubey780)

---

## 📜 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Nitin Dubey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<div align="center">

Made with ❤️ using Python & Flet

⭐ **Star this repo if you found it helpful!**

</div>