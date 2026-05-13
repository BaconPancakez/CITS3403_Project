import json
from datetime import datetime
from pathlib import Path
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# ── Mixin ─────────────────────────────────────────────────────────────────────

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ── Core models ───────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False)
    name          = db.Column(db.String(120), nullable=True)
    role          = db.Column(db.String(20),  nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Review(TimestampMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False, index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    rating      = db.Column(db.Integer, nullable=False)
    text        = db.Column(db.Text,    nullable=False)

    user = db.relationship("User", backref=db.backref("reviews", lazy="dynamic"))

    @property
    def display_name(self):
        return self.user.name if self.user else "Anonymous"


class Discussion(TimestampMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False, index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    text        = db.Column(db.Text, nullable=False)
    parent_id   = db.Column(db.Integer, db.ForeignKey("discussion.id"), nullable=True)

    user    = db.relationship("User", backref=db.backref("discussions", lazy="dynamic"))
    replies = db.relationship(
        "Discussion",
        backref=db.backref("parent", remote_side=[id]),
        lazy="select",
    )

    @property
    def display_name(self):
        return self.user.name if self.user else "Anonymous"


class BannedUser(TimestampMixin, db.Model):
    __tablename__ = "banned_user"
    id     = db.Column(db.Integer, primary_key=True)
    email  = db.Column(db.String(255), unique=True, nullable=False)
    name   = db.Column(db.String(120), nullable=True)
    reason = db.Column(db.Text,        nullable=True)


# ── Notes / file models ───────────────────────────────────────────────────────

class fileModel(TimestampMixin, db.Model):
    __tablename__ = "file_model"
    id          = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20),  nullable=False, index=True)
    author_id   = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title       = db.Column(db.String(255), nullable=False)
    details     = db.Column(db.Text,        nullable=True)
    filename    = db.Column(db.String(255), nullable=True)
    mimetype    = db.Column(db.String(100), nullable=True)
    file        = db.Column(db.BLOB,        nullable=False)

    author = db.relationship("User", backref=db.backref("notes", lazy="dynamic"))

    @property
    def display_name(self):
        return self.author.name if self.author else "Anonymous"

    # ── Vote helpers (backed by NoteVote.votes backref) ───────────────────────
    @property
    def upvotes(self):
        return self.votes.filter_by(value=1).count()

    @property
    def downvotes(self):
        return self.votes.filter_by(value=-1).count()

    @property
    def vote_score(self):
        return self.upvotes - self.downvotes


class NoteVote(db.Model):
    __tablename__ = "note_vote"
    id      = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(
        db.Integer, db.ForeignKey("file_model.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    value   = db.Column(db.SmallInteger, nullable=False)          # +1 or -1

    __table_args__ = (
        db.UniqueConstraint("note_id", "user_id", name="uq_note_vote"),
    )

    note = db.relationship("fileModel", backref=db.backref("votes",      lazy="dynamic"))
    user = db.relationship("User",      backref=db.backref("note_votes", lazy="dynamic"))


class NoteReport(TimestampMixin, db.Model):
    __tablename__ = "note_report"
    id          = db.Column(db.Integer, primary_key=True)
    note_id     = db.Column(
        db.Integer, db.ForeignKey("file_model.id", ondelete="CASCADE"), nullable=False
    )
    reporter_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    reason = db.Column(db.Text, nullable=True)

    note     = db.relationship("fileModel", backref=db.backref("reports",       lazy="dynamic"))
    reporter = db.relationship("User",      backref=db.backref("reports_filed", lazy="dynamic"))


# ── Quiz models ───────────────────────────────────────────────────────────────

class CourseQuiz(TimestampMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    course_code   = db.Column(db.String(20), nullable=False, index=True)
    author_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    question      = db.Column(db.Text,    nullable=False)
    choices       = db.Column(db.JSON,    nullable=False)
    correct_index = db.Column(db.Integer, nullable=False)
    upvote_count  = db.Column(db.Integer, nullable=False, default=0)

    author = db.relationship("User", backref=db.backref("course_quizzes", lazy="dynamic"))

    @property
    def display_name(self):
        return self.author.name if self.author else "Anonymous"


class QuizUpvote(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("course_quiz.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "quiz_id", name="uq_quiz_upvote_user_quiz"),
    )

    user = db.relationship("User",      backref=db.backref("quiz_upvotes", lazy="dynamic"))
    quiz = db.relationship("CourseQuiz", backref=db.backref("upvote_rows", lazy="dynamic"))


class QuizReport(TimestampMixin, db.Model):
    __tablename__ = "quiz_report"
    id          = db.Column(db.Integer, primary_key=True)
    quiz_id     = db.Column(
        db.Integer, db.ForeignKey("course_quiz.id", ondelete="CASCADE"), nullable=False
    )
    reporter_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    reason = db.Column(db.Text, nullable=True)

    quiz     = db.relationship("CourseQuiz", backref=db.backref("quiz_reports", lazy="dynamic"))
    reporter = db.relationship("User",       backref=db.backref("quiz_reports_filed", lazy="dynamic"))


# ── Notification ──────────────────────────────────────────────────────────────

class Notification(TimestampMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    course_code = db.Column(db.String(20),  nullable=False)
    message     = db.Column(db.String(300), nullable=False)
    is_read     = db.Column(db.Boolean, default=False, nullable=False)
    user        = db.relationship("User", backref=db.backref("notifications", lazy="dynamic"))


# ── Course catalogue ──────────────────────────────────────────────────────────

FEATURED_COURSES = [
    {
        "code":    "CITS3403",
        "title":   "Agile Web Development",
        "summary": "Project-based web development, APIs, and teamwork.",
    },
    {
        "code":    "CITS1402",
        "title":   "Relational Database Management Systems",
        "summary": "SQL, modelling, and database design fundamentals.",
    },
    {
        "code":    "CITS5508",
        "title":   "Machine Learning",
        "summary": "Algorithms and practice for prediction and pattern discovery.",
    },
]

_UNITS_PATH = Path(__file__).resolve().parent / "data" / "uwa_units_detailed.json"


def _load_uwa_units():
    if not _UNITS_PATH.is_file():
        return []
    try:
        with _UNITS_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    out = []
    for row in data:
        if isinstance(row, dict) and row.get("code") and row.get("title"):
            raw_desc = (
                row.get("summary")
                or row.get("description")
                or row.get("Description")
                or ""
            )
            summary_text = str(raw_desc).strip()
            if summary_text.lower() == "nan":
                summary_text = ""
            out.append(
                {
                    "code":               str(row["code"]).strip(),
                    "title":              str(row["title"]).strip(),
                    "summary":            summary_text or "UWA Handbook unit — open for overview and offerings.",
                    "credit_points":      row.get("credit_points", 0),
                    "level_of_study":     str(row.get("level_of_study")     or "").strip(),
                    "url":                str(row.get("url")                 or "").strip(),
                    "school":             str(row.get("school")              or "").strip(),
                    "availability":       str(row.get("availability")        or "").strip(),
                    "location":           str(row.get("location")            or "").strip(),
                    "coordinators":       str(row.get("coordinators")        or "").strip(),
                    "field_of_education": str(row.get("field_of_education")  or "").strip(),
                }
            )
    return sorted(out, key=lambda r: r["code"])


UWA_UNITS = _load_uwa_units()
if not UWA_UNITS:
    UWA_UNITS = sorted([dict(row) for row in FEATURED_COURSES], key=lambda r: r["code"])

UWA_UNITS_BY_CODE = {u["code"].upper(): u for u in UWA_UNITS}