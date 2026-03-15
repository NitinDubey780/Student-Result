from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from connection import get_connection, get_all_results, get_grade
import datetime

# ── Color palette ────────────────────────────────────────────────────────────
DARK      = colors.HexColor("#0d1b2a")
DARK2     = colors.HexColor("#1b2d3e")
ACCENT    = colors.HexColor("#1565c0")
ACCENT_L  = colors.HexColor("#e3f2fd")
SUCCESS   = colors.HexColor("#00897b")
DANGER    = colors.HexColor("#e53935")
WARNING   = colors.HexColor("#f57c00")
PURPLE    = colors.HexColor("#7b1fa2")
GREY      = colors.HexColor("#f5f5f5")
GREY2     = colors.HexColor("#eceff1")
WHITE     = colors.white
BLACK     = colors.HexColor("#212121")

def _grade_color(percent):
    p = float(percent)
    if p >= 75:   return SUCCESS
    elif p >= 60: return ACCENT
    elif p >= 45: return WARNING
    elif p >= 33: return PURPLE
    else:         return DANGER

def _hf(canvas_obj, doc, title, is_landscape=False):
    """Header and footer for every page."""
    canvas_obj.saveState()
    w, h = landscape(A4) if is_landscape else A4

    # ── Header ──────────────────────────────────────────────────────
    canvas_obj.setFillColor(DARK)
    canvas_obj.rect(0, h - 60, w, 60, fill=1, stroke=0)
    canvas_obj.setFillColor(ACCENT)
    canvas_obj.rect(0, h - 63, w, 4, fill=1, stroke=0)

    canvas_obj.setFont("Helvetica-Bold", 15)
    canvas_obj.setFillColor(WHITE)
    canvas_obj.drawCentredString(w / 2, h - 36, "Student Result Management System")
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.setFillColor(colors.HexColor("#90caf9"))
    canvas_obj.drawCentredString(w / 2, h - 52, title)

    # ── Footer ──────────────────────────────────────────────────────
    canvas_obj.setFillColor(DARK)
    canvas_obj.rect(0, 0, w, 28, fill=1, stroke=0)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#90caf9"))
    canvas_obj.drawString(20, 8,
        f"Generated: {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    canvas_obj.drawCentredString(w / 2, 8,
        "Student Result Management System  |  Confidential")
    canvas_obj.drawRightString(w - 20, 8, f"Page {doc.page}")
    canvas_obj.restoreState()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INDIVIDUAL MARKSHEET
# ═══════════════════════════════════════════════════════════════════════════════
def generate_marksheet(student_data, result_data, filepath="marksheet.pdf"):
    """
    result_data: tuple from result table (rid, roll, name, course, marks_ob, full_marks, percent)
    student_data: optional — we fetch from DB using roll if needed
    """
    if result_data is None:
        return None

    roll    = str(result_data[1])
    name    = str(result_data[2])
    course  = str(result_data[3])
    marks   = str(result_data[4])
    full    = str(result_data[5])
    percent = str(result_data[6])

    # Try to fetch extra student details from student table
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM student WHERE roll=?", (roll,))
    s = cur.fetchone(); con.close()

    # Use student table values if result fields are empty
    if s:
        if not name or name == "None":   name   = str(s[1])
        if not course or course == "None": course = str(s[7])
        email   = str(s[2])
        gender  = str(s[3])
        contact = str(s[5])
        adm     = str(s[6])
    else:
        email = gender = contact = adm = "—"

    grade, _ = get_grade(percent)
    gc       = _grade_color(percent)
    pct_f    = float(percent)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=75, bottomMargin=45,
        leftMargin=40, rightMargin=40,
    )
    elements = [Spacer(1, 8)]

    # ── Student Info Box ────────────────────────────────────────────
    info_style = TableStyle([
        ('BACKGROUND',  (0,0), (0,-1), ACCENT_L),
        ('BACKGROUND',  (2,0), (2,-1), ACCENT_L),
        ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME',    (3,0), (3,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('TEXTCOLOR',   (0,0), (0,-1), ACCENT),
        ('TEXTCOLOR',   (2,0), (2,-1), ACCENT),
        ('TEXTCOLOR',   (1,0), (-1,-1), BLACK),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor("#b0bec5")),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, GREY2]),
        ('PADDING',     (0,0), (-1,-1), 9),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ])

    info_data = [
        ["Student Name",  name,    "Roll Number",    roll],
        ["Course",        course,  "Date of Report", datetime.datetime.now().strftime("%d %b %Y")],
        ["Gender",        gender,  "Contact",        contact],
        ["Admission",     adm,     "Email",          email],
    ]
    info_table = Table(info_data, colWidths=[3.8*cm, 7.2*cm, 3.8*cm, 7.2*cm])
    info_table.setStyle(info_style)
    elements.append(info_table)
    elements.append(Spacer(1, 18))

    # ── Section heading ─────────────────────────────────────────────
    elements.append(Paragraph(
        '<font color="#1565c0"><b>ACADEMIC RESULT  —  MARKSHEET</b></font>',
        ParagraphStyle("h", fontSize=13, alignment=TA_CENTER, spaceAfter=6),
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    elements.append(Spacer(1, 14))

    # ── Marks detail table ──────────────────────────────────────────
    marks_data = [
        ["Subject / Course", "Marks Obtained", "Full Marks", "Percentage", "Grade"],
        [course, marks, full, f"{pct_f:.2f}%", grade],
    ]
    marks_table = Table(marks_data,
                        colWidths=[6.5*cm, 3.8*cm, 3.2*cm, 3.5*cm, 5*cm])
    marks_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  DARK),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  10),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 11),
        ('ALIGN',       (1,0), (-1,-1), 'CENTER'),
        ('ALIGN',       (0,0), (0,-1),  'LEFT'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHTS',  (0,1), (-1,-1), 32),
        ('BACKGROUND',  (0,1), (-1,-1), WHITE),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor("#b0bec5")),
        ('PADDING',     (0,0), (-1,-1), 9),
        ('TEXTCOLOR',   (4,1), (4,-1),  gc),
        ('FONTNAME',    (4,1), (4,-1),  'Helvetica-Bold'),
        ('FONTSIZE',    (4,1), (4,-1),  12),
    ]))
    elements.append(marks_table)
    elements.append(Spacer(1, 22))

    # ── Summary box ─────────────────────────────────────────────────
    summary_data = [
        ["Total Marks Obtained", "Full Marks", "Percentage", "Final Grade"],
        [marks,                  full,         f"{pct_f:.2f}%", grade],
    ]
    summary = Table(summary_data, colWidths=[5.5*cm]*4)
    summary.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  ACCENT),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  9),
        ('FONTSIZE',    (0,1), (-1,1),  14),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHTS',  (0,1), (-1,1),  44),
        ('GRID',        (0,0), (-1,-1), 1, WHITE),
        ('BACKGROUND',  (0,1), (2,1),   GREY2),
        ('BACKGROUND',  (3,1), (3,1),   gc),
        ('TEXTCOLOR',   (3,1), (3,1),   WHITE),
        ('PADDING',     (0,0), (-1,-1), 8),
    ]))
    elements.append(summary)
    elements.append(Spacer(1, 30))

    # ── Grade scale legend ──────────────────────────────────────────
    legend_data = [
        ["Grade Scale:", "Distinction >= 75%", "First Div >= 60%",
         "Second Div >= 45%", "Pass >= 33%", "Fail < 33%"],
    ]
    legend = Table(legend_data, colWidths=[2.5*cm, 3.5*cm, 3*cm, 3.5*cm, 2.5*cm, 2.5*cm])
    legend.setStyle(TableStyle([
        ('FONTNAME',    (0,0), (0,0),   'Helvetica-Bold'),
        ('FONTNAME',    (1,0), (-1,0),  'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 8),
        ('TEXTCOLOR',   (0,0), (-1,-1), colors.HexColor("#607d8b")),
        ('BACKGROUND',  (0,0), (-1,-1), GREY),
        ('PADDING',     (0,0), (-1,-1), 6),
        ('BOX',         (0,0), (-1,-1), 0.5, colors.HexColor("#b0bec5")),
    ]))
    elements.append(legend)

    doc.build(
        elements,
        onFirstPage=lambda c, d: _hf(c, d, "Individual Student Marksheet"),
        onLaterPages=lambda c, d: _hf(c, d, "Individual Student Marksheet"),
    )
    return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CLASS TOPPER LIST
# ═══════════════════════════════════════════════════════════════════════════════
def generate_topper_list(filepath="topper_list.pdf"):
    results = get_all_results()
    if not results:
        return None

    sorted_r = sorted(results, key=lambda x: float(x[6]), reverse=True)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=75, bottomMargin=45,
        leftMargin=40, rightMargin=40,
    )
    elements = [Spacer(1, 8)]
    elements.append(Paragraph(
        '<font color="#1565c0"><b>CLASS TOPPER LIST  —  RANKED BY PERCENTAGE</b></font>',
        ParagraphStyle("h", fontSize=13, alignment=TA_CENTER, spaceAfter=6),
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    elements.append(Spacer(1, 12))

    headers = ["Rank", "Roll No.", "Student Name", "Course",
               "Marks", "Full Marks", "Percentage", "Grade"]
    data    = [headers]
    medals  = {0:"1st", 1:"2nd", 2:"3rd"}

    for i, r in enumerate(sorted_r):
        grade, _ = get_grade(r[6])
        rank_lbl = medals.get(i, str(i+1))
        data.append([rank_lbl, str(r[1]), str(r[2]), str(r[3]),
                     str(r[4]), str(r[5]), f"{float(r[6]):.2f}%", grade])

    col_w = [1.8*cm, 2.5*cm, 5*cm, 4*cm, 2.2*cm, 2.8*cm, 3*cm, 3.2*cm]
    table = Table(data, colWidths=col_w, repeatRows=1)

    style = [
        ('BACKGROUND',  (0,0), (-1,0),  DARK),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  9),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',       (2,0), (3,-1),  'LEFT'),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GREY2]),
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor("#b0bec5")),
        ('PADDING',     (0,0), (-1,-1), 7),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ]
    # Gold/silver/bronze rows
    for i in range(min(3, len(sorted_r))):
        bg = [colors.HexColor("#fff9c4"),
              colors.HexColor("#f5f5f5"),
              colors.HexColor("#fff3e0")][i]
        style.append(('BACKGROUND', (0, i+1), (-1, i+1), bg))

    # Grade column color
    for i, r in enumerate(sorted_r):
        gc = _grade_color(r[6])
        style.append(('TEXTCOLOR', (7, i+1), (7, i+1), gc))
        style.append(('FONTNAME',  (7, i+1), (7, i+1), 'Helvetica-Bold'))

    table.setStyle(TableStyle(style))
    elements.append(table)

    doc.build(
        elements,
        onFirstPage=lambda c, d: _hf(c, d, "Class Topper List"),
        onLaterPages=lambda c, d: _hf(c, d, "Class Topper List"),
    )
    return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SUBJECT-WISE REPORT
# ═══════════════════════════════════════════════════════════════════════════════
def generate_subject_report(filepath="subject_report.pdf"):
    results = get_all_results()
    if not results:
        return None

    # Group by course
    course_map = {}
    for r in results:
        c = r[3]
        course_map.setdefault(c, []).append(r)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=75, bottomMargin=45,
        leftMargin=40, rightMargin=40,
    )
    elements = [Spacer(1, 8)]

    for course_name, c_results in course_map.items():
        # Section heading
        elements.append(Paragraph(
            f'<font color="#ffffff"><b>  Course : {course_name}  </b></font>',
            ParagraphStyle("ch", fontSize=11, alignment=TA_LEFT,
                           backColor=ACCENT, textColor=WHITE,
                           leftIndent=0, spaceAfter=6, spaceBefore=8,
                           borderPad=7),
        ))

        # Stats row
        avg     = sum(float(r[6]) for r in c_results) / len(c_results)
        highest = max(c_results, key=lambda x: float(x[6]))
        passed  = sum(1 for r in c_results if float(r[6]) >= 33)

        stats_data = [
            ["Total Students", "Avg %", "Highest Score", "Pass / Fail"],
            [str(len(c_results)), f"{avg:.2f}%",
             f"{float(highest[6]):.1f}%  ({highest[2]})",
             f"{passed} / {len(c_results)-passed}"],
        ]
        st = Table(stats_data, colWidths=[4*cm]*4)
        st.setStyle(TableStyle([
            ('BACKGROUND',  (0,0), (-1,0),  ACCENT_L),
            ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',    (0,0), (-1,-1), 9),
            ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
            ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor("#b0bec5")),
            ('PADDING',     (0,0), (-1,-1), 7),
            ('TEXTCOLOR',   (0,0), (-1,0),  ACCENT),
        ]))
        elements.append(st)
        elements.append(Spacer(1, 6))

        # Student rows
        tdata = [["Roll No.", "Student Name", "Marks", "Full Marks", "Percentage", "Grade"]]
        for r in sorted(c_results, key=lambda x: float(x[6]), reverse=True):
            grade, _ = get_grade(r[6])
            tdata.append([str(r[1]), str(r[2]), str(r[4]),
                          str(r[5]), f"{float(r[6]):.2f}%", grade])

        t = Table(tdata, colWidths=[2.5*cm, 5.5*cm, 2.5*cm, 3*cm, 3*cm, 3*cm],
                  repeatRows=1)
        t_style = [
            ('BACKGROUND',  (0,0), (-1,0),  DARK),
            ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
            ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',    (0,0), (-1,-1), 9),
            ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
            ('ALIGN',       (1,0), (1,-1),  'LEFT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GREY2]),
            ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor("#b0bec5")),
            ('PADDING',     (0,0), (-1,-1), 6),
        ]
        for i, r in enumerate(sorted(c_results, key=lambda x: float(x[6]), reverse=True)):
            gc = _grade_color(r[6])
            t_style.append(('TEXTCOLOR', (5, i+1), (5, i+1), gc))
            t_style.append(('FONTNAME',  (5, i+1), (5, i+1), 'Helvetica-Bold'))
        t.setStyle(TableStyle(t_style))
        elements.append(t)
        elements.append(Spacer(1, 14))

    doc.build(
        elements,
        onFirstPage=lambda c, d: _hf(c, d, "Subject-wise Report"),
        onLaterPages=lambda c, d: _hf(c, d, "Subject-wise Report"),
    )
    return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FULL CLASS RESULT SHEET (landscape)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_full_result_sheet(filepath="full_result.pdf"):
    results = get_all_results()
    if not results:
        return None

    sorted_r = sorted(results, key=lambda x: float(x[6]), reverse=True)

    doc = SimpleDocTemplate(
        filepath, pagesize=landscape(A4),
        topMargin=75, bottomMargin=45,
        leftMargin=40, rightMargin=40,
    )
    elements = [Spacer(1, 8)]
    elements.append(Paragraph(
        '<font color="#1565c0"><b>COMPLETE CLASS RESULT SHEET</b></font>',
        ParagraphStyle("h", fontSize=13, alignment=TA_CENTER, spaceAfter=6),
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    elements.append(Spacer(1, 12))

    headers = ["#", "Roll No.", "Student Name", "Course",
               "Marks", "Full Marks", "Percentage", "Grade", "Status"]
    data    = [headers]

    for i, r in enumerate(sorted_r):
        grade, _ = get_grade(r[6])
        status   = "PASS" if float(r[6]) >= 33 else "FAIL"
        data.append([str(i+1), str(r[1]), str(r[2]), str(r[3]),
                     str(r[4]), str(r[5]), f"{float(r[6]):.2f}%", grade, status])

    col_w = [1.2*cm, 2.5*cm, 6*cm, 5*cm, 2.8*cm, 3.2*cm, 3.2*cm, 4*cm, 2.5*cm]
    table = Table(data, colWidths=col_w, repeatRows=1)

    t_style = [
        ('BACKGROUND',  (0,0), (-1,0),  DARK),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  9),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',       (2,0), (3,-1),  'LEFT'),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, GREY2]),
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor("#b0bec5")),
        ('PADDING',     (0,0), (-1,-1), 6),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ]
    for i, r in enumerate(sorted_r):
        gc     = _grade_color(r[6])
        status = "PASS" if float(r[6]) >= 33 else "FAIL"
        sc     = SUCCESS if status == "PASS" else DANGER
        t_style.append(('TEXTCOLOR', (7, i+1), (7, i+1), gc))
        t_style.append(('FONTNAME',  (7, i+1), (7, i+1), 'Helvetica-Bold'))
        t_style.append(('TEXTCOLOR', (8, i+1), (8, i+1), sc))
        t_style.append(('FONTNAME',  (8, i+1), (8, i+1), 'Helvetica-Bold'))

    table.setStyle(TableStyle(t_style))
    elements.append(table)

    # ── Summary ─────────────────────────────────────────────────────
    elements.append(Spacer(1, 16))
    total  = len(results)
    passed = sum(1 for r in results if float(r[6]) >= 33)
    avg    = sum(float(r[6]) for r in results) / total
    topper = sorted_r[0] if sorted_r else None

    s_data = [
        ["Total Students", "Passed", "Failed", "Pass Rate", "Class Average", "Topper"],
        [str(total), str(passed), str(total-passed),
         f"{passed/total*100:.1f}%", f"{avg:.2f}%",
         f"{topper[2]}  ({float(topper[6]):.1f}%)" if topper else "—"],
    ]
    summary = Table(s_data, colWidths=[3.8*cm]*6)
    summary.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  ACCENT),
        ('TEXTCOLOR',   (0,0), (-1,0),  WHITE),
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  9),
        ('FONTSIZE',    (0,1), (-1,1),  11),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHTS',  (0,1), (-1,1),  36),
        ('GRID',        (0,0), (-1,-1), 1, WHITE),
        ('BACKGROUND',  (0,1), (-1,1),  ACCENT_L),
        ('PADDING',     (0,0), (-1,-1), 7),
    ]))
    elements.append(summary)

    def lscape_hf(c, d):
        _hf(c, d, "Complete Class Result Sheet", is_landscape=True)

    doc.build(elements, onFirstPage=lscape_hf, onLaterPages=lscape_hf)
    return filepath