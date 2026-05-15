# UUUA Study Hub 
For CITS3403 Agile Web Development

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
| 24224716 | Oliver Wright | oliver-31415 |
| 24217338| Rosie Wang | R89097 |
| 25303739  | Qi Ming Seng | BaconPancakez |
| 23433973 | Zacc Benabid | ZacB28 |

## Setup

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

## Run

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

## Run Tests

### Unit tests

The project includes backend unit tests for:
- User authentication
- Password hashing
- Reviews
- Discussions and replies
- Notes preview support
- Notifications
- Database constraints

### Selenium Web tests
The project also includes Selenium browser-based system tests for:
- Landing page loading
- Student login
- Admin login
- Invalid login handling
- Course search
- Course page navigation
- Review submission
- Upload notes modal functionality

Install Chrome and ChromeDriver
###### macOS/Linux
```bash
brew install --cask google-chrome
brew install chromedriver
```
###### Windows
download from approved sources, matching your Chrome version, then extract and add to your system PATH.

Example:
- Extract chromedriver.exe
- Move it to:
    C:\chromedriver\
- Add:
    C:\chromedriver\
to Environment Variables → PATH.



##### Run Unit tests:
```bash
python3 -m unittest tests/unit_tests.py
```

##### Run Selenium tests:
```bash
python3 -m unittest tests/selenium_tests.py
```
