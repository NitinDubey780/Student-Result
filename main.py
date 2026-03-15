import flet as ft
import os
from login_view import login_page
from admin_dashboard import admin_dashboard
from student_dashboard import student_dashboard


def main(page: ft.Page):
    page.title        = "Student Result Management System"
    page.window.width  = 1200
    page.window.height = 750
    page.window.min_width  = 900
    page.window.min_height = 600
    page.theme_mode   = ft.ThemeMode.DARK
    page.padding      = 0
    page.bgcolor      = "#0d1b2a"

    session = {"uid": None, "uname": None, "role": None, "roll_no": None}

    def on_login_success(uid, uname, role, roll_no):
        session.update(uid=uid, uname=uname, role=role, roll_no=roll_no)
        if role == "admin":
            admin_dashboard(page, uid, uname, on_logout)
        else:
            student_dashboard(page, uid, uname, roll_no, on_logout)

    def on_logout():
        session.update(uid=None, uname=None, role=None, roll_no=None)
        login_page(page, on_login_success)

    login_page(page, on_login_success)


if __name__ == "__main__":
    # Web deploy ke liye PORT env variable use karta hai
    port = int(os.environ.get("PORT", 8080))
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port,
    )