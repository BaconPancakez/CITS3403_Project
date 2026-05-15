
import os, tempfile, threading, time, unittest, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

os.environ.setdefault("MYAPP_SECRET_KEY", "test-secret-key")

from app import app, db
from app.models import User

BASE_URL = "http://127.0.0.1:5001"

class SeleniumTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        )
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Create a test user
            student = User.query.filter_by(email="student_selenium_test@student.uwa.edu.au").first()
            if not student:
                student = User(
                    email="student_selenium_test@student.uwa.edu.au",
                    name="Student Selenium Test",
                    role="student"
                )
                student.set_password("testpassword")
                db.session.add(student)

            admin = User.query.filter_by(email="admin@uwa.edu.au").first()
            if not admin:
                admin = User(
                    email="admin@uwa.edu.au",
                    name="Admin Selenium Test",
                    role="admin"
                )
                admin.set_password("testpassword")
                db.session.add(admin)

            db.session.commit()
        
        cls.server_thread = threading.Thread(
            target=lambda: app.run(port=5001, use_reloader=False),
            daemon=True,
        )
        cls.server_thread.start()
        time.sleep(1)  # Wait for the server to start

    def setUp(self):
        option=Options()
        option.add_argument("--headless=new")
        option.add_argument("--window-size=1400,1000")

        self.driver = webdriver.Chrome(options=option)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()
    
    def test_student_login_flow(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.NAME, "email").send_keys("student_selenium_test@student.uwa.edu.au")
        self.driver.find_element(By.NAME, "password").send_keys("testpassword")

        submit = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit.click()
        self.wait.until(EC.url_contains("/home"))
    
    def test_admin_login_flow(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.NAME, "email").send_keys("admin@uwa.edu.au")
        self.driver.find_element(By.NAME, "password").send_keys("testpassword")

        submit = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit.click()
        self.wait.until(EC.url_contains("/admin"))
        self.assertIn("Admin", self.driver.page_source)

    def test_landing_page_loads(self):
        self.driver.get(BASE_URL)
        self.assertIn("Welcome to UUUA", self.driver.page_source)
        self.assertIn("Get Started", self.driver.page_source)
        self.assertIn("Sign In", self.driver.page_source)

    def test_invalid_login_shows_error(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.NAME, "email").send_keys("fake@student.uwa.edu.au")
        self.driver.find_element(By.NAME, "password").send_keys("wrong")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.assertIn("Invalid", self.driver.page_source)

    def test_student_login_redirects_home(self):
        self.login_as_student()
        self.assertIn("/home", self.driver.current_url)
        self.assertIn("Welcome", self.driver.page_source)

    def test_course_search_shows_course(self):
        self.login_as_student()
        self.driver.get(f"{BASE_URL}/course")

        search = self.wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search.clear()
        search.send_keys("CITS3403")
        search.send_keys("\n")
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                "CITS3403"
            )
        )
        self.assertIn("CITS3403", self.driver.page_source)

    def test_can_open_course_page(self):
        self.login_as_student()
        self.driver.get(f"{BASE_URL}/course/CITS3403")

        self.assertIn("CITS3403", self.driver.page_source)
        self.assertIn("Reviews", self.driver.page_source)

    def test_can_submit_review(self):
        self.login_as_student()
        self.driver.get(f"{BASE_URL}/course/CITS3403")
        review_text = "Great course from Selenium test."
        rating = self.wait.until(
            EC.presence_of_element_located((By.NAME, "rating"))
        )
        Select(rating).select_by_value("5")

        review_box = self.wait.until(
            EC.presence_of_element_located((By.NAME, "review_text"))
        )
        review_box.clear()
        review_box.send_keys(review_text)

        form = review_box.find_element(By.XPATH, "./ancestor::form")
        self.driver.execute_script("arguments[0].submit();", form)

        self.wait.until(EC.url_contains("/course/CITS3403"))

        self.assertTrue(
            review_text in self.driver.page_source
            or "Average Rating" in self.driver.page_source
            or "5/5" in self.driver.page_source
        )

    def test_upload_notes_modal_opens(self):
        self.login_as_student()
        self.driver.get(f"{BASE_URL}/course/CITS3403")

        upload_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#uploadNotesModal']"))
        )
        upload_button.click()

        title_input = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#uploadNotesModal input[name='notes_title']"))
        )

        self.assertTrue(title_input.is_displayed())
        self.assertIn("Upload Notes", self.driver.page_source)
    
    def login_as_student(self):
        self.driver.get(f"{BASE_URL}/login")

        email = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email.clear()
        email.send_keys("student_selenium_test@student.uwa.edu.au")

        password = self.driver.find_element(By.NAME, "password")
        password.clear()
        password.send_keys("testpassword")

        submit = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit.click()

        self.wait.until(EC.url_contains("/home"))
        self.assertIn("Welcome", self.driver.page_source)


if __name__ == "__main__":
    unittest.main()

