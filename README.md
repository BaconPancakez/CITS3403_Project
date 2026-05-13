# CITS3403_Project




### Setup

1. Create a virtual environment
```
python3 -m venv .venv
```

2. Activate the virtual environment
```
source .venv/bin/activate
```

3. Install dependencies
```
pip3 install -r requirements.txt
```

4. Create a `.env` file in the project root
```
MYAPP_SECRET_KEY=change-me

# Optional: override the default SQLite database
# MYAPP_DATABASE_URL=sqlite:////absolute/path/to/uuua.db
```

### Run

```
flask run
```

Optional: run database migrations if needed
```
flask db upgrade
```