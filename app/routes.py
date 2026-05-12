from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from app.models import FEATURED_COURSES, UWA_UNITS, UWA_UNITS_BY_CODE, User, Review, Discussion

FORGOT_RESET_EMAIL = "forgot_reset_email"


def _favorite_codes():
    return set(session.get("favorite_course_codes", []))


def _favorite_units():
    codes = _favorite_codes()
    return [u for u in UWA_UNITS if u["code"] in codes]


# ── Public routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:                           # already logged in
        return redirect(url_for("home"))

    if request.method == "POST":
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))           # optional "remember me" checkbox

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.name or user.email}!", "success")

        if user.role == "admin":
            return redirect(url_for("admin"))
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        name             = request.form.get("name",             "").strip()
        email            = request.form.get("email",            "").strip().lower()
        password         = request.form.get("password",         "")
        confirm_password = request.form.get("confirm_password", "")

        # ── Validation ────────────────────────────────────────────────────────
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("signup"))

        # ── Create user ───────────────────────────────────────────────────────
        role = "admin" if email.endswith("@uwa.edu.au") and not email.endswith("@student.uwa.edu.au") else "student"
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created — please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("favorite_course_codes", None)                  # clear session-only data
    session.pop(FORGOT_RESET_EMAIL, None)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Please enter your email.", "danger")
            return redirect(url_for("forgot_password"))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("We could not find an account with that email.", "danger")
            return redirect(url_for("forgot_password"))

        session[FORGOT_RESET_EMAIL] = email
        return redirect(url_for("forgot_password_new_password"))

    return render_template("forgot_password.html")


@app.route("/forgot-password/new-password", methods=["GET", "POST"])
def forgot_password_new_password():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    email = session.get(FORGOT_RESET_EMAIL)
    if not email:
        flash("Enter your email on the forgot password page first.", "warning")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not password or not confirm_password:
            flash("Both password fields are required.", "danger")
            return redirect(url_for("forgot_password_new_password"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("forgot_password_new_password"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("forgot_password_new_password"))

        user = User.query.filter_by(email=email).first()
        if not user:
            session.pop(FORGOT_RESET_EMAIL, None)
            flash("Account not found.", "danger")
            return redirect(url_for("forgot_password"))

        user.set_password(password)
        db.session.commit()
        session.pop(FORGOT_RESET_EMAIL, None)
        flash("Your password has been updated. You can sign in.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password_new_password.html")


# ── Protected routes ──────────────────────────────────────────────────────────

@app.route("/home")
@login_required
def home():
    return render_template("home.html", courses=FEATURED_COURSES, favorite_units=_favorite_units())


@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        flash("Admins only.", "danger")
        return redirect(url_for("home"))
    return render_template("admin.html", courses=FEATURED_COURSES, favorite_units=_favorite_units())


@app.route("/course")
@login_required
def course_list():
    q               = request.args.get("q",              default="", type=str).strip()
    school_filter   = request.args.get("school",         default="", type=str).strip()
    level_filter    = request.args.get("level_of_study", default="", type=str).strip()
    location_filter = request.args.get("location",       default="", type=str).strip()

    q_lower        = q.lower()
    favorite_codes = _favorite_codes()
    filtered_units = UWA_UNITS

    if q_lower:
        filtered_units = [
            u for u in filtered_units
            if q_lower in u["code"].lower() or q_lower in u["title"].lower()
        ]
    if school_filter:
        filtered_units = [u for u in filtered_units if u.get("school") == school_filter]
    if level_filter:
        filtered_units = [u for u in filtered_units if level_filter in u.get("level_of_study", "")]
    if location_filter:
        filtered_units = [u for u in filtered_units if location_filter in u.get("location", "")]

    courses = [u for u in filtered_units if u["code"] not in favorite_codes]

    schools   = sorted({u["school"] for u in UWA_UNITS if u.get("school")})
    levels    = sorted({
        lvl
        for u in UWA_UNITS
        for lvl in u.get("level_of_study", "").split(" | ")
        if lvl
    })
    locations = sorted({
        loc
        for u in UWA_UNITS
        for loc in u.get("location", "").split(" | ")
        if loc
    })

    return render_template(
        "courses.html",
        courses=courses,
        favorite_units=_favorite_units(),
        favorite_codes=favorite_codes,
        q=q,
        school_filter=school_filter,
        level_filter=level_filter,
        location_filter=location_filter,
        schools=schools,
        levels=levels,
        locations=locations,
    )


@app.route("/course/favorite/<course_code>", methods=["POST"])
@login_required
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

    return redirect(url_for(
        "course_list",
        q=request.form.get("q", ""),
        school=request.form.get("school", ""),
        level_of_study=request.form.get("level_of_study", ""),
        location=request.form.get("location", ""),
    ))


@app.route("/course/<course_code>", methods=["GET", "POST"])
@login_required
def course_detail(course_code):
    course = UWA_UNITS_BY_CODE.get(course_code.strip().upper())

    if not course:
        flash("Course not found.", "warning")
        return redirect(url_for("course_list"))

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "review":
            rating = int(request.form.get("rating", 0))
            text   = request.form.get("review_text", "").strip()

            if rating < 1 or rating > 5:
                flash("Rating must be between 1 and 5.", "danger")
            elif not text:
                flash("Review text cannot be empty.", "danger")
            else:
                db.session.add(Review(
                    course_code=course["code"],
                    user_id=current_user.id,            # ← real user id from Flask-Login
                    rating=rating,
                    text=text,
                ))
                db.session.commit()
                flash("Review submitted.", "success")

        elif form_type == "discussion":
            comment = request.form.get("comment", "").strip()

            if not comment:
                flash("Comment cannot be empty.", "danger")
            else:
                db.session.add(Discussion(
                    course_code=course["code"],
                    user_id=current_user.id,            # ← real user id from Flask-Login
                    text=comment,
                ))
                db.session.commit()

        return redirect(url_for("course_detail", course_code=course["code"]))

    # ── GET ───────────────────────────────────────────────────────────────────
    course_reviews = (
        Review.query
        .filter_by(course_code=course["code"])
        .order_by(Review.created_at.desc())
        .all()
    )
    course_discussions = (
        Discussion.query
        .filter_by(course_code=course["code"])
        .order_by(Discussion.created_at.asc())
        .all()
    )
    avg_rating = (
        round(sum(r.rating for r in course_reviews) / len(course_reviews), 1)
        if course_reviews else None
    )

    return render_template(
        "coursepg.html",
        course=course,
        reviews=course_reviews,
        discussions=course_discussions,
        avg_rating=avg_rating,
        favorite_units=_favorite_units(),
    )


# ── Admin delete routes ───────────────────────────────────────────────────────

@app.route("/admin/review/delete/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    review = Review.query.get_or_404(review_id)
    course_code = review.course_code
    db.session.delete(review)
    db.session.commit()
    flash("Review removed.", "success")
    return redirect(url_for("course_detail", course_code=course_code))


@app.route("/admin/discussion/delete/<int:discussion_id>", methods=["POST"])
@login_required
def delete_discussion(discussion_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    discussion = Discussion.query.get_or_404(discussion_id)
    course_code = discussion.course_code
    db.session.delete(discussion)
    db.session.commit()
    flash("Discussion removed.", "success")
    return redirect(url_for("course_detail", course_code=course_code))