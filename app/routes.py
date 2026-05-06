# from app.models import Group
from flask import render_template, request, redirect, url_for, flash, session

from app import app, db

from app.models import FEATURED_COURSES, UWA_UNITS, UWA_UNITS_BY_CODE


def _favorite_codes():
    return set(session.get("favorite_course_codes", []))


def _favorite_units():
    codes = _favorite_codes()
    return [u for u in UWA_UNITS if u["code"] in codes]


@app.route("/")
def index():
    return render_template("admin.html", courses=FEATURED_COURSES)


@app.route("/dashboard")
def dashboard():
    """Course grid + sidebar; used when guests choose Home from auth pages."""
    return render_template("admin.html", courses=FEATURED_COURSES)


@app.route("/course")
def course_list():
    per_page = 80
    page = request.args.get("page", default=1, type=int)
    q = request.args.get("q", default="", type=str).strip()
    q_lower = q.lower()
    favorite_codes = _favorite_codes()

    if q_lower:
        filtered_units = [
            u
            for u in UWA_UNITS
            if q_lower in u["code"].lower() or q_lower in u["title"].lower()
        ]
    else:
        filtered_units = UWA_UNITS

    non_favorite_units = [u for u in filtered_units if u["code"] not in favorite_codes]
    total = len(non_favorite_units)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    courses_page = non_favorite_units[start : start + per_page]
    showing_from = start + 1 if total else 0
    showing_to = min(page * per_page, total)
    return render_template(
        "courses.html",
        courses=courses_page,
        favorite_units=_favorite_units(),
        favorite_codes=favorite_codes,
        page=page,
        total_pages=total_pages,
        total_units=total,
        per_page=per_page,
        showing_from=showing_from,
        showing_to=showing_to,
        q=q,
    )


@app.route("/course/favorite/<course_code>", methods=["POST"])
def toggle_favorite_course(course_code):
    code = course_code.strip().upper()
    if code not in UWA_UNITS_BY_CODE:
        flash("Course not found.", "warning")
        return redirect(url_for("course_list"))

    favorites = _favorite_codes()
    if code in favorites:
        favorites.remove(code)
    else:
        favorites.add(code)
    session["favorite_course_codes"] = sorted(favorites)

    page = request.form.get("page", default=1, type=int)
    q = request.form.get("q", default="", type=str)
    return redirect(url_for("course_list", page=page, q=q))


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