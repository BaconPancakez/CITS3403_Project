# from app.models import Group
from flask import render_template, request, redirect, url_for, flash, session

from app import app, db

from app.models import MOCK_COURSES

@app.route("/")
def index():
    return render_template("home.html", courses=MOCK_COURSES)

@app.route("/admin")
def admin():
    return render_template("admin.html", courses=MOCK_COURSES)

@app.route("/course")
def course_list():
    return render_template("courses.html", courses=MOCK_COURSES)


@app.route("/course/<course_code>")
def course_detail(course_code):
    course = next((item for item in MOCK_COURSES if item["code"] == course_code), None)
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