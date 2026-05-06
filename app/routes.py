# from app.models import Group
from flask import render_template, request, redirect, url_for, flash, session
from jinja2 import TemplateNotFound

from app import app, db

from app.models import FEATURED_COURSES, UWA_UNITS, UWA_UNITS_BY_CODE


@app.route("/")
def index():
    if session.get("is_authenticated"):
        return render_template("admin.html", courses=FEATURED_COURSES)
    try:
        return render_template("landing.html")
    except TemplateNotFound:
        # e.g. clone without landing.html committed — keep site usable
        return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    """Course grid + sidebar; used when guests choose Home from auth pages."""
    return render_template("admin.html", courses=FEATURED_COURSES)


@app.route("/course")
def course_list():
    per_page = 80
    page = request.args.get("page", default=1, type=int)
    total = len(UWA_UNITS)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    courses_page = UWA_UNITS[start : start + per_page]
    showing_from = start + 1 if total else 0
    showing_to = min(page * per_page, total)
    return render_template(
        "courses.html",
        courses=courses_page,
        page=page,
        total_pages=total_pages,
        total_units=total,
        per_page=per_page,
        showing_from=showing_from,
        showing_to=showing_to,
    )


@app.route("/course/<course_code>")
def course_detail(course_code):
    course = UWA_UNITS_BY_CODE.get(course_code.strip().upper())
    if not course:
        flash("Course not found.", "warning")
        return redirect(url_for("course_list"))

    return render_template("coursepg.html", course=course)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("RAW FORM DATA:", request.form)

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if email == "admin@uwa.edu.au" and password == "1234":
            session["is_authenticated"] = True
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("is_authenticated", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))

        flash("Signup submitted.", "success")
        return redirect(url_for("signup"))

    return render_template("signup.html")

# if __name__ == "__main__":
#     app.run(debug=True)