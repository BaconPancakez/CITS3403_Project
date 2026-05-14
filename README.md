# CITS3403_Project UUUA Study Hub 

## Purpose
UUUA is a student-focused web application designed to support UWA students academically through collaborative resource sharing and course transparency.

The platform allows students to:

- Browse UWA courses and unit information
- Upload and share study materials
- Leave course reviews and ratings
- Participate in course-specific discussions and reply threads
- Favourite courses for quick access
- Search for units efficiently
- Access admin moderation tools for managing notes, reviews, and discussions

The application is designed to improve accessibility to study materials, increase peer collaboration, and provide clearer insight into course experiences for future students.


## Group Members
| UWA ID | Name | GitHub Username |
|--------|------|-----------------|
| -- | Name | --- |
| 24217338| Rosie Wang | R89097 |
| -- | Name | --- |
| -- | Name | --- |

### Setup

1. Create a virtual environment
```
python3 -m venv .venv
```

2. Activate the virtual environment
#### macOS / Linux
```
source .venv/bin/activate
```
#### Windows
```
.venv\Scripts\activate
```

3. Install dependencies
```
pip3 install -r requirements.txt
```

4. This project requires the following system packages:
- LibreOffice

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install libreoffice
```
#### macOS
```bash
brew install --cask libreoffice
```
#### Windows
Install LibreOffice manually from:
https://www.libreoffice.org/download/download-libreoffice/


5. Create a `.env` file in the project root
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
then open the following URL in your web browser:
```
http://127.0.0.1:5000
```