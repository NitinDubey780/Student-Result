import flet as ft
from connection import (get_connection, get_student_results, get_student_attendance,
                        get_attendance_summary, get_notifications, mark_notification_read,
                        get_grade)
from pdf_generator import generate_marksheet
import datetime, os

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

def student_dashboard(page: ft.Page, uid, uname, roll_no, on_logout):
    page.clean(); page.bgcolor=BG; page.padding=0

    def snack(msg, color=SUCCESS):
        page.snack_bar=ft.SnackBar(
            ft.Text(msg,color="white",weight=ft.FontWeight.W_500),
            bgcolor=color,duration=3000)
        page.snack_bar.open=True; page.update()

    # Fetch student info
    con=get_connection(); cur=con.cursor()
    cur.execute("SELECT * FROM student WHERE roll=?",(str(roll_no) if roll_no else "",))
    student=cur.fetchone(); con.close()

    results  = get_student_results(roll_no) if roll_no else []
    notifs   = get_notifications(roll_no)   if roll_no else []
    unread   = sum(1 for n in notifs if not n[4])

    # ══════════════════════════════════════════════════════════════════
    # TAB 1 — HOME
    # ══════════════════════════════════════════════════════════════════
    def build_home():
        if not student:
            return ft.Container(expand=True,
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING_ROUNDED,size=50,color=WARNING),
                    ft.Text("Profile not linked!",size=20,weight=ft.FontWeight.BOLD,color=TEXT),
                    ft.Text("Ask admin to link your roll number.",size=12,color=SUBTEXT),
                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  alignment=ft.MainAxisAlignment.CENTER,spacing=10))

        avg = sum(float(r[8]) for r in results)/len(results) if results else 0
        best= max(results,key=lambda x:float(x[8])) if results else None

        # Attendance summary
        total_att,present,absent,att_pct=get_attendance_summary(roll_no)
        att_color=SUCCESS if att_pct>=75 else (WARNING if att_pct>=50 else DANGER)

        def scard(label,val,icon,color):
            return ft.Container(expand=True,bgcolor=CARD,border_radius=12,
                border=ft.Border.all(1,BORDER),padding=14,
                content=ft.Row([
                    ft.Container(ft.Icon(icon,color=color,size=22),
                                 bgcolor=f"{color}22",border_radius=8,padding=8),
                    ft.Column([ft.Text(label,size=10,color=SUBTEXT),
                               ft.Text(str(val),size=20,weight=ft.FontWeight.BOLD,color=color)],
                              spacing=2),
                ],spacing=12))

        # Subject-wise results breakdown
        result_cards=[]
        for res in results:
            try: pct_f=float(res[8])
            except: pct_f=0
            g,gc=get_grade(str(pct_f))
            result_cards.append(
                ft.Container(bgcolor=CARD2,border_radius=10,
                    border=ft.Border.all(1,BORDER),
                    padding=ft.Padding.symmetric(horizontal=16,vertical=12),
                    content=ft.Row([
                        ft.Column([
                            ft.Text(str(res[4]),size=13,weight=ft.FontWeight.BOLD,color=TEXT),
                            ft.Text(f"Exam: {res[5]}",size=10,color=SUBTEXT),
                            ft.Text(f"Course: {res[3]}",size=10,color=SUBTEXT),
                        ],expand=True,spacing=2),
                        ft.Column([
                            ft.Text(f"{res[6]} / {res[7]}",size=12,color=TEXT),
                            ft.Text("marks",size=9,color=SUBTEXT),
                        ],spacing=1,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                            ft.Text(f"{pct_f:.1f}%",size=18,weight=ft.FontWeight.BOLD,color=gc),
                            ft.Container(
                                ft.Text(g,color="white",size=9,weight=ft.FontWeight.BOLD),
                                bgcolor=gc,border_radius=5,
                                padding=ft.Padding.symmetric(horizontal=7,vertical=3)),
                        ],spacing=4,horizontal_alignment=ft.CrossAxisAlignment.END),
                    ],vertical_alignment=ft.CrossAxisAlignment.CENTER)))

        # Recent notifications
        notif_cards=[]
        for n in notifs[:3]:
            notif_cards.append(
                ft.Container(bgcolor=CARD2,border_radius=8,
                    border=ft.Border.all(1,BORDER if n[4] else ACCENT),
                    padding=ft.Padding.symmetric(horizontal=12,vertical=8),
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ROUNDED,
                                color=SUBTEXT if n[4] else ACCENT2,size=16),
                        ft.Column([
                            ft.Text(str(n[2]),size=11,weight=ft.FontWeight.BOLD,color=TEXT),
                            ft.Text(str(n[3]),size=10,color=SUBTEXT),
                        ],spacing=2,expand=True),
                        ft.Text(str(n[5])[:10],size=9,color=SUBTEXT),
                    ],spacing=8,vertical_alignment=ft.CrossAxisAlignment.CENTER)))

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text(f"Hello, {student[1]} 👋",size=20,weight=ft.FontWeight.BOLD,color=TEXT),
                    ft.Text(datetime.datetime.now().strftime("%A, %d %B %Y"),size=11,color=SUBTEXT),
                ],expand=True,spacing=2),
                ft.Container(
                    ft.Text(f"Roll: {student[0]}",size=11,color=ACCENT2,weight=ft.FontWeight.BOLD),
                    bgcolor=f"{ACCENT2}22",border_radius=7,
                    padding=ft.Padding.symmetric(horizontal=12,vertical=6)),
            ]),
            ft.Divider(color=BORDER,height=12),
            ft.Row([
                scard("Course",    student[7],  ft.Icons.BOOK_ROUNDED,       ACCENT2),
                scard("Subjects",  len(results),ft.Icons.SUBJECT_ROUNDED,    SUCCESS),
                scard("Avg Score", f"{avg:.1f}%",ft.Icons.ANALYTICS_ROUNDED, WARNING),
                scard("Best Score",f"{float(best[8]):.1f}%" if best else "—",
                      ft.Icons.EMOJI_EVENTS_ROUNDED,PURPLE),
                scard("Attendance",f"{att_pct}%",ft.Icons.FACT_CHECK_ROUNDED,att_color),
            ],spacing=10),
            ft.Divider(color=BORDER,height=12),
            ft.Row([
                # Results
                ft.Container(expand=2,bgcolor=CARD,border_radius=14,
                    border=ft.Border.all(1,BORDER),padding=18,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.ANALYTICS_OUTLINED,color=ACCENT2,size=16),
                            ft.Text("My Subject Results",size=13,weight=ft.FontWeight.BOLD,color=TEXT),
                        ],spacing=6),
                        ft.Divider(color=BORDER,height=8),
                    ]+result_cards if result_cards else [
                        ft.Row([ft.Icon(ft.Icons.ANALYTICS_OUTLINED,color=ACCENT2,size=16),
                                ft.Text("My Results",size=13,weight=ft.FontWeight.BOLD,color=TEXT)],spacing=6),
                        ft.Text("No results yet.",color=SUBTEXT),
                    ],spacing=8,scroll=ft.ScrollMode.AUTO)),
                # Notifications
                ft.Container(expand=True,bgcolor=CARD,border_radius=14,
                    border=ft.Border.all(1,BORDER),padding=18,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED,color=ACCENT2,size=16),
                            ft.Text("Notifications",size=13,weight=ft.FontWeight.BOLD,color=TEXT),
                            ft.Container(
                                ft.Text(str(unread),color="white",size=9),
                                bgcolor=DANGER,border_radius=10,
                                padding=ft.Padding.symmetric(horizontal=6,vertical=2),
                                visible=unread>0),
                        ],spacing=6),
                        ft.Divider(color=BORDER,height=8),
                    ]+(notif_cards if notif_cards else [ft.Text("No notifications.",color=SUBTEXT,size=11)]),
                    spacing=6,scroll=ft.ScrollMode.AUTO)),
            ],spacing=14,vertical_alignment=ft.CrossAxisAlignment.START),
        ],spacing=10,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 2 — RESULTS (detailed)
    # ══════════════════════════════════════════════════════════════════
    def build_results():
        if not results:
            return ft.Container(expand=True,
                content=ft.Column([
                    ft.Icon(ft.Icons.ANALYTICS_OUTLINED,size=50,color=SUBTEXT),
                    ft.Text("No results available yet.",size=16,color=SUBTEXT),
                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  alignment=ft.MainAxisAlignment.CENTER,spacing=10))

        # Group by exam
        exam_map={}
        for r in results:
            key=r[5]  # exam name
            exam_map.setdefault(key,[]).append(r)

        sections=[]
        for exam_name,ress in exam_map.items():
            total_marks=sum(int(str(r[6]).split('.')[0]) for r in ress if r[6])
            total_full=sum(int(str(r[7]).split('.')[0]) for r in ress if r[7])
            overall_pct=total_marks/total_full*100 if total_full else 0
            overall_g,overall_gc=get_grade(str(overall_pct))

            rows=[]
            for r in ress:
                try: pct_f=float(r[8])
                except: pct_f=0
                g,gc=get_grade(str(pct_f))
                rows.append(ft.Container(bgcolor=CARD2,border_radius=8,
                    padding=ft.Padding.symmetric(horizontal=14,vertical=10),
                    content=ft.Row([
                        ft.Text(str(r[4]),color=TEXT,size=12,expand=True,weight=ft.FontWeight.W_500),
                        ft.Text(f"{r[6]} / {r[7]}",color=TEXT,size=12,width=80,text_align=ft.TextAlign.CENTER),
                        ft.Container(width=80,
                            content=ft.Stack([
                                ft.Container(bgcolor=CARD,border_radius=3,height=6,width=80),
                                ft.Container(bgcolor=gc,border_radius=3,height=6,
                                             width=max(2,pct_f*0.8)),
                            ])),
                        ft.Text(f"{pct_f:.1f}%",color=gc,size=12,
                                weight=ft.FontWeight.BOLD,width=55,text_align=ft.TextAlign.RIGHT),
                        ft.Container(
                            ft.Text(g,color="white",size=9,weight=ft.FontWeight.BOLD),
                            bgcolor=gc,border_radius=5,
                            padding=ft.Padding.symmetric(horizontal=7,vertical=3),width=90,
                            alignment=ft.Alignment.CENTER),
                    ],vertical_alignment=ft.CrossAxisAlignment.CENTER,spacing=10)))

            sections.append(ft.Container(bgcolor=CARD,border_radius=14,
                border=ft.Border.all(1,BORDER),padding=18,
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(exam_name,size=14,weight=ft.FontWeight.BOLD,color=TEXT),
                            ft.Text(f"Course: {ress[0][3]}",size=10,color=SUBTEXT),
                        ],expand=True,spacing=2),
                        ft.Column([
                            ft.Text(f"{overall_pct:.1f}%",size=20,
                                    weight=ft.FontWeight.BOLD,color=overall_gc),
                            ft.Container(
                                ft.Text(overall_g,color="white",size=10,weight=ft.FontWeight.BOLD),
                                bgcolor=overall_gc,border_radius=6,
                                padding=ft.Padding.symmetric(horizontal=10,vertical=4)),
                        ],horizontal_alignment=ft.CrossAxisAlignment.END,spacing=4),
                    ]),
                    ft.Divider(color=BORDER,height=8),
                    ft.Row([
                        ft.Text("Subject",color=SUBTEXT,size=10,expand=True),
                        ft.Text("Marks",color=SUBTEXT,size=10,width=80,text_align=ft.TextAlign.CENTER),
                        ft.Text("Progress",color=SUBTEXT,size=10,width=80),
                        ft.Text("%",color=SUBTEXT,size=10,width=55,text_align=ft.TextAlign.RIGHT),
                        ft.Text("Grade",color=SUBTEXT,size=10,width=90),
                    ],spacing=10),
                    *rows,
                    ft.Divider(color=BORDER,height=4),
                    ft.Row([
                        ft.Text(f"Total: {total_marks}/{total_full}",
                                size=12,color=TEXT,weight=ft.FontWeight.BOLD),
                        ft.Text(f"Overall: {overall_pct:.2f}%",
                                size=12,color=overall_gc,weight=ft.FontWeight.BOLD),
                    ],spacing=20),
                ],spacing=8)))

        return ft.Column(sections,spacing=14,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 3 — ATTENDANCE
    # ══════════════════════════════════════════════════════════════════
    def build_attendance():
        total,present,absent,pct=get_attendance_summary(roll_no)
        att_color=SUCCESS if pct>=75 else (WARNING if pct>=50 else DANGER)

        records=get_student_attendance(roll_no)

        def acard(label,val,color):
            return ft.Container(expand=True,bgcolor=CARD,border_radius=12,
                border=ft.Border.all(1,BORDER),padding=16,
                content=ft.Column([
                    ft.Text(label,size=11,color=SUBTEXT),
                    ft.Text(str(val),size=26,weight=ft.FontWeight.BOLD,color=color),
                ],spacing=4,horizontal_alignment=ft.CrossAxisAlignment.CENTER))

        rec_rows=[]
        for r in records[:30]:
            sc=SUCCESS if r[3]=="P" else (WARNING if r[3]=="L" else DANGER)
            lbl={"P":"Present","A":"Absent","L":"Leave"}.get(r[3],r[3])
            rec_rows.append(ft.Container(bgcolor=CARD2,border_radius=8,
                padding=ft.Padding.symmetric(horizontal=14,vertical=10),
                content=ft.Row([
                    ft.Text(str(r[2]),color=TEXT,size=12,expand=True),
                    ft.Container(
                        ft.Text(lbl,color="white",size=10,weight=ft.FontWeight.BOLD),
                        bgcolor=sc,border_radius=5,
                        padding=ft.Padding.symmetric(horizontal=10,vertical=4)),
                ],vertical_alignment=ft.CrossAxisAlignment.CENTER)))

        return ft.Column([
            ft.Row([
                acard("Total Days",total,SUBTEXT),
                acard("Present",present,SUCCESS),
                acard("Absent",absent,DANGER),
                ft.Container(expand=True,bgcolor=CARD,border_radius=12,
                    border=ft.Border.all(1,att_color),padding=16,
                    content=ft.Column([
                        ft.Text("Attendance %",size=11,color=SUBTEXT),
                        ft.Text(f"{pct}%",size=26,weight=ft.FontWeight.BOLD,color=att_color),
                        ft.Container(bgcolor=CARD2,border_radius=4,height=6,
                            content=ft.Container(bgcolor=att_color,border_radius=4,
                                height=6,width=pct*1.2 if pct else 0)),
                        ft.Text("Min 75% required",size=9,color=SUBTEXT),
                    ],spacing=4,horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
            ],spacing=12),
            ft.Divider(color=BORDER,height=14),
            ft.Container(bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),
                padding=18,expand=True,
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED,color=ACCENT2,size=16),
                            ft.Text("Attendance Record",size=13,weight=ft.FontWeight.BOLD,color=TEXT)],spacing=6),
                    ft.Divider(color=BORDER,height=8),
                ]+(rec_rows if rec_rows else [ft.Text("No records found.",color=SUBTEXT,size=12)]),
                spacing=6,scroll=ft.ScrollMode.AUTO)),
        ],spacing=12,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 4 — NOTIFICATIONS
    # ══════════════════════════════════════════════════════════════════
    def build_notifications():
        notif_col=ft.Column([],spacing=8,scroll=ft.ScrollMode.AUTO)

        def load():
            notif_col.controls.clear()
            ns=get_notifications(roll_no)
            if not ns:
                notif_col.controls.append(
                    ft.Text("No notifications yet.",color=SUBTEXT,size=12))
            for n in ns:
                is_read=bool(n[4])
                notif_col.controls.append(
                    ft.Container(bgcolor=CARD2,border_radius=10,
                        border=ft.Border.all(1,BORDER if is_read else ACCENT),
                        padding=ft.Padding.symmetric(horizontal=16,vertical=12),
                        on_click=lambda e,nid=n[0]:mark_and_reload(nid),
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.NOTIFICATIONS_ROUNDED,
                                        color=SUBTEXT if is_read else ACCENT2,size=16),
                                ft.Text(str(n[2]),size=12,weight=ft.FontWeight.BOLD,
                                        color=SUBTEXT if is_read else TEXT,expand=True),
                                ft.Text(str(n[5])[:10],size=9,color=SUBTEXT),
                                ft.Container(
                                    ft.Text("NEW",color="white",size=8),
                                    bgcolor=ACCENT,border_radius=4,
                                    padding=ft.Padding.symmetric(horizontal=5,vertical=2),
                                    visible=not is_read),
                            ],spacing=8,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Text(str(n[3]),size=11,color=SUBTEXT),
                        ],spacing=4)))
            page.update()

        def mark_and_reload(nid):
            mark_notification_read(nid);load()

        load()
        return ft.Container(expand=True,bgcolor=CARD,border_radius=14,
            border=ft.Border.all(1,BORDER),padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ROUNDED,color=ACCENT2,size=18),
                    ft.Text("Notifications",size=14,weight=ft.FontWeight.BOLD,color=TEXT),
                    ft.Container(expand=True),
                    ft.TextButton("Mark all read",
                        on_click=lambda e:[mark_notification_read(n[0]) for n in get_notifications(roll_no)] or load()),
                    ft.IconButton(ft.Icons.REFRESH,icon_color=SUBTEXT,on_click=lambda e:load()),
                ],spacing=8),
                ft.Divider(color=BORDER,height=8),
                ft.Container(notif_col,expand=True),
            ],spacing=6))

    # ══════════════════════════════════════════════════════════════════
    # TAB 5 — PROFILE
    # ══════════════════════════════════════════════════════════════════
    def build_profile():
        if not student:
            return ft.Text("No profile found.",color=SUBTEXT,size=13)

        def irow(icon,label,val):
            return ft.Container(bgcolor=CARD2,border_radius=8,
                border=ft.Border.all(1,BORDER),
                padding=ft.Padding.symmetric(horizontal=16,vertical=10),
                content=ft.Row([
                    ft.Icon(icon,color=ACCENT2,size=16),
                    ft.Text(label+":",size=11,color=SUBTEXT,width=120),
                    ft.Text(str(val),size=12,color=TEXT,expand=True),
                ],spacing=10))

        return ft.Column([
            ft.Row([
                ft.CircleAvatar(content=ft.Text(student[1][0].upper(),size=28,color="white",
                                                weight=ft.FontWeight.BOLD),
                                bgcolor=ACCENT,radius=40),
                ft.Column([
                    ft.Text(student[1],size=20,weight=ft.FontWeight.BOLD,color=TEXT),
                    ft.Text(f"Roll No: {student[0]}",size=12,color=ACCENT2),
                    ft.Text(f"Course: {student[7]}",size=11,color=SUBTEXT),
                ],spacing=4),
            ],spacing=18),
            ft.Divider(color=BORDER,height=16),
            ft.Container(bgcolor=CARD,border_radius=14,border=ft.Border.all(1,BORDER),
                padding=18,
                content=ft.Column([
                    ft.Text("Personal Information",size=13,weight=ft.FontWeight.BOLD,color=TEXT),
                    ft.Divider(color=BORDER,height=8),
                    irow(ft.Icons.EMAIL_OUTLINED,     "Email",     student[2]),
                    irow(ft.Icons.PEOPLE_OUTLINED,    "Gender",    student[3]),
                    irow(ft.Icons.CAKE_OUTLINED,      "DOB",       student[4]),
                    irow(ft.Icons.PHONE_OUTLINED,     "Contact",   student[5]),
                    irow(ft.Icons.CALENDAR_TODAY,     "Admission", student[6]),
                    irow(ft.Icons.LOCATION_ON_OUTLINED,"State",   student[8]),
                    irow(ft.Icons.LOCATION_CITY,      "City",      student[9]),
                    irow(ft.Icons.PIN_DROP_OUTLINED,  "Pin Code",  student[10]),
                    irow(ft.Icons.HOME_OUTLINED,      "Address",   student[11]),
                ],spacing=7)),
        ],spacing=12,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 6 — MARKSHEET (PDF)
    # ══════════════════════════════════════════════════════════════════
    def build_marksheet():
        pdf_status=ft.Text("",size=11,color=SUCCESS)

        if not results:
            return ft.Container(expand=True,
                content=ft.Column([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF_OUTLINED,size=50,color=SUBTEXT),
                    ft.Text("No results available yet.",size=16,color=SUBTEXT),
                ],horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  alignment=ft.MainAxisAlignment.CENTER,spacing=10))

        def dl_pdf(e,res):
            path=f"marksheet_{res[1]}_sub{res[0]}.pdf"
            # Build compatible result tuple for pdf_generator
            compat=(res[0],res[1],res[2],res[3],res[6],res[7],res[8])
            generate_marksheet(None,compat,path)
            pdf_status.value=f"Saved: {path}";page.update()
            try:
                import subprocess,sys
                if sys.platform=="win32": os.startfile(path)
                elif sys.platform=="darwin": subprocess.run(["open",path])
                else: subprocess.run(["xdg-open",path])
            except: pass

        # Group by exam
        exam_map={}
        for r in results:
            exam_map.setdefault(r[5],[]).append(r)

        cards=[]
        for exam_name,ress in exam_map.items():
            try:
                total_m=sum(int(str(r[6]).split('.')[0]) for r in ress if r[6])
                total_f=sum(int(str(r[7]).split('.')[0]) for r in ress if r[7])
                overall_pct=total_m/total_f*100 if total_f else 0
            except: overall_pct=0
            g,gc=get_grade(str(overall_pct))

            subject_rows=[]
            for r in ress:
                try: pf=float(r[8])
                except: pf=0
                sg,sgc=get_grade(str(pf))
                subject_rows.append(ft.Row([
                    ft.Text(str(r[4]),color=TEXT,size=11,expand=True),
                    ft.Text(f"{r[6]}/{r[7]}",color=TEXT,size=11,width=70,text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{pf:.1f}%",color=sgc,size=11,weight=ft.FontWeight.BOLD,width=55),
                    ft.Container(ft.Text(sg,color="white",size=9,weight=ft.FontWeight.BOLD),
                        bgcolor=sgc,border_radius=4,
                        padding=ft.Padding.symmetric(horizontal=6,vertical=2),width=80,
                        alignment=ft.Alignment.CENTER),
                ],spacing=8,vertical_alignment=ft.CrossAxisAlignment.CENTER))

            cards.append(ft.Container(bgcolor=CARD,border_radius=14,
                border=ft.Border.all(1,BORDER),padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(exam_name,size=14,weight=ft.FontWeight.BOLD,color=TEXT),
                            ft.Text(f"{ress[0][3]}  |  Roll: {ress[0][1]}",size=10,color=SUBTEXT),
                        ],expand=True,spacing=2),
                        ft.Column([
                            ft.Text(f"{overall_pct:.1f}%",size=20,weight=ft.FontWeight.BOLD,color=gc),
                            ft.Container(ft.Text(g,color="white",size=10,weight=ft.FontWeight.BOLD),
                                bgcolor=gc,border_radius=6,
                                padding=ft.Padding.symmetric(horizontal=10,vertical=4)),
                        ],horizontal_alignment=ft.CrossAxisAlignment.END,spacing=4),
                    ]),
                    ft.Divider(color=BORDER,height=8),
                    ft.Row([ft.Text("Subject",color=SUBTEXT,size=9,expand=True),
                            ft.Text("Marks",color=SUBTEXT,size=9,width=70,text_align=ft.TextAlign.CENTER),
                            ft.Text("%",color=SUBTEXT,size=9,width=55),
                            ft.Text("Grade",color=SUBTEXT,size=9,width=80)],spacing=8),
                    *subject_rows,
                    ft.Divider(color=BORDER,height=8),
                    ft.ElevatedButton(f"Download PDF — {exam_name}",
                        icon=ft.Icons.DOWNLOAD_ROUNDED,
                        bgcolor=ACCENT,color="white",
                        on_click=lambda e,r=ress[0]:dl_pdf(e,r),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7))),
                ],spacing=8)))

        return ft.Column([*cards,pdf_status],spacing=14,scroll=ft.ScrollMode.AUTO,expand=True)

    # ══════════════════════════════════════════════════════════════════
    # LAYOUT
    # ══════════════════════════════════════════════════════════════════
    tab_labels=["Home","Results","Attendance","Notifications","Profile","Marksheet"]
    tab_icons=[ft.Icons.HOME_ROUNDED,ft.Icons.ANALYTICS_ROUNDED,
               ft.Icons.FACT_CHECK_ROUNDED,ft.Icons.NOTIFICATIONS_ROUNDED,
               ft.Icons.PERSON_ROUNDED,ft.Icons.PICTURE_AS_PDF_ROUNDED]
    builders=[build_home,build_results,build_attendance,
              build_notifications,build_profile,build_marksheet]

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
        badge=None
        if label=="Notifications" and unread>0:
            badge=ft.Badge(ft.Text(str(unread),color="white",size=8),bgcolor=DANGER)
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
                    ft.CircleAvatar(content=ft.Text(uname[0].upper(),color="white"),
                                    bgcolor=SUCCESS,radius=16),
                    ft.Column([ft.Text(uname,size=11,color=TEXT,weight=ft.FontWeight.BOLD),
                               ft.Text("Student",size=9,color=SUBTEXT)],spacing=1,expand=True),
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