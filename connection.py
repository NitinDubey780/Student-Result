import sqlite3
import hashlib

DB_PATH = "Result_Manage.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_db():
    con = get_connection()
    cur = con.cursor()

    # ── Users ────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid        INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            role       TEXT NOT NULL DEFAULT 'student',
            roll_no    TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Course ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS course (
            cid         INTEGER PRIMARY KEY AUTOINCREMENT,
            Name        TEXT,
            Duration    TEXT,
            Charges     TEXT,
            Description TEXT
        )
    """)

    # ── Subject (NEW) ────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subject (
            sid        INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            course_id  INTEGER NOT NULL,
            max_marks  INTEGER DEFAULT 100,
            FOREIGN KEY (course_id) REFERENCES course(cid) ON DELETE CASCADE
        )
    """)

    # ── Student ──────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student (
            roll      INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT,
            email     TEXT,
            gender    TEXT,
            dob       TEXT,
            contact   TEXT,
            admission TEXT,
            course    TEXT,
            state     TEXT,
            city      TEXT,
            pin       TEXT,
            address   TEXT
        )
    """)

    # ── Exam (NEW) ───────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exam (
            eid           INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            exam_type     TEXT DEFAULT 'Theory',
            course_id     INTEGER NOT NULL,
            academic_year TEXT DEFAULT '2025-26',
            semester      TEXT DEFAULT '1',
            FOREIGN KEY (course_id) REFERENCES course(cid) ON DELETE CASCADE
        )
    """)

    # ── Result (UPGRADED) ────────────────────────────────────────────
    # Keep old columns + add subject_id, exam_id
    cur.execute("""
        CREATE TABLE IF NOT EXISTS result (
            rid        INTEGER PRIMARY KEY AUTOINCREMENT,
            roll       TEXT,
            name       TEXT,
            course     TEXT,
            subject_id INTEGER,
            exam_id    INTEGER,
            marks_ob   TEXT,
            full_marks TEXT,
            percent    TEXT,
            grade      TEXT,
            FOREIGN KEY (subject_id) REFERENCES subject(sid),
            FOREIGN KEY (exam_id)    REFERENCES exam(eid)
        )
    """)

    # ── Attendance (NEW) ─────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            aid        INTEGER PRIMARY KEY AUTOINCREMENT,
            roll       TEXT NOT NULL,
            date       TEXT NOT NULL,
            status     TEXT DEFAULT 'P',
            course_id  INTEGER,
            marked_by  TEXT DEFAULT 'admin'
        )
    """)

    # ── Notifications (NEW) ──────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notification (
            nid       INTEGER PRIMARY KEY AUTOINCREMENT,
            roll      TEXT,
            title     TEXT,
            message   TEXT,
            is_read   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    con.commit()

    # Migrate old result table if missing new columns
    try:
        cur.execute("ALTER TABLE result ADD COLUMN subject_id INTEGER")
        con.commit()
    except: pass
    try:
        cur.execute("ALTER TABLE result ADD COLUMN exam_id INTEGER")
        con.commit()
    except: pass
    try:
        cur.execute("ALTER TABLE result ADD COLUMN grade TEXT")
        con.commit()
    except: pass

    # Default admin
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                    ("admin", hash_password("admin123"), "admin"))
        con.commit()

    con.close()

# ── Auth ─────────────────────────────────────────────────────────────────────
def verify_user(username, password):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT uid,username,role,roll_no FROM users WHERE username=? AND password=?",
                (username, hash_password(password)))
    row = cur.fetchone(); con.close()
    return row

def register_user(username, password, role="student", roll_no=None):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute("INSERT INTO users (username,password,role,roll_no) VALUES (?,?,?,?)",
                    (username, hash_password(password), role, roll_no))
        con.commit(); con.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        con.close(); return False, "Username already exists!"
    except Exception as e:
        con.close(); return False, str(e)

# ── Counts ───────────────────────────────────────────────────────────────────
def get_counts():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM course");  c = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM student"); s = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM result");  r = cur.fetchone()[0]
    con.close(); return c, s, r

def get_extended_counts():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM course");   c = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM student");  s = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM result");   r = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM subject");  sub = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM exam");     e = cur.fetchone()[0]
    con.close(); return c, s, r, sub, e

# ── Getters ──────────────────────────────────────────────────────────────────
def get_all_courses():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM course"); rows = cur.fetchall(); con.close(); return rows

def get_all_students():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM student"); rows = cur.fetchall(); con.close(); return rows

def get_all_results():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM result"); rows = cur.fetchall(); con.close(); return rows

def get_subjects_by_course(course_id):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM subject WHERE course_id=?", (course_id,))
    rows = cur.fetchall(); con.close(); return rows

def get_all_subjects():
    con = get_connection(); cur = con.cursor()
    cur.execute("""SELECT s.sid, s.name, c.Name as course_name, s.max_marks
                   FROM subject s JOIN course c ON s.course_id=c.cid""")
    rows = cur.fetchall(); con.close(); return rows

def get_exams_by_course(course_id):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM exam WHERE course_id=?", (course_id,))
    rows = cur.fetchall(); con.close(); return rows

def get_all_exams():
    con = get_connection(); cur = con.cursor()
    cur.execute("""SELECT e.eid, e.name, e.exam_type, c.Name, e.academic_year, e.semester
                   FROM exam e JOIN course c ON e.course_id=c.cid""")
    rows = cur.fetchall(); con.close(); return rows

def get_student_results(roll):
    con = get_connection(); cur = con.cursor()
    cur.execute("""
        SELECT r.rid, r.roll, r.name, r.course,
               COALESCE(s.name,'—') as subject_name,
               COALESCE(e.name,'—') as exam_name,
               r.marks_ob, r.full_marks, r.percent, r.grade
        FROM result r
        LEFT JOIN subject s ON r.subject_id = s.sid
        LEFT JOIN exam    e ON r.exam_id    = e.eid
        WHERE r.roll = ?
    """, (str(roll),))
    rows = cur.fetchall(); con.close(); return rows

def get_student_attendance(roll):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM attendance WHERE roll=? ORDER BY date DESC", (str(roll),))
    rows = cur.fetchall(); con.close(); return rows

def get_attendance_summary(roll):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM attendance WHERE roll=?",        (str(roll),))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM attendance WHERE roll=? AND status='P'", (str(roll),))
    present = cur.fetchone()[0]
    con.close()
    pct = round(present/total*100, 1) if total else 0
    return total, present, total-present, pct

def get_notifications(roll):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM notification WHERE roll=? OR roll='all' ORDER BY created_at DESC LIMIT 20",
                (str(roll),))
    rows = cur.fetchall(); con.close(); return rows

def mark_notification_read(nid):
    con = get_connection(); cur = con.cursor()
    cur.execute("UPDATE notification SET is_read=1 WHERE nid=?", (nid,))
    con.commit(); con.close()

def send_notification(roll, title, message):
    con = get_connection(); cur = con.cursor()
    cur.execute("INSERT INTO notification (roll,title,message) VALUES (?,?,?)",
                (str(roll), title, message))
    con.commit(); con.close()

def get_grade(percent):
    p = float(percent)
    if p >= 75:   return "Distinction",    "#00897b"
    elif p >= 60: return "First Division", "#1976d2"
    elif p >= 45: return "Second Division","#f57c00"
    elif p >= 33: return "Pass",           "#7b1fa2"
    else:         return "Fail",           "#e53935"

create_db()