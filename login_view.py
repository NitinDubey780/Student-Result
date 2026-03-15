import flet as ft
from connection import verify_user, register_user

BG        = "#0d1b2a"
CARD      = "#1b2d3e"
ACCENT    = "#1976d2"
ACCENT2   = "#42a5f5"
SUCCESS   = "#00897b"
DANGER    = "#e53935"
TEXT      = "#e8f4fd"
SUBTEXT   = "#7fa8c9"
BORDER    = "#2a4a6b"
INPUT_BG  = "#112030"
HIGHLIGHT = "#1565c0"


def _stat_chip(icon, label):
    return ft.Container(
        content=ft.Column(
            [ft.Icon(icon, color="white", size=20),
             ft.Text(label, color="white", size=10)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        bgcolor="#ffffff22",
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=14, vertical=8),
    )


def login_page(page: ft.Page, on_login_success):
    page.clean()
    page.bgcolor = BG
    page.padding = 0

    is_login = [True]

    def show_snack(msg, color=SUCCESS):
        page.snack_bar = ft.SnackBar(
            ft.Text(msg, color="white", weight=ft.FontWeight.W_500),
            bgcolor=color, duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    username_field = ft.TextField(
        label="Username", prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=10, cursor_color=ACCENT2,
    )
    password_field = ft.TextField(
        label="Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True, can_reveal_password=True,
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=10, cursor_color=ACCENT2,
    )
    confirm_field = ft.TextField(
        label="Confirm Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True, can_reveal_password=True,
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=10, cursor_color=ACCENT2,
        visible=False,
    )
    roll_field = ft.TextField(
        label="Roll Number (students only)", prefix_icon=ft.Icons.BADGE_OUTLINED,
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=10, cursor_color=ACCENT2,
        visible=False,
    )
    role_dropdown = ft.Dropdown(
        label="Register As",
        options=[ft.dropdown.Option("student", "Student"),
                 ft.dropdown.Option("admin",   "Admin")],
        value="student",
        border_color=BORDER, focused_border_color=ACCENT2,
        label_style=ft.TextStyle(color=SUBTEXT),
        text_style=ft.TextStyle(color=TEXT),
        bgcolor=INPUT_BG, border_radius=10,
        visible=False,
    )

    title_text = ft.Text("Welcome Back", size=26, weight=ft.FontWeight.BOLD, color=TEXT)
    sub_text   = ft.Text("Sign in to continue", size=13, color=SUBTEXT)
    toggle_btn = ft.TextButton(
        "Don't have an account? Register",
        style=ft.ButtonStyle(color=ACCENT2),
    )
    action_btn = ft.ElevatedButton(
        "Sign In", width=320, height=46,
        style=ft.ButtonStyle(
            bgcolor=ACCENT, color="white",
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=4,
        ),
    )
    loading = ft.ProgressRing(
        width=22, height=22, stroke_width=2.5,
        color=ACCENT2, visible=False,
    )

    def toggle_mode(e):
        is_login[0] = not is_login[0]
        if is_login[0]:
            title_text.value      = "Welcome Back"
            sub_text.value        = "Sign in to continue"
            action_btn.text       = "Sign In"
            toggle_btn.text       = "Don't have an account? Register"
            confirm_field.visible = False
            roll_field.visible    = False
            role_dropdown.visible = False
        else:
            title_text.value      = "Create Account"
            sub_text.value        = "Register to get started"
            action_btn.text       = "Register"
            toggle_btn.text       = "Already have an account? Sign In"
            confirm_field.visible = True
            roll_field.visible    = True
            role_dropdown.visible = True
        page.update()

    toggle_btn.on_click = toggle_mode

    def handle_action(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        if not username or not password:
            show_snack("Please fill all required fields!", DANGER)
            return
        loading.visible     = True
        action_btn.disabled = True
        page.update()

        if is_login[0]:
            result = verify_user(username, password)
            if result:
                uid, uname, role, roll_no = result
                loading.visible     = False
                action_btn.disabled = False
                page.update()
                show_snack(f"Welcome, {uname}!", SUCCESS)
                on_login_success(uid, uname, role, roll_no)
            else:
                loading.visible     = False
                action_btn.disabled = False
                show_snack("Invalid username or password!", DANGER)
        else:
            confirm = confirm_field.value.strip()
            if password != confirm:
                loading.visible     = False
                action_btn.disabled = False
                show_snack("Passwords do not match!", DANGER)
                return
            ok, msg = register_user(username, password,
                                    role_dropdown.value,
                                    roll_field.value.strip() or None)
            loading.visible     = False
            action_btn.disabled = False
            if ok:
                show_snack(msg + " Please sign in.", SUCCESS)
                toggle_mode(None)
            else:
                show_snack(msg, DANGER)
        page.update()

    action_btn.on_click      = handle_action
    password_field.on_submit = handle_action

    left_panel = ft.Container(
        width=400,
        bgcolor=CARD,
        border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
        padding=ft.Padding.symmetric(horizontal=36, vertical=44),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=0,
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=34, color=ACCENT2),
                    ft.Text("SRMS", size=24, weight=ft.FontWeight.BOLD, color=ACCENT2),
                ], spacing=10),
                ft.Divider(color=BORDER, height=28),
                title_text, sub_text,
                ft.Divider(color="transparent", height=10),
                username_field,
                ft.Divider(color="transparent", height=8),
                password_field,
                ft.Divider(color="transparent", height=6),
                confirm_field,
                ft.Divider(color="transparent", height=4),
                roll_field,
                ft.Divider(color="transparent", height=4),
                role_dropdown,
                ft.Divider(color="transparent", height=14),
                ft.Row([action_btn, loading],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Divider(color="transparent", height=4),
                ft.Row([toggle_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(color=BORDER, height=24),
                ft.Text("Default Admin: admin / admin123",
                        size=11, color=SUBTEXT, italic=True,
                        text_align=ft.TextAlign.CENTER),
            ],
        ),
    )

    right_panel = ft.Container(
        expand=True,
        bgcolor=HIGHLIGHT,
        border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=80, color="white"),
                ft.Text("Student Result\nManagement System",
                        size=28, weight=ft.FontWeight.BOLD,
                        color="white", text_align=ft.TextAlign.CENTER),
                ft.Divider(color="transparent", height=10),
                ft.Text("Manage courses, students,\nresults & reports effortlessly.",
                        size=13, color="#90caf9", text_align=ft.TextAlign.CENTER),
                ft.Divider(color="transparent", height=28),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, spacing=12,
                    controls=[
                        _stat_chip(ft.Icons.BOOK_OUTLINED,      "Courses"),
                        _stat_chip(ft.Icons.PEOPLE_OUTLINED,    "Students"),
                        _stat_chip(ft.Icons.ANALYTICS_OUTLINED, "Results"),
                    ],
                ),
            ],
        ),
    )

    page.add(
        ft.Container(
            expand=True,
            bgcolor=BG,
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                height=580, width=860,
                border_radius=20,
                shadow=ft.BoxShadow(
                    blur_radius=40, color="#00000066",
                    offset=ft.Offset(0, 10),
                ),
                content=ft.Row(controls=[left_panel, right_panel], spacing=0),
            ),
        )
    )