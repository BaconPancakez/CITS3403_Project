from datetime import datetime

from app import db


# class TimestampMixin:
# 	created_at = db.Column(db.DateTime...)
# 	updated_at = db.Column(...)


class User(db.Model,):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	name = db.Column(db.String(120), nullable=True)
	role = db.Column(db.String(20), nullable=True)
	

MOCK_COURSES = [
    {
        "code": "CITS3403",
        "title": "Agile Web Development",
        "summary": "bla bla bla.",
    },
    {
        "code": "CITS1402",
        "title": "Relational Database",
        "summary": "bla bla bla.",
    },
    {
        "code": "CITS5508",
        "title": "Machine Learning",
        "summary": "bla bla bla.",
    },
]
