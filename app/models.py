import json
from pathlib import Path

from app import db


# class TimestampMixin:
# 	created_at = db.Column(db.DateTime...)
# 	updated_at = db.Column(...)


class User(db.Model,):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	name = db.Column(db.String(120), nullable=True)
	role = db.Column(db.String(20), nullable=True)


# Compact set for dashboard cards (full catalogue is on /course).
FEATURED_COURSES = [
	{
		"code": "CITS3403",
		"title": "Agile Web Development",
		"summary": "Project-based web development, APIs, and teamwork.",
	},
	{
		"code": "CITS1402",
		"title": "Relational Database Management Systems",
		"summary": "SQL, modelling, and database design fundamentals.",
	},
	{
		"code": "CITS5508",
		"title": "Machine Learning",
		"summary": "Algorithms and practice for prediction and pattern discovery.",
	},
]

_UNITS_PATH = Path(__file__).resolve().parent / "data" / "uwa_units.json"


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
			out.append(
				{
					"code": str(row["code"]).strip(),
					"title": str(row["title"]).strip(),
					"summary": str(row.get("summary") or "").strip()
					or "UWA Handbook unit — open for overview and offerings.",
				}
			)
	return sorted(out, key=lambda r: r["code"])


UWA_UNITS = _load_uwa_units()
if not UWA_UNITS:
	UWA_UNITS = sorted([dict(row) for row in FEATURED_COURSES], key=lambda r: r["code"])

UWA_UNITS_BY_CODE = {u["code"].upper(): u for u in UWA_UNITS}
