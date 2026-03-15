import flet as ft
import sqlite3
from connection import (get_connection, get_all_courses, get_all_students,
                        get_all_results, get_counts, get_extended_counts,
                        get_all_subjects, get_all_exams, get_grade,
                        send_notification)
from pdf_generator import (generate_marksheet, generate_topper_list,
                            generate_subject_report, generate_full_result_sheet)
import os, datetime

BG       = "#0d1b2a"
CARD     = "#1b2d3e"
CARD2    = "#162436"
ACCENT   = "#1976d2"
ACCENT2  = "#42a5f5"
SUCCESS  = "#00897b"
DANGER   = "#e53935"
WARNING  = "#f57c00"
PURPLE   = "#7b1fa2"
TEXT     = "#e8f4fd"
SUBTEXT  = "#7fa8c9"
BORDER   = "#2a4a6b"
INPUT_BG = "#112030"

STATE_LIST = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa",
    "Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
    "Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland",
    "Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura",
    "Uttar Pradesh","Uttarakhand","West Bengal","Delhi","Other"
]

def inp(label, icon, password=False, readonly=False, multiline=False, expand=False):
    return ft.TextField(
        label=label, prefix_icon=icon,
        password=password, can_reveal_password=password,
        read_only=readonly, multiline=multiline,
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=8, cursor_color=ACCENT2,
        expand=expand,
        min_lines=2 if multiline else None,
        max_lines=3 if multiline else None,
    )

def ddl(label, opts, expand=False):
    return ft.Dropdown(
        label=label,
        options=[ft.dropdown.Option(str(o[0]), str(o[1])) if isinstance(o, tuple)
                 else ft.dropdown.Option(str(o)) for o in opts],
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=8, expand=expand,
    )

def stat_card(title, value, icon, color, ref=None):
    vt = ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=color, ref=ref)
    return ft.Container(
        expand=True, bgcolor=CARD, border_radius=14,
        border=ft.Border.all(1, BORDER), padding=16,
        content=ft.Row([
            ft.Container(ft.Icon(icon, color=color, size=28),
                         bgcolor=f"{color}22", border_radius=10, padding=10),
            ft.Column([ft.Text(title, size=11, color=SUBTEXT),vt], spacing=2),
        ], spacing=14),
    )

def section_title(text, icon=None):
    return ft.Row([
        ft.Icon(icon, color=ACCENT2, size=18) if icon else ft.Container(),
        ft.Text(text, size=14, weight=ft.FontWeight.BOLD, color=TEXT),
    ], spacing=8)

def table_hdr(cols):
    return [ft.DataColumn(ft.Text(c, color=ACCENT2, size=11, weight=ft.FontWeight.BOLD))
            for c in cols]

def admin_dashboard(page: ft.Page, uid, uname, on_logout):
    page.clean(); page.bgcolor = BG; page.padding = 0; page.scroll = None

    def snack(msg, color=SUCCESS):
        page.snack_bar = ft.SnackBar(
            ft.Text(msg, color="white", weight=ft.FontWeight.W_500),
            bgcolor=color, duration=3000)
        page.snack_bar.open = True; page.update()

    ref_c = ft.Ref[ft.Text](); ref_s = ft.Ref[ft.Text]()
    ref_r = ft.Ref[ft.Text](); ref_sub = ft.Ref[ft.Text](); ref_e = ft.Ref[ft.Text]()

    def refresh_stats():
        c,s,r,sub,e = get_extended_counts()
        for ref,val in [(ref_c,c),(ref_s,s),(ref_r,r),(ref_sub,sub),(ref_e,e)]:
            if ref.current: ref.current.value = str(val)
        page.update()

    # ══════════════════════════════════════════════════════════════════
    # TAB 1 — DASHBOARD
    # ══════════════════════════════════════════════════════════════════
    def build_dashboard():
        c,s,r,sub,e = get_extended_counts()
        results = get_all_results()

        dist = {"Distinction":0,"First Division":0,"Second Division":0,"Pass":0,"Fail":0}
        for res in results:
            g,_ = get_grade(res[8] or res[6] or "0")
            dist[g] = dist.get(g,0)+1

        gcols = {"Distinction":SUCCESS,"First Division":ACCENT,
                 "Second Division":WARNING,"Pass":PURPLE,"Fail":DANGER}
        total_r = len(results) or 1
        bars = []
        for grade,count in dist.items():
            pct = count/total_r*100
            bars.append(ft.Column([
                ft.Row([ft.Text(grade,size=11,color=SUBTEXT,expand=True),
                        ft.Text(f"{count} ({pct:.0f}%)",size=11,color=TEXT)]),
                ft.Stack([
                    ft.Container(bgcolor=CARD2,border_radius=4,height=7,expand=True),
                    ft.Container(bgcolor=gcols[grade],border_radius=4,height=7,
                                 width=max(4,pct*2.2)),
                ]),
            ],spacing=3))

        recent = sorted(results,key=lambda x:x[0],reverse=True)[:6]
        recent_rows=[]
        for res in recent:
            pct_val = res[8] or res[6] or "0"
            g,gc = get_grade(pct_val)
            recent_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(res[1]),color=ACCENT2,size=11)),
                ft.DataCell(ft.Text(str(res[2]),color=TEXT,size=11)),
                ft.DataCell(ft.Text(str(res[3]),color=SUBTEXT,size=10)),
                ft.DataCell(ft.Text(f"{float(pct_val):.1f}%",color=TEXT,size=11)),
                ft.DataCell(ft.Container(
                    ft.Text(g,color="white",size=9,weight=ft.FontWeight.BOLD),
                    bgcolor=gc,border_radius=5,
                    padding=ft.Padding.symmetric(horizontal=7,vertical=3))),
            ]))

        return ft.Column([
            ft.Text(f"Good day, {uname} 👋",size=20,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Text(datetime.datetime.now().strftime("%A, %d %B %Y"),size=11,color=SUBTEXT),
            ft.Divider(color=BORDER,height=14),
            ft.Row([
                stat_card("Courses",  c,   ft.Icons.BOOK_ROUNDED,       ACCENT2, ref_c),
                stat_card("Students", s,   ft.Icons.PEOPLE_ROUNDED,     SUCCESS, ref_s),
                stat_card("Results",  r,   ft.Icons.ANALYTICS_ROUNDED,  WARNING, ref_r),
                stat_card("Subjects", sub, ft.Icons.SUBJECT_ROUNDED,    PURPLE,  ref_sub),
                stat_card("Exams",    e,   ft.Icons.ASSIGNMENT_ROUNDED, DANGER,  ref_e),
            ],spacing=10),
            ft.Divider(color=BORDER,height=14),
            ft.Row([
                ft.Container(expand=True,bgcolor=CARD,border_radius=14,
                    border=ft.Border.all(1,BORDER),padding=18,
                    content=ft.Column([
                        section_title("Grade Distribution",ft.Icons.PIE_CHART_ROUNDED),
                        ft.Divider(color=BORDER,height=8),
                        *bars,
                    ],spacing=8)),
                ft.Container(expand=2,bgcolor=CARD,border_radius=14,
                    border=ft.Border.all(1,BORDER),padding=18,
                    content=ft.Column([
                        section_title("Recent Results",ft.Icons.HISTORY_ROUNDED),
                        ft.Divider(color=BORDER,height=6),
                        ft.DataTable(
                            columns=table_hdr(["Roll","Name","Course","%","Grade"]),
                            rows=recent_rows,
                            heading_row_color=CARD2,
                            data_row_max_height=38,column_spacing=12,
                        ) if recent_rows else ft.Text("No results yet",color=SUBTEXT),
                    ],spacing=6)),
            ],spacing=14,vertical_alignment=ft.CrossAxisAlignment.START),
        ],spacing=10,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 2 — COURSES
    # ══════════════════════════════════════════════════════════════════
    def build_courses():
        c_name=inp("Course Name",ft.Icons.BOOK_OUTLINED)
        c_dur=inp("Duration",ft.Icons.TIMER_OUTLINED)
        c_chg=inp("Charges (₹)",ft.Icons.CURRENCY_RUPEE)
        c_desc=inp("Description",ft.Icons.DESCRIPTION_OUTLINED,multiline=True)
        c_srch=inp("Search",ft.Icons.SEARCH,expand=True)
        sel=[None]

        tbl=ft.DataTable(columns=table_hdr(["ID","Name","Duration","Charges","Desc"]),
            heading_row_color=CARD2,data_row_max_height=42,column_spacing=20,horizontal_margin=10)

        def reload(q=""):
            con=get_connection();cur=con.cursor()
            cur.execute("SELECT * FROM course WHERE Name LIKE ?" if q else "SELECT * FROM course",
                        (f"%{q}%",) if q else ())
            rows=cur.fetchall();con.close();tbl.rows=[]
            for r in rows:
                d=str(r[4])
                tbl.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]),color=SUBTEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[1]),color=TEXT,size=11,weight=ft.FontWeight.W_500),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[2]),color=TEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(f"₹{r[3]}",color=SUCCESS,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(d[:30]+"..." if len(d)>30 else d,color=SUBTEXT,size=10),on_tap=lambda e,row=r:sel_row(row)),
                ]))
            page.update()

        def sel_row(r):
            sel[0]=r[0];c_name.value=r[1];c_name.read_only=True
            c_dur.value=r[2];c_chg.value=r[3];c_desc.value=r[4];page.update()

        def add(e):
            if not c_name.value.strip(): snack("Course name required!",DANGER);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("SELECT * FROM course WHERE Name=?",(c_name.value,))
                if cur.fetchone(): snack("Course already exists!",WARNING);return
                cur.execute("INSERT INTO course(Name,Duration,Charges,Description) VALUES(?,?,?,?)",
                            (c_name.value,c_dur.value,c_chg.value,c_desc.value))
                con.commit();snack("Course added! ✅");clr(None);refresh_stats()
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def upd(e):
            if not sel[0]: snack("Select a course first!",WARNING);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("UPDATE course SET Duration=?,Charges=?,Description=? WHERE cid=?",
                            (c_dur.value,c_chg.value,c_desc.value,sel[0]))
                con.commit();snack("Updated! ✅");clr(None)
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def delete(e):
            if not sel[0]: snack("Select first!",WARNING);return
            def do(e):
                page.pop_dialog()
                con=get_connection();cur=con.cursor()
                try:
                    cur.execute("DELETE FROM course WHERE cid=?",(sel[0],))
                    con.commit();snack("Deleted!");clr(None);refresh_stats()
                except Exception as ex: snack(str(ex),DANGER)
                finally: con.close()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Confirm Delete",color=TEXT),
                content=ft.Text("Delete this course and all its subjects/exams?",color=SUBTEXT),
                actions=[ft.TextButton("Cancel",on_click=lambda e:page.pop_dialog()),
                         ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",on_click=do)],
                bgcolor=CARD))

        def clr(e):
            c_name.value="";c_dur.value="";c_chg.value=""
            c_desc.value="";sel[0]=None;c_name.read_only=False
            reload();page.update()

        reload()
        return ft.Row([
            ft.Container(width=300,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Course Details",ft.Icons.BOOK_ROUNDED),
                    ft.Divider(color=BORDER,height=8),
                    c_name,c_dur,c_chg,c_desc,
                    ft.Divider(color=BORDER,height=6),
                    ft.Row([
                        ft.ElevatedButton("Save",bgcolor=SUCCESS,color="white",icon=ft.Icons.SAVE_ROUNDED,on_click=add),
                        ft.ElevatedButton("Update",bgcolor=ACCENT,color="white",icon=ft.Icons.EDIT_ROUNDED,on_click=upd),
                    ],spacing=6),
                    ft.Row([
                        ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",icon=ft.Icons.DELETE_ROUNDED,on_click=delete),
                        ft.ElevatedButton("Clear",bgcolor="#374151",color="white",icon=ft.Icons.CLEAR_ROUNDED,on_click=clr),
                    ],spacing=6),
                ],spacing=8,scroll=ft.ScrollMode.AUTO)),
            ft.Container(expand=True,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("All Courses",ft.Icons.LIST_ROUNDED),
                    ft.Row([c_srch,
                            ft.IconButton(ft.Icons.SEARCH,icon_color=ACCENT2,on_click=lambda e:reload(c_srch.value)),
                            ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:reload())]),
                    ft.Container(ft.Column([tbl],scroll=ft.ScrollMode.AUTO),expand=True),
                ],spacing=8,expand=True)),
        ],spacing=14,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 3 — SUBJECTS
    # ══════════════════════════════════════════════════════════════════
    def build_subjects():
        courses = get_all_courses()
        s_course=ddl("Course",[( r[0],r[1]) for r in courses])
        s_name=inp("Subject Name",ft.Icons.SUBJECT_ROUNDED)
        s_max=inp("Max Marks",ft.Icons.NUMBERS)
        s_max.value="100"
        sel=[None]

        tbl=ft.DataTable(columns=table_hdr(["ID","Subject Name","Course","Max Marks"]),
            heading_row_color=CARD2,data_row_max_height=42,column_spacing=20,horizontal_margin=10)

        def reload():
            subs=get_all_subjects();tbl.rows=[]
            for r in subs:
                tbl.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]),color=SUBTEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[1]),color=TEXT,size=11,weight=ft.FontWeight.W_500),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[2]),color=SUBTEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[3]),color=WARNING,size=11),on_tap=lambda e,row=r:sel_row(row)),
                ]))
            page.update()

        def sel_row(r):
            sel[0]=r[0];s_name.value=r[1];s_max.value=str(r[3])
            # find course
            for c in courses:
                if c[1]==r[2]: s_course.value=str(c[0]);break
            page.update()

        def add(e):
            if not s_name.value.strip() or not s_course.value:
                snack("Subject name and course required!",DANGER);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("INSERT INTO subject(name,course_id,max_marks) VALUES(?,?,?)",
                            (s_name.value,s_course.value,s_max.value or 100))
                con.commit();snack("Subject added! ✅");clr(None)
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def upd(e):
            if not sel[0]: snack("Select a subject first!",WARNING);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("UPDATE subject SET name=?,course_id=?,max_marks=? WHERE sid=?",
                            (s_name.value,s_course.value,s_max.value,sel[0]))
                con.commit();snack("Updated! ✅");clr(None)
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def delete(e):
            if not sel[0]: snack("Select first!",WARNING);return
            def do(ev):
                page.pop_dialog()
                con=get_connection();cur=con.cursor()
                try:
                    cur.execute("DELETE FROM subject WHERE sid=?",(sel[0],))
                    con.commit();snack("Deleted!");clr(None)
                except Exception as ex: snack(str(ex),DANGER)
                finally: con.close()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Confirm Delete",color=TEXT),
                content=ft.Text("Delete this subject?",color=SUBTEXT),
                actions=[ft.TextButton("Cancel",on_click=lambda e:page.pop_dialog()),
                         ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",on_click=do)],
                bgcolor=CARD))

        def clr(e):
            s_name.value="";s_course.value=None;s_max.value="100";sel[0]=None
            reload();page.update()

        reload()
        return ft.Row([
            ft.Container(width=300,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Subject Details",ft.Icons.SUBJECT_ROUNDED),
                    ft.Divider(color=BORDER,height=8),
                    s_course,s_name,s_max,
                    ft.Divider(color=BORDER,height=6),
                    ft.Row([
                        ft.ElevatedButton("Save",bgcolor=SUCCESS,color="white",icon=ft.Icons.SAVE_ROUNDED,on_click=add),
                        ft.ElevatedButton("Update",bgcolor=ACCENT,color="white",icon=ft.Icons.EDIT_ROUNDED,on_click=upd),
                    ],spacing=6),
                    ft.Row([
                        ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",icon=ft.Icons.DELETE_ROUNDED,on_click=delete),
                        ft.ElevatedButton("Clear",bgcolor="#374151",color="white",icon=ft.Icons.CLEAR_ROUNDED,on_click=clr),
                    ],spacing=6),
                ],spacing=8)),
            ft.Container(expand=True,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("All Subjects",ft.Icons.LIST_ROUNDED),
                    ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:reload()),
                    ft.Container(ft.Column([tbl],scroll=ft.ScrollMode.AUTO),expand=True),
                ],spacing=8,expand=True)),
        ],spacing=14,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 4 — EXAMS
    # ══════════════════════════════════════════════════════════════════
    def build_exams():
        courses=get_all_courses()
        e_name=inp("Exam Name",ft.Icons.ASSIGNMENT_OUTLINED)
        e_course=ddl("Course",[(r[0],r[1]) for r in courses])
        e_type=ddl("Exam Type",["Theory","Practical","Mid-Term","Final","Assignment"])
        e_year=inp("Academic Year (e.g. 2025-26)",ft.Icons.CALENDAR_TODAY)
        e_year.value="2025-26"
        e_sem=ddl("Semester",["1","2","3","4","5","6","7","8"])
        sel=[None]

        tbl=ft.DataTable(columns=table_hdr(["ID","Exam Name","Type","Course","Year","Sem"]),
            heading_row_color=CARD2,data_row_max_height=42,column_spacing=16,horizontal_margin=10)

        def reload():
            exams=get_all_exams();tbl.rows=[]
            for r in exams:
                tbl.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]),color=SUBTEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[1]),color=TEXT,size=11,weight=ft.FontWeight.W_500),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[2]),color=WARNING,size=10),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[3]),color=SUBTEXT,size=10),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[4]),color=TEXT,size=10),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[5]),color=ACCENT2,size=11),on_tap=lambda e,row=r:sel_row(row)),
                ]))
            page.update()

        def sel_row(r):
            sel[0]=r[0];e_name.value=r[1];e_type.value=r[2]
            for c in courses:
                if c[1]==r[3]: e_course.value=str(c[0]);break
            e_year.value=r[4];e_sem.value=r[5];page.update()

        def add(e):
            if not e_name.value.strip() or not e_course.value:
                snack("Exam name and course required!",DANGER);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("INSERT INTO exam(name,exam_type,course_id,academic_year,semester) VALUES(?,?,?,?,?)",
                            (e_name.value,e_type.value or "Theory",e_course.value,
                             e_year.value,e_sem.value or "1"))
                con.commit();snack("Exam added! ✅");clr(None)
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def upd(e):
            if not sel[0]: snack("Select an exam first!",WARNING);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("UPDATE exam SET name=?,exam_type=?,course_id=?,academic_year=?,semester=? WHERE eid=?",
                            (e_name.value,e_type.value,e_course.value,e_year.value,e_sem.value,sel[0]))
                con.commit();snack("Updated! ✅");clr(None)
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def delete(e):
            if not sel[0]: snack("Select first!",WARNING);return
            def do(ev):
                page.pop_dialog()
                con=get_connection();cur=con.cursor()
                try:
                    cur.execute("DELETE FROM exam WHERE eid=?",(sel[0],))
                    con.commit();snack("Deleted!");clr(None)
                except Exception as ex: snack(str(ex),DANGER)
                finally: con.close()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Confirm Delete",color=TEXT),
                content=ft.Text("Delete this exam?",color=SUBTEXT),
                actions=[ft.TextButton("Cancel",on_click=lambda e:page.pop_dialog()),
                         ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",on_click=do)],
                bgcolor=CARD))

        def clr(e):
            e_name.value="";e_course.value=None;e_type.value=None
            e_year.value="2025-26";e_sem.value=None;sel[0]=None
            reload();page.update()

        reload()
        return ft.Row([
            ft.Container(width=300,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Exam Details",ft.Icons.ASSIGNMENT_ROUNDED),
                    ft.Divider(color=BORDER,height=8),
                    e_course,e_name,e_type,e_year,e_sem,
                    ft.Divider(color=BORDER,height=6),
                    ft.Row([
                        ft.ElevatedButton("Save",bgcolor=SUCCESS,color="white",icon=ft.Icons.SAVE_ROUNDED,on_click=add),
                        ft.ElevatedButton("Update",bgcolor=ACCENT,color="white",icon=ft.Icons.EDIT_ROUNDED,on_click=upd),
                    ],spacing=6),
                    ft.Row([
                        ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",icon=ft.Icons.DELETE_ROUNDED,on_click=delete),
                        ft.ElevatedButton("Clear",bgcolor="#374151",color="white",icon=ft.Icons.CLEAR_ROUNDED,on_click=clr),
                    ],spacing=6),
                ],spacing=8,scroll=ft.ScrollMode.AUTO)),
            ft.Container(expand=True,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("All Exams",ft.Icons.LIST_ROUNDED),
                    ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:reload()),
                    ft.Container(ft.Column([tbl],scroll=ft.ScrollMode.AUTO),expand=True),
                ],spacing=8,expand=True)),
        ],spacing=14,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 5 — STUDENTS
    # ══════════════════════════════════════════════════════════════════
    def build_students():
        s_roll=inp("Roll Number",ft.Icons.BADGE_OUTLINED)
        s_name=inp("Full Name",ft.Icons.PERSON_OUTLINED)
        s_email=inp("Email",ft.Icons.EMAIL_OUTLINED)
        s_contact=inp("Contact",ft.Icons.PHONE_OUTLINED)
        s_dob=inp("Date of Birth (DD/MM/YYYY)",ft.Icons.CAKE_OUTLINED)
        s_adm=inp("Admission Date",ft.Icons.CALENDAR_TODAY)
        s_city=inp("City",ft.Icons.LOCATION_CITY)
        s_pin=inp("Pin Code",ft.Icons.PIN_DROP_OUTLINED)
        s_address=inp("Address",ft.Icons.HOME_OUTLINED,multiline=True)
        s_srch=inp("Search by Roll",ft.Icons.SEARCH,expand=True)
        courses=get_all_courses()
        s_course=ddl("Course",[(r[0],r[1]) for r in courses])
        s_gender=ddl("Gender",["Male","Female","Other"])
        s_state=ddl("State",STATE_LIST)
        sel=[None]

        tbl=ft.DataTable(columns=table_hdr(["Roll","Name","Course","Contact","Email"]),
            heading_row_color=CARD2,data_row_max_height=42,column_spacing=16,horizontal_margin=10)

        def reload(q=""):
            con=get_connection();cur=con.cursor()
            if q: cur.execute("SELECT * FROM student WHERE roll=?",(q,))
            else: cur.execute("SELECT * FROM student")
            rows=cur.fetchall();con.close();tbl.rows=[]
            for r in rows:
                tbl.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]),color=ACCENT2,size=11,weight=ft.FontWeight.BOLD),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[1]),color=TEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[7]),color=SUBTEXT,size=10),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[5]),color=TEXT,size=11),on_tap=lambda e,row=r:sel_row(row)),
                    ft.DataCell(ft.Text(str(r[2]),color=SUBTEXT,size=10),on_tap=lambda e,row=r:sel_row(row)),
                ]))
            page.update()

        def sel_row(r):
            sel[0]=r[0];s_roll.read_only=True
            s_roll.value=str(r[0]);s_name.value=str(r[1]);s_email.value=str(r[2])
            s_gender.value=str(r[3]);s_dob.value=str(r[4]);s_contact.value=str(r[5])
            s_adm.value=str(r[6]);s_course.value=str(r[7]);s_state.value=str(r[8])
            s_city.value=str(r[9]);s_pin.value=str(r[10]);s_address.value=str(r[11])
            page.update()

        def add(e):
            if not s_roll.value.strip() or not s_name.value.strip():
                snack("Roll No. and Name required!",DANGER);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("SELECT * FROM student WHERE roll=?",(s_roll.value,))
                if cur.fetchone(): snack("Roll No. already exists!",WARNING);return
                cur.execute("INSERT INTO student VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(
                    s_roll.value,s_name.value,s_email.value,s_gender.value,
                    s_dob.value,s_contact.value,s_adm.value,s_course.value,
                    s_state.value,s_city.value,s_pin.value,s_address.value))
                con.commit();snack("Student added! ✅");clr(None);refresh_stats()
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def upd(e):
            if not sel[0]: snack("Select a student first!",WARNING);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("""UPDATE student SET name=?,email=?,gender=?,dob=?,
                    contact=?,admission=?,course=?,state=?,city=?,pin=?,address=? WHERE roll=?""",
                    (s_name.value,s_email.value,s_gender.value,s_dob.value,
                     s_contact.value,s_adm.value,s_course.value,s_state.value,
                     s_city.value,s_pin.value,s_address.value,sel[0]))
                con.commit();snack("Updated! ✅");clr(None)
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def delete(e):
            if not sel[0]: snack("Select first!",WARNING);return
            def do(ev):
                page.pop_dialog()
                con=get_connection();cur=con.cursor()
                try:
                    cur.execute("DELETE FROM student WHERE roll=?",(sel[0],))
                    con.commit();snack("Deleted!");clr(None);refresh_stats()
                except Exception as ex: snack(str(ex),DANGER)
                finally: con.close()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Confirm Delete",color=TEXT),
                content=ft.Text("Delete this student?",color=SUBTEXT),
                actions=[ft.TextButton("Cancel",on_click=lambda e:page.pop_dialog()),
                         ft.ElevatedButton("Delete",bgcolor=DANGER,color="white",on_click=do)],
                bgcolor=CARD))

        def clr(e):
            for f in [s_roll,s_name,s_email,s_contact,s_dob,s_adm,s_city,s_pin,s_address]:
                f.value=""
            s_gender.value=None;s_course.value=None;s_state.value=None
            s_roll.read_only=False;sel[0]=None;reload();page.update()

        reload()
        return ft.Row([
            ft.Container(width=360,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Student Details",ft.Icons.PERSON_ROUNDED),
                    ft.Divider(color=BORDER,height=6),
                    s_roll,
                    s_name,
                    s_email,
                    s_gender,
                    s_dob,
                    s_contact,
                    s_adm,
                    s_course,
                    s_state,
                    s_city,
                    s_pin,
                    s_address,
                    ft.Divider(color=BORDER,height=6),
                    ft.Row([
                        ft.ElevatedButton("Save",  bgcolor=SUCCESS,  color="white",icon=ft.Icons.SAVE_ROUNDED,   on_click=add, expand=True),
                        ft.ElevatedButton("Update",bgcolor=ACCENT,   color="white",icon=ft.Icons.EDIT_ROUNDED,   on_click=upd, expand=True),
                    ],spacing=6),
                    ft.Row([
                        ft.ElevatedButton("Delete",bgcolor=DANGER,   color="white",icon=ft.Icons.DELETE_ROUNDED, on_click=delete, expand=True),
                        ft.ElevatedButton("Clear", bgcolor="#374151", color="white",icon=ft.Icons.CLEAR_ROUNDED,  on_click=clr,    expand=True),
                    ],spacing=6),
                ],spacing=7,scroll=ft.ScrollMode.AUTO)),
            ft.Container(expand=True,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("All Students",ft.Icons.LIST_ROUNDED),
                    ft.Row([s_srch,
                            ft.IconButton(ft.Icons.SEARCH,icon_color=ACCENT2,on_click=lambda e:reload(s_srch.value)),
                            ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:reload())]),
                    ft.Container(ft.Column([tbl],scroll=ft.ScrollMode.AUTO),expand=True),
                ],spacing=8,expand=True)),
        ],spacing=14,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 6 — RESULTS (multi-subject)
    # ══════════════════════════════════════════════════════════════════
    def build_results():
        students=get_all_students()
        subjects=get_all_subjects()
        exams=get_all_exams()

        r_roll=ddl("Select Student (Roll No.)",[(str(s[0]),f"{s[0]} — {s[1]}") for s in students])
        r_name=inp("Student Name",ft.Icons.PERSON_OUTLINED,readonly=True)
        r_course=inp("Course",ft.Icons.BOOK_OUTLINED,readonly=True)
        r_sub=ddl("Subject",[(s[0],s[1]) for s in subjects])
        r_exam=ddl("Exam",[(e[0],f"{e[1]} ({e[2]})") for e in exams])
        r_marks=inp("Marks Obtained",ft.Icons.EDIT_NOTE_ROUNDED)
        r_full=inp("Full Marks",ft.Icons.NUMBERS)
        r_pct=inp("Percentage",ft.Icons.PERCENT,readonly=True)
        r_grade=ft.Text("",size=14,weight=ft.FontWeight.BOLD)
        sel=[None]

        tbl=ft.DataTable(columns=table_hdr(["Roll","Name","Subject","Exam","Marks","Full","%","Grade"]),
            heading_row_color=CARD2,data_row_max_height=42,column_spacing=12,horizontal_margin=10)

        def fetch_student(e):
            if not r_roll.value: return
            con=get_connection();cur=con.cursor()
            cur.execute("SELECT name,course FROM student WHERE roll=?",(r_roll.value,))
            row=cur.fetchone();con.close()
            if row: r_name.value=row[0];r_course.value=row[1]
            else: snack("Student not found!",DANGER)
            page.update()

        r_roll.on_change=fetch_student

        def calc(e):
            try:
                if r_marks.value and r_full.value:
                    pct=float(r_marks.value)/float(r_full.value)*100
                    r_pct.value=f"{pct:.2f}"
                    g,gc=get_grade(str(pct))
                    r_grade.value=g;r_grade.color=gc;page.update()
            except: pass

        r_marks.on_change=calc;r_full.on_change=calc

        def reload():
            con=get_connection();cur=con.cursor()
            cur.execute("""
                SELECT r.rid,r.roll,r.name,
                       COALESCE(s.name,r.course) as sub,
                       COALESCE(e.name,'—') as exam,
                       r.marks_ob,r.full_marks,
                       COALESCE(r.percent,r.marks_ob) as pct,
                       COALESCE(r.grade,'—') as grade
                FROM result r
                LEFT JOIN subject s ON r.subject_id=s.sid
                LEFT JOIN exam    e ON r.exam_id=e.eid
                ORDER BY r.rid DESC
            """)
            rows=cur.fetchall();con.close();tbl.rows=[]
            for res in rows:
                try: pct_f=float(res[7])
                except: pct_f=0
                g,gc=get_grade(str(pct_f))
                tbl.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(res[1]),color=ACCENT2,size=11),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Text(str(res[2]),color=TEXT,size=11),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Text(str(res[3]),color=SUBTEXT,size=10),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Text(str(res[4]),color=SUBTEXT,size=10),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Text(str(res[5]),color=TEXT,size=11),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Text(str(res[6]),color=TEXT,size=11),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Text(f"{pct_f:.1f}%",color=TEXT,size=11),on_tap=lambda e,row=res:sel_res(row)),
                    ft.DataCell(ft.Container(
                        ft.Text(g,color="white",size=9,weight=ft.FontWeight.BOLD),
                        bgcolor=gc,border_radius=5,
                        padding=ft.Padding.symmetric(horizontal=7,vertical=3)),
                        on_tap=lambda e,row=res:sel_res(row)),
                ]))
            page.update()

        def sel_res(res):
            sel[0]=res[0]
            r_roll.value=str(res[1]);r_name.value=str(res[2])
            r_marks.value=str(res[5]);r_full.value=str(res[6])
            try:
                pct=float(res[7]);r_pct.value=f"{pct:.2f}"
                g,gc=get_grade(str(pct));r_grade.value=g;r_grade.color=gc
            except: pass
            page.update()

        def add(e):
            if not r_roll.value or not r_marks.value or not r_full.value:
                snack("Fill all required fields!",DANGER);return
            try: pct=float(r_marks.value)/float(r_full.value)*100
            except: snack("Invalid marks!",DANGER);return
            g,_=get_grade(str(pct))
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("""INSERT INTO result
                    (roll,name,course,subject_id,exam_id,marks_ob,full_marks,percent,grade)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                    (r_roll.value,r_name.value,r_course.value,
                     r_sub.value,r_exam.value,
                     r_marks.value,r_full.value,str(round(pct,2)),g))
                con.commit()
                # Notify student
                try: send_notification(r_roll.value,"Result Published",
                    f"Your result for {r_name.value} has been published. Score: {r_marks.value}/{r_full.value} ({pct:.1f}%)")
                except: pass
                snack("Result added! ✅");clr(None);refresh_stats()
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def delete(e):
            if not sel[0]: snack("Select a result first!",WARNING);return
            con=get_connection();cur=con.cursor()
            try:
                cur.execute("DELETE FROM result WHERE rid=?",(sel[0],))
                con.commit();snack("Deleted!");clr(None);refresh_stats()
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        def clr(e):
            r_roll.value=None;r_name.value="";r_course.value=""
            r_sub.value=None;r_exam.value=None
            r_marks.value="";r_full.value="";r_pct.value=""
            r_grade.value="";sel[0]=None;reload();page.update()

        reload()
        return ft.Row([
            ft.Container(width=320,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Enter Result",ft.Icons.EDIT_NOTE_ROUNDED),
                    ft.Divider(color=BORDER,height=8),
                    r_roll,r_name,r_course,r_sub,r_exam,
                    r_marks,r_full,
                    ft.Row([r_pct,r_grade],spacing=10,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(color=BORDER,height=6),
                    ft.Row([
                        ft.ElevatedButton("Submit",bgcolor=SUCCESS,color="white",icon=ft.Icons.CHECK_CIRCLE,   on_click=add,    expand=True),
                        ft.ElevatedButton("Delete",bgcolor=DANGER, color="white",icon=ft.Icons.DELETE_ROUNDED, on_click=delete, expand=True),
                    ],spacing=6),
                    ft.Row([
                        ft.ElevatedButton("Clear",bgcolor="#374151",color="white",
                            icon=ft.Icons.CLEAR_ROUNDED,on_click=clr,
                            height=44,expand=True),
                    ]),
                ],spacing=8,scroll=ft.ScrollMode.AUTO)),
            ft.Container(expand=True,bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("All Results",ft.Icons.LIST_ROUNDED),
                    ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:reload()),
                    ft.Container(ft.Column([tbl],scroll=ft.ScrollMode.AUTO),expand=True),
                ],spacing=8,expand=True)),
        ],spacing=14,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 7 — ATTENDANCE
    # ══════════════════════════════════════════════════════════════════
    def build_attendance():
        students=get_all_students()
        courses=get_all_courses()

        a_course=ddl("Filter by Course",[(r[0],r[1]) for r in courses])
        a_date=inp("Date (YYYY-MM-DD)",ft.Icons.CALENDAR_TODAY)
        a_date.value=datetime.date.today().strftime("%Y-%m-%d")

        status_map={}  # roll -> status container

        def load_students_for_att(e=None):
            att_list.controls.clear()
            status_map.clear()
            for s in students:
                if a_course.value and str(s[7]) not in [c[1] for c in courses if str(c[0])==a_course.value]:
                    pass  # show all if course filter not matching
                rb = ft.RadioGroup(
                    value="P",
                    content=ft.Row([
                        ft.Radio(value="P",label="Present",fill_color=SUCCESS),
                        ft.Radio(value="A",label="Absent", fill_color=DANGER),
                        ft.Radio(value="L",label="Leave",  fill_color=WARNING),
                    ],spacing=10)
                )
                status_map[str(s[0])]=rb
                att_list.controls.append(
                    ft.Container(bgcolor=CARD2,border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=14,vertical=10),
                        content=ft.Row([
                            ft.Container(
                                ft.Text(str(s[0]),color=ACCENT2,size=11,weight=ft.FontWeight.BOLD),
                                width=50),
                            ft.Text(str(s[1]),color=TEXT,size=12,expand=True),
                            ft.Text(str(s[7]),color=SUBTEXT,size=10,width=120),
                            rb,
                        ],vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ))
            page.update()

        def save_attendance(e):
            if not a_date.value.strip(): snack("Enter date!",DANGER);return
            con=get_connection();cur=con.cursor()
            saved=0
            try:
                for roll,rb in status_map.items():
                    cur.execute("DELETE FROM attendance WHERE roll=? AND date=?",(roll,a_date.value))
                    cur.execute("INSERT INTO attendance(roll,date,status,marked_by) VALUES(?,?,?,?)",
                                (roll,a_date.value,rb.value,"admin"))
                    saved+=1
                con.commit();snack(f"Attendance saved for {saved} students! ✅")
            except Exception as ex: snack(str(ex),DANGER)
            finally: con.close()

        # Summary table
        summary_tbl=ft.DataTable(
            columns=table_hdr(["Roll","Name","Total Days","Present","Absent","Attendance %"]),
            heading_row_color=CARD2,data_row_max_height=40,column_spacing=16,horizontal_margin=10)

        def load_summary():
            summary_tbl.rows=[]
            con=get_connection();cur=con.cursor()
            for s in students:
                roll=str(s[0])
                cur.execute("SELECT COUNT(*) FROM attendance WHERE roll=?",(roll,))
                total=cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM attendance WHERE roll=? AND status='P'",(roll,))
                present=cur.fetchone()[0]
                absent=total-present
                pct=round(present/total*100,1) if total else 0
                color=SUCCESS if pct>=75 else (WARNING if pct>=50 else DANGER)
                summary_tbl.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(roll,color=ACCENT2,size=11)),
                    ft.DataCell(ft.Text(str(s[1]),color=TEXT,size=11)),
                    ft.DataCell(ft.Text(str(total),color=TEXT,size=11)),
                    ft.DataCell(ft.Text(str(present),color=SUCCESS,size=11)),
                    ft.DataCell(ft.Text(str(absent),color=DANGER,size=11)),
                    ft.DataCell(ft.Text(f"{pct}%",color=color,size=11,weight=ft.FontWeight.BOLD)),
                ]))
            con.close();page.update()

        att_list=ft.Column([],spacing=6,scroll=ft.ScrollMode.AUTO)
        load_students_for_att()
        load_summary()

        return ft.Column([
            ft.Row([
                ft.Container(expand=2,bgcolor=CARD,border_radius=14,
                    border=ft.Border.all(1,BORDER),padding=18,
                    content=ft.Column([
                        section_title("Mark Attendance",ft.Icons.FACT_CHECK_ROUNDED),
                        ft.Divider(color=BORDER,height=8),
                        ft.Row([a_date,a_course,
                                ft.ElevatedButton("Load",bgcolor=ACCENT,color="white",
                                    icon=ft.Icons.REFRESH,on_click=load_students_for_att),
                                ft.ElevatedButton("Save All",bgcolor=SUCCESS,color="white",
                                    icon=ft.Icons.SAVE_ROUNDED,on_click=save_attendance),
                               ],spacing=8),
                        ft.Divider(color=BORDER,height=6),
                        ft.Container(att_list,expand=True,height=320),
                    ],spacing=8)),
                ft.Container(expand=True,bgcolor=CARD,border_radius=14,
                    border=ft.Border.all(1,BORDER),padding=18,
                    content=ft.Column([
                        section_title("Attendance Summary",ft.Icons.ANALYTICS_ROUNDED),
                        ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:load_summary()),
                        ft.Container(ft.Column([summary_tbl],scroll=ft.ScrollMode.AUTO),expand=True),
                    ],spacing=8,expand=True)),
            ],spacing=14,vertical_alignment=ft.CrossAxisAlignment.START,expand=True),
        ],spacing=12,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 8 — NOTIFICATIONS
    # ══════════════════════════════════════════════════════════════════
    def build_notifications():
        students=get_all_students()
        n_to=ddl("Send To",[(str(s[0]),f"{s[0]} — {s[1]}") for s in students]+[("all","All Students")])
        n_title=inp("Notification Title",ft.Icons.TITLE)
        n_msg=inp("Message",ft.Icons.MESSAGE_OUTLINED,multiline=True)

        def send(e):
            if not n_title.value.strip() or not n_msg.value.strip():
                snack("Title and message required!",DANGER);return
            try:
                send_notification(n_to.value or "all",n_title.value,n_msg.value)
                snack("Notification sent! ✅")
                n_title.value="";n_msg.value="";page.update()
            except Exception as ex: snack(str(ex),DANGER)

        # Recent notifications
        notif_list=ft.Column([],spacing=8,scroll=ft.ScrollMode.AUTO)

        def load_notifs():
            notif_list.controls.clear()
            con=get_connection();cur=con.cursor()
            cur.execute("SELECT * FROM notification ORDER BY created_at DESC LIMIT 30")
            rows=cur.fetchall();con.close()
            if not rows:
                notif_list.controls.append(ft.Text("No notifications yet",color=SUBTEXT,size=12))
            for n in rows:
                notif_list.controls.append(
                    ft.Container(bgcolor=CARD2,border_radius=10,
                        border=ft.Border.all(1,BORDER),
                        padding=ft.Padding.symmetric(horizontal=14,vertical=10),
                        content=ft.Column([
                            ft.Row([
                                ft.Text(str(n[2]),color=TEXT,size=12,
                                        weight=ft.FontWeight.BOLD,expand=True),
                                ft.Text(f"To: Roll {n[1]}",color=SUBTEXT,size=10),
                                ft.Text(str(n[5])[:16],color=SUBTEXT,size=9),
                            ]),
                            ft.Text(str(n[3]),color=SUBTEXT,size=11),
                        ],spacing=4)))
            page.update()

        load_notifs()

        return ft.Row([
            ft.Container(width=320,bgcolor=CARD,border_radius=14,
                border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Send Notification",ft.Icons.NOTIFICATIONS_ROUNDED),
                    ft.Divider(color=BORDER,height=8),
                    n_to,n_title,n_msg,
                    ft.Divider(color=BORDER,height=6),
                    ft.ElevatedButton("Send",bgcolor=ACCENT,color="white",
                        icon=ft.Icons.SEND_ROUNDED,on_click=send,
                        height=44,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                ],spacing=8)),
            ft.Container(expand=True,bgcolor=CARD,border_radius=14,
                border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    section_title("Recent Notifications",ft.Icons.INBOX_ROUNDED),
                    ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,
                                  on_click=lambda e:load_notifs()),
                    ft.Container(notif_list,expand=True),
                ],spacing=8,expand=True)),
        ],spacing=14,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 9 — REPORTS
    # ══════════════════════════════════════════════════════════════════
    def build_reports():
        srch=inp("Enter Roll No. for Marksheet",ft.Icons.SEARCH)
        status=ft.Text("",size=11,color=SUCCESS)

        def open_pdf(path):
            try:
                import subprocess,sys
                if sys.platform=="win32": os.startfile(path)
                elif sys.platform=="darwin": subprocess.run(["open",path])
                else: subprocess.run(["xdg-open",path])
            except: pass
            snack(f"PDF saved: {path}",SUCCESS)

        def gen_marksheet(e):
            if not srch.value.strip(): snack("Enter Roll No.!",DANGER);return
            con=get_connection();cur=con.cursor()
            cur.execute("SELECT * FROM result WHERE roll=?",(srch.value,))
            res=cur.fetchone();con.close()
            if not res: snack("No result found!",WARNING);return
            path=f"marksheet_{srch.value}.pdf"
            generate_marksheet(None,res,path)
            status.value=f"Saved: {path}";page.update();open_pdf(path)

        def gen_topper(e):
            path="topper_list.pdf"
            r=generate_topper_list(path)
            if r: status.value=f"Saved: {path}";page.update();open_pdf(path)
            else: snack("No results available!",WARNING)

        def gen_subject(e):
            path="subject_report.pdf"
            r=generate_subject_report(path)
            if r: status.value=f"Saved: {path}";page.update();open_pdf(path)
            else: snack("No results available!",WARNING)

        def gen_full(e):
            path="full_result.pdf"
            r=generate_full_result_sheet(path)
            if r: status.value=f"Saved: {path}";page.update();open_pdf(path)
            else: snack("No results available!",WARNING)

        def rcard(icon,title,desc,color,btxt,fn):
            return ft.Container(expand=True,bgcolor=CARD,border_radius=14,
                border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    ft.Row([ft.Container(ft.Icon(icon,color=color,size=24),
                            bgcolor=f"{color}22",border_radius=8,padding=9),
                            ft.Column([ft.Text(title,size=12,weight=ft.FontWeight.BOLD,color=TEXT),
                                       ft.Text(desc,size=10,color=SUBTEXT)],spacing=2,expand=True)],spacing=10),
                    ft.Divider(color=BORDER,height=8),
                    ft.ElevatedButton(btxt,icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                        bgcolor=color,color="white",on_click=fn,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7))),
                ],spacing=7))

        return ft.Column([
            section_title("PDF Reports & Exports",ft.Icons.PICTURE_AS_PDF_ROUNDED),
            ft.Divider(color=BORDER,height=10),
            ft.Container(bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    ft.Row([ft.Container(ft.Icon(ft.Icons.PERSON_OUTLINED,color=ACCENT2,size=24),
                            bgcolor=f"{ACCENT2}22",border_radius=8,padding=9),
                            ft.Column([ft.Text("Individual Marksheet",size=12,weight=ft.FontWeight.BOLD,color=TEXT),
                                       ft.Text("Generate PDF for a specific student",size=10,color=SUBTEXT)],
                                      spacing=2,expand=True)],spacing=10),
                    ft.Row([srch,ft.ElevatedButton("Generate PDF",icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                        bgcolor=ACCENT2,color="white",on_click=gen_marksheet)],spacing=10),
                ],spacing=10)),
            ft.Row([
                rcard(ft.Icons.EMOJI_EVENTS_ROUNDED,"Class Topper List","Ranked by percentage",
                      WARNING,"Generate Topper List",gen_topper),
                rcard(ft.Icons.SUBJECT_ROUNDED,"Subject-wise Report","Course-wise analysis",
                      SUCCESS,"Generate Subject Report",gen_subject),
                rcard(ft.Icons.TABLE_CHART_ROUNDED,"Full Class Result","Complete sheet (landscape)",
                      PURPLE,"Generate Full Sheet",gen_full),
            ],spacing=14),
            ft.Divider(color=BORDER,height=6),
            status,
        ],spacing=10,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # SIDEBAR + LAYOUT
    # ══════════════════════════════════════════════════════════════════
    tab_labels=["Dashboard","Courses","Subjects","Exams","Students","Results","Attendance","Notifications","Reports"]
    tab_icons=[ft.Icons.DASHBOARD_ROUNDED,ft.Icons.BOOK_ROUNDED,ft.Icons.SUBJECT_ROUNDED,
               ft.Icons.ASSIGNMENT_ROUNDED,ft.Icons.PEOPLE_ROUNDED,ft.Icons.ANALYTICS_ROUNDED,
               ft.Icons.FACT_CHECK_ROUNDED,ft.Icons.NOTIFICATIONS_ROUNDED,ft.Icons.PICTURE_AS_PDF_ROUNDED]
    builders=[build_dashboard,build_courses,build_subjects,build_exams,
              build_students,build_results,build_attendance,build_notifications,build_reports]

    content_area=ft.Container(expand=True)
    nav_btns=[]

    def render(idx):
        for i,btn in enumerate(nav_btns):
            btn.bgcolor=ACCENT if i==idx else "transparent"
            btn.content.controls[0].color="white" if i==idx else SUBTEXT
            btn.content.controls[1].color="white" if i==idx else SUBTEXT
        content_area.content=ft.Container(expand=True,padding=20,content=builders[idx]())
        page.update()

    for i,(label,icon) in enumerate(zip(tab_labels,tab_icons)):
        btn=ft.Container(
            content=ft.Row([ft.Icon(icon,size=16,color=SUBTEXT),
                            ft.Text(label,size=12,color=SUBTEXT)],spacing=8),
            padding=ft.Padding.symmetric(horizontal=14,vertical=9),
            border_radius=8,bgcolor="transparent",
            on_click=lambda e,i=i:render(i),ink=True)
        nav_btns.append(btn)

    sidebar=ft.Container(width=190,bgcolor=CARD,
        padding=ft.Padding.symmetric(horizontal=8,vertical=16),
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SCHOOL_ROUNDED,size=24,color=ACCENT2),
                    ft.Text("SRMS",size=18,weight=ft.FontWeight.BOLD,color=ACCENT2)],spacing=8),
            ft.Divider(color=BORDER,height=16),
            ft.Container(bgcolor=INPUT_BG,border_radius=10,
                padding=ft.Padding.symmetric(horizontal=10,vertical=8),
                content=ft.Row([
                    ft.CircleAvatar(content=ft.Text(uname[0].upper(),color="white"),bgcolor=ACCENT,radius=16),
                    ft.Column([ft.Text(uname,size=11,color=TEXT,weight=ft.FontWeight.BOLD),
                               ft.Text("Administrator",size=9,color=SUBTEXT)],spacing=1,expand=True),
                ],spacing=8)),
            ft.Divider(color=BORDER,height=12),
            *nav_btns,
            ft.Container(expand=True),
            ft.Divider(color=BORDER,height=6),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.LOGOUT_ROUNDED,size=14,color=DANGER),
                                 ft.Text("Logout",size=12,color=DANGER)],spacing=8),
                padding=ft.Padding.symmetric(horizontal=14,vertical=9),
                border_radius=8,on_click=lambda e:on_logout(),ink=True),
        ],spacing=3,expand=True))

    page.add(ft.Row([sidebar,ft.VerticalDivider(width=1,color=BORDER),content_area],
                    expand=True,spacing=0))
    render(0)