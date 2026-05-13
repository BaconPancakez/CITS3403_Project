from io import BytesIO

from flask import (
    render_template, request, redirect, url_for,
    flash, session, send_file, jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import app, db
from app.models import (
    FEATURED_COURSES, UWA_UNITS, UWA_UNITS_BY_CODE,
    User, Review, Discussion, fileModel,
    BannedUser, CourseQuiz, QuizUpvote, Notification,
    NoteVote, NoteReport, QuizReport,
)

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_login import logout_user

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
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if BannedUser.query.filter_by(email=email).first():
            flash("This account has been banned. Contact support if you believe this is an error.", "danger")
            return redirect(url_for("login"))

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

        role = (
            "admin"
            if email.endswith("@uwa.edu.au") and not email.endswith("@student.uwa.edu.au")
            else "student"
        )
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
    session.pop("favorite_course_codes", None)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# ── Protected routes ──────────────────────────────────────────────────────────

@app.route("/home")
@login_required
def home():
    latest_notes = (
        fileModel.query
        .order_by(fileModel.created_at.desc())
        .limit(5)
        .all()
    )
    notifications = (
        Notification.query
        .filter_by(user_id=current_user.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template(
        "home.html",
        courses=FEATURED_COURSES,
        favorite_units=_favorite_units(),
        latest_notes=latest_notes,
        notifications=notifications[0:5],
    )


@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        flash("Admins only.", "danger")
        return redirect(url_for("home"))

    students     = User.query.filter_by(role="student").order_by(User.name).all()
    banned       = BannedUser.query.order_by(BannedUser.created_at.desc()).all()
    reports      = NoteReport.query.order_by(NoteReport.created_at.desc()).all()
    quiz_reports = QuizReport.query.order_by(QuizReport.created_at.desc()).all()

    return render_template(
        "admin.html",
        courses=FEATURED_COURSES,
        favorite_units=_favorite_units(),
        students=students,
        banned=banned,
        reports=reports,
        quiz_reports=quiz_reports,
    )


@app.route("/admin/ban/<int:user_id>", methods=["POST"])
@login_required
def ban_user(user_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("Admin accounts cannot be banned.", "danger")
        return redirect(url_for("admin", tab="students"))

    reason = request.form.get("reason", "").strip() or None

    if not BannedUser.query.filter_by(email=user.email).first():
        db.session.add(BannedUser(email=user.email, name=user.name, reason=reason))

    # Nullify nullable FK references so history is preserved
    for review in user.reviews.all():
        review.user_id = None
    for discussion in user.discussions.all():
        discussion.user_id = None

    # Remove note votes cast BY this user
    NoteVote.query.filter_by(user_id=user.id).delete()

    # Remove quiz upvotes cast BY this user (adjust counts for quizzes they don't own)
    for upvote in user.quiz_upvotes.all():
        quiz = CourseQuiz.query.get(upvote.quiz_id)
        if quiz and quiz.author_id != user.id:
            quiz.upvote_count = max(0, (quiz.upvote_count or 0) - 1)
        db.session.delete(upvote)

    # Remove notifications for this user (non-nullable user_id)
    Notification.query.filter_by(user_id=user.id).delete()

    # Delete notes (non-nullable author_id) — clean up votes & reports first
    for note in user.notes.all():
        NoteVote.query.filter_by(note_id=note.id).delete()
        NoteReport.query.filter_by(note_id=note.id).delete()
        db.session.delete(note)

    # Delete quizzes (non-nullable author_id) — clean up upvotes & reports first
    for quiz in user.course_quizzes.all():
        QuizReport.query.filter_by(quiz_id=quiz.id).delete()
        QuizUpvote.query.filter_by(quiz_id=quiz.id).delete()
        db.session.delete(quiz)

    display = user.name or user.email
    db.session.delete(user)
    db.session.commit()

    flash(f"'{display}' has been banned and removed.", "success")
    return redirect(url_for("admin", tab="students"))


@app.route("/admin/unban/<int:banned_id>", methods=["POST"])
@login_required
def unban_user(banned_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    entry = BannedUser.query.get_or_404(banned_id)
    display = entry.name or entry.email
    db.session.delete(entry)
    db.session.commit()

    flash(f"'{display}' has been removed from the ban list.", "success")
    return redirect(url_for("admin", tab="students"))


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
                    course_code=course["code"], user_id=current_user.id,
                    rating=rating, text=text,
                ))
                db.session.commit()
                flash("Review submitted.", "success")

        elif form_type == "discussion":
            comment = request.form.get("comment", "").strip()
            if not comment:
                flash("Comment cannot be empty.", "danger")
            else:
                db.session.add(Discussion(
                    course_code=course["code"], user_id=current_user.id,
                    text=comment, parent_id=None,
                ))
                db.session.commit()

        elif form_type == "discussion_reply":
            parent_id = request.form.get("parent_id", type=int)
            comment   = request.form.get("comment", "").strip()
            parent    = Discussion.query.get_or_404(parent_id)
            if not comment:
                flash("Reply cannot be empty.", "danger")
            else:
                reply = Discussion(
                    course_code=course["code"], user_id=current_user.id,
                    text=comment, parent_id=parent.id,
                )
                db.session.add(reply)
                if parent.user_id and parent.user_id != current_user.id:
                    db.session.add(Notification(
                        user_id=parent.user_id,
                        course_code=course["code"],
                        message=(
                            f"{current_user.name or current_user.email} replied to your "
                            f"discussion in {course['code']}"
                        ),
                    ))
                db.session.commit()

        elif form_type == "notes_upload":
            title   = request.form.get("notes_title",   "").strip()
            details = request.form.get("notes_details", "").strip()
            upload  = request.files.get("notes_file")
            if not title:
                flash("Please provide a title for the notes.", "danger")
            elif not upload or not upload.filename:
                flash("Please choose a PDF file to upload.", "danger")
            elif not upload.filename.lower().endswith(".pdf"):
                flash("Only PDF files are supported.", "danger")
            else:
                file_bytes = upload.read()
                if not file_bytes:
                    flash("The uploaded file is empty.", "danger")
                else:
                    db.session.add(fileModel(
                        course_code=course["code"],
                        author_id=current_user.id,
                        title=title,
                        details=details or None,
                        filename=upload.filename,
                        mimetype=upload.mimetype or "application/pdf",
                        file=file_bytes,
                    ))
                    db.session.commit()
                    flash("Notes uploaded.", "success")

        elif form_type == "quiz_create":
            question    = request.form.get("quiz_question", "").strip()
            raw_choices = [request.form.get(f"quiz_choice_{i}", "").strip() for i in range(6)]
            raw_correct = request.form.get("quiz_correct_row")
            try:
                correct_row = int(raw_correct) if raw_correct not in (None, "") else -1
            except ValueError:
                correct_row = -1

            filled_idx = [i for i, t in enumerate(raw_choices) if t]
            if not question:
                flash("Quiz question cannot be empty.", "danger")
            elif len(filled_idx) < 2:
                flash("Add at least two answer options.", "danger")
            elif raw_correct in (None, ""):
                flash("You must select a correct answer.", "danger")
            elif correct_row not in filled_idx:
                flash("Mark the correct answer on a row that has text.", "danger")
            else:
                choices       = [raw_choices[i] for i in filled_idx]
                correct_index = filled_idx.index(correct_row)
                db.session.add(CourseQuiz(
                    course_code=course["code"],
                    author_id=current_user.id,
                    question=question,
                    choices=choices,
                    correct_index=correct_index,
                ))
                db.session.commit()
                flash("Quiz added.", "success")

        return redirect(url_for("course_detail", course_code=course["code"]))

    # ── GET ───────────────────────────────────────────────────────────────────
    sort = request.args.get("sort", "date")

    if sort == "votes":
        vote_sq = (
            db.session.query(
                NoteVote.note_id,
                db.func.coalesce(db.func.sum(NoteVote.value), 0).label("score"),
            )
            .group_by(NoteVote.note_id)
            .subquery()
        )
        course_notes = (
            db.session.query(fileModel)
            .filter(fileModel.course_code == course["code"])
            .outerjoin(vote_sq, fileModel.id == vote_sq.c.note_id)
            .order_by(
                db.func.coalesce(vote_sq.c.score, 0).desc(),
                fileModel.created_at.desc(),
            )
            .all()
        )
    else:
        course_notes = (
            fileModel.query
            .filter_by(course_code=course["code"])
            .order_by(fileModel.created_at.desc())
            .all()
        )

    # Current user's existing votes so the template can highlight active buttons
    user_votes = {}
    if course_notes:
        user_votes = {
            v.note_id: v.value
            for v in NoteVote.query.filter(
                NoteVote.note_id.in_([n.id for n in course_notes]),
                NoteVote.user_id == current_user.id,
            ).all()
        }

    course_reviews = (
        Review.query
        .filter_by(course_code=course["code"])
        .order_by(Review.created_at.desc())
        .all()
    )
    course_discussions = (
        Discussion.query
        .filter_by(course_code=course["code"], parent_id=None)
        .order_by(Discussion.created_at.asc())
        .all()
    )
    avg_rating = (
        round(sum(r.rating for r in course_reviews) / len(course_reviews), 1)
        if course_reviews else None
    )
    course_quizzes = (
        CourseQuiz.query
        .filter_by(course_code=course["code"])
        .order_by(CourseQuiz.upvote_count.desc(), CourseQuiz.created_at.desc())
        .all()
    )
    if course_quizzes:
        quiz_ids = [q.id for q in course_quizzes]
        upvoted_quiz_ids = {
            row.quiz_id
            for row in QuizUpvote.query.filter(
                QuizUpvote.user_id == current_user.id,
                QuizUpvote.quiz_id.in_(quiz_ids),
            ).all()
        }
    else:
        upvoted_quiz_ids = set()

    quiz_total_count = len(course_quizzes)
    quizzes_preview  = course_quizzes[:5]

    return render_template(
        "coursepg.html",
        course=course,
        reviews=course_reviews,
        discussions=course_discussions,
        avg_rating=avg_rating,
        notes=course_notes,
        quizzes_preview=quizzes_preview,
        quiz_total_count=quiz_total_count,
        upvoted_quiz_ids=upvoted_quiz_ids,
        favorite_units=_favorite_units(),
        sort=sort,
        user_votes=user_votes,
    )


# ── Note voting & reporting ───────────────────────────────────────────────────

@app.route("/notes/<int:note_id>/vote", methods=["POST"])
@login_required
def vote_note(note_id):
    note  = fileModel.query.get_or_404(note_id)
    value = request.form.get("value", type=int)

    if value not in (1, -1):
        flash("Invalid vote.", "danger")
        return redirect(url_for("course_detail", course_code=note.course_code))

    existing = NoteVote.query.filter_by(note_id=note_id, user_id=current_user.id).first()
    if existing:
        if existing.value == value:
            db.session.delete(existing)          # toggle off
        else:
            existing.value = value               # flip direction
    else:
        db.session.add(NoteVote(note_id=note_id, user_id=current_user.id, value=value))

    db.session.commit()
    sort = request.form.get("sort", "date")
    return redirect(url_for("course_detail", course_code=note.course_code, sort=sort))


@app.route("/notes/<int:note_id>/report", methods=["POST"])
@login_required
def report_note(note_id):
    note   = fileModel.query.get_or_404(note_id)
    reason = request.form.get("reason", "").strip() or None

    if NoteReport.query.filter_by(note_id=note_id, reporter_id=current_user.id).first():
        flash("You have already reported this note.", "warning")
    else:
        db.session.add(NoteReport(
            note_id=note_id, reporter_id=current_user.id, reason=reason
        ))
        db.session.commit()
        flash("Note reported. An admin will review it.", "info")

    sort = request.form.get("sort", "date")
    return redirect(url_for("course_detail", course_code=note.course_code, sort=sort))


# ── Quiz reporting ────────────────────────────────────────────────────────────

@app.route("/course/<course_code>/quiz/<int:quiz_id>/report", methods=["POST"])
@login_required
def report_quiz(course_code, quiz_id):
    course = UWA_UNITS_BY_CODE.get(course_code.strip().upper())
    if not course:
        flash("Course not found.", "warning")
        return redirect(url_for("course_list"))

    quiz   = CourseQuiz.query.filter_by(id=quiz_id, course_code=course["code"]).first_or_404()
    reason = request.form.get("reason", "").strip() or None

    if QuizReport.query.filter_by(quiz_id=quiz_id, reporter_id=current_user.id).first():
        flash("You have already reported this quiz.", "warning")
    else:
        db.session.add(QuizReport(
            quiz_id=quiz_id, reporter_id=current_user.id, reason=reason
        ))
        db.session.commit()
        flash("Quiz reported. An admin will review it.", "info")

    next_url = request.form.get("_next") or url_for("course_detail", course_code=course["code"])
    return redirect(next_url)


# ── Admin: delete routes ──────────────────────────────────────────────────────

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


@app.route("/admin/note/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    if current_user.role != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("home"))

    note = fileModel.query.get_or_404(note_id)
    course_code = note.course_code

    # Remove dependent rows first to avoid FK issues on SQLite
    NoteVote.query.filter_by(note_id=note.id).delete()
    NoteReport.query.filter_by(note_id=note.id).delete()
    db.session.delete(note)
    db.session.commit()

    flash("Note removed successfully.", "success")
    next_url = request.form.get("_next") or url_for("course_detail", course_code=course_code)
    return redirect(next_url)


@app.route("/admin/quiz/delete/<int:quiz_id>", methods=["POST"])
@login_required
def delete_quiz(quiz_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    quiz = CourseQuiz.query.get_or_404(quiz_id)
    course_code = quiz.course_code

    QuizReport.query.filter_by(quiz_id=quiz.id).delete()
    QuizUpvote.query.filter_by(quiz_id=quiz.id).delete()
    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz removed successfully.", "success")
    next_url = request.form.get("_next") or url_for("course_detail", course_code=course_code)
    return redirect(next_url)


# ── Admin: dismiss report routes ──────────────────────────────────────────────

@app.route("/admin/report/dismiss/<int:report_id>", methods=["POST"])
@login_required
def dismiss_report(report_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    report = NoteReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash("Note report dismissed.", "success")
    return redirect(url_for("admin", tab="reports"))


@app.route("/admin/quiz-report/dismiss/<int:report_id>", methods=["POST"])
@login_required
def dismiss_quiz_report(report_id):
    if current_user.role != "admin":
        flash("Unauthorized.", "danger")
        return redirect(url_for("home"))

    report = QuizReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash("Quiz report dismissed.", "success")
    return redirect(url_for("admin", tab="reports"))


# ── Full-page quiz list ───────────────────────────────────────────────────────

@app.route("/course/<course_code>/quizzes", methods=["GET", "POST"])
@login_required
def course_quizzes(course_code):
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
                    course_code=course["code"], user_id=current_user.id,
                    rating=rating, text=text,
                ))
                db.session.commit()
                flash("Review submitted.", "success")

        elif form_type == "discussion":
            comment = request.form.get("comment", "").strip()
            if not comment:
                flash("Comment cannot be empty.", "danger")
            else:
                db.session.add(Discussion(
                    course_code=course["code"], user_id=current_user.id,
                    text=comment, parent_id=None,
                ))
                db.session.commit()

        elif form_type == "discussion_reply":
            parent_id = request.form.get("parent_id", type=int)
            comment   = request.form.get("comment", "").strip()
            parent    = Discussion.query.get_or_404(parent_id)
            if parent.course_code != course["code"]:
                flash("Invalid discussion thread.", "danger")
            elif not comment:
                flash("Reply cannot be empty.", "danger")
            else:
                reply = Discussion(
                    course_code=course["code"], user_id=current_user.id,
                    text=comment, parent_id=parent.id,
                )
                db.session.add(reply)
                if parent.user_id and parent.user_id != current_user.id:
                    db.session.add(Notification(
                        user_id=parent.user_id,
                        course_code=course["code"],
                        message=(
                            f"{current_user.name or current_user.email} replied to your "
                            f"discussion in {course['code']}"
                        ),
                    ))
                db.session.commit()

        return redirect(url_for("course_quizzes", course_code=course["code"]))

    course_reviews = (
        Review.query.filter_by(course_code=course["code"])
        .order_by(Review.created_at.desc()).all()
    )
    course_discussions = (
        Discussion.query.filter_by(course_code=course["code"], parent_id=None)
        .order_by(Discussion.created_at.asc()).all()
    )
    avg_rating = (
        round(sum(r.rating for r in course_reviews) / len(course_reviews), 1)
        if course_reviews else None
    )
    course_quizzes_all = (
        CourseQuiz.query.filter_by(course_code=course["code"])
        .order_by(CourseQuiz.upvote_count.desc(), CourseQuiz.created_at.desc())
        .all()
    )
    if course_quizzes_all:
        quiz_ids = [q.id for q in course_quizzes_all]
        upvoted_quiz_ids = {
            row.quiz_id
            for row in QuizUpvote.query.filter(
                QuizUpvote.user_id == current_user.id,
                QuizUpvote.quiz_id.in_(quiz_ids),
            ).all()
        }
    else:
        upvoted_quiz_ids = set()

    return render_template(
        "course_quizzes.html",
        course=course,
        reviews=course_reviews,
        discussions=course_discussions,
        avg_rating=avg_rating,
        quizzes=course_quizzes_all,
        upvoted_quiz_ids=upvoted_quiz_ids,
        favorite_units=_favorite_units(),
    )


# ── Quiz AJAX endpoints ───────────────────────────────────────────────────────

@app.route("/course/<course_code>/quiz/<int:quiz_id>/answer", methods=["POST"])
@login_required
def quiz_answer_json(course_code, quiz_id):
    course = UWA_UNITS_BY_CODE.get(course_code.strip().upper())
    if not course:
        return jsonify({"ok": False, "error": "course_not_found"}), 404

    data = request.get_json(silent=True) or {}
    try:
        selected = int(data.get("selected_index", -1))
    except (TypeError, ValueError):
        selected = -1

    quiz = CourseQuiz.query.filter_by(id=quiz_id, course_code=course["code"]).first()
    if not quiz:
        return jsonify({"ok": False, "error": "quiz_not_found"}), 404
    if selected < 0 or selected >= len(quiz.choices):
        return jsonify({"ok": False, "error": "invalid_choice"}), 400

    return jsonify({"ok": True, "correct": selected == quiz.correct_index})


@app.route("/course/<course_code>/quiz/<int:quiz_id>/upvote", methods=["POST"])
@login_required
def quiz_upvote_json(course_code, quiz_id):
    course = UWA_UNITS_BY_CODE.get(course_code.strip().upper())
    if not course:
        return jsonify({"ok": False, "error": "course_not_found"}), 404

    quiz = CourseQuiz.query.filter_by(id=quiz_id, course_code=course["code"]).first()
    if not quiz:
        return jsonify({"ok": False, "error": "quiz_not_found"}), 404

    data = request.get_json(silent=True) or {}
    if data.get("remove"):
        row = QuizUpvote.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
        if row:
            db.session.delete(row)
            quiz.upvote_count = max(0, (quiz.upvote_count or 0) - 1)
            db.session.commit()
        return jsonify({"ok": True, "count": quiz.upvote_count, "upvoted": False})

    if QuizUpvote.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first():
        return jsonify({"ok": True, "count": quiz.upvote_count, "upvoted": True})

    db.session.add(QuizUpvote(user_id=current_user.id, quiz_id=quiz_id))
    quiz.upvote_count = (quiz.upvote_count or 0) + 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        quiz = CourseQuiz.query.get(quiz_id)
        return jsonify({
            "ok": True,
            "count": quiz.upvote_count if quiz else 0,
            "upvoted": True,
        })

    return jsonify({"ok": True, "count": quiz.upvote_count, "upvoted": True})


# ── File serving ──────────────────────────────────────────────────────────────

@app.route("/notes/<int:note_id>/file")
@login_required
def notes_file(note_id):
    note = fileModel.query.get_or_404(note_id)
    download_name = note.filename or f"{note.title or 'notes'}.pdf"
    return send_file(
        BytesIO(note.file),
        mimetype=note.mimetype or "application/pdf",
        download_name=download_name,
        as_attachment=False,
    )


def _reset_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"])

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            token = _reset_serializer().dumps(user.email, salt="password-reset")
            reset_link = url_for("reset_password", token=token, _external=True)
            flash("Password reset link generated.", "success")
        else:
            flash("No account found with that email.", "danger")

    return render_template("forgot_password.html", reset_link=reset_link)

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = _reset_serializer().loads(
            token,
            salt="password-reset",
            max_age=1800
        )
    except SignatureExpired:
        flash("Reset link expired.", "danger")
        return redirect(url_for("forgot_password"))
    except BadSignature:
        flash("Invalid reset link.", "danger")
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password", token=token))

        user.set_password(password)
        db.session.commit()

        logout_user()
        flash("Password updated. Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")
