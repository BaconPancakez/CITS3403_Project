import json
from pathlib import Path

from app import db

class User(db.Model,):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	name = db.Column(db.String(120), nullable=True)
	role = db.Column(db.String(20), nullable=True)

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
			# Catch variations in JSON keys
			raw_desc = row.get("summary") or row.get("description") or row.get("Description") or ""
			summary_text = str(raw_desc).strip()
			
			# Filter out pandas 'nan' string artifacts
			if summary_text.lower() == "nan":
				summary_text = ""

			out.append(
				{
					"code": str(row["code"]).strip(),
					"title": str(row["title"]).strip(),
					"summary": summary_text or "UWA Handbook unit — open for overview and offerings.",
					"credit_points": row.get("credit_points", 0),
					"level_of_study": str(row.get("level_of_study") or "").strip(),
					"url": str(row.get("url") or "").strip(),
					"school": str(row.get("school") or "").strip(),
					"availability": str(row.get("availability") or "").strip(),
					"location": str(row.get("location") or "").strip(),
					"coordinators": str(row.get("coordinators") or "").strip(),
					"field_of_education": str(row.get("field_of_education") or "").strip()
				}
			)
	return sorted(out, key=lambda r: r["code"])

UWA_UNITS = _load_uwa_units()
if not UWA_UNITS:
	UWA_UNITS = sorted([dict(row) for row in FEATURED_COURSES], key=lambda r: r["code"])

UWA_UNITS_BY_CODE = {u["code"].upper(): u for u in UWA_UNITS}