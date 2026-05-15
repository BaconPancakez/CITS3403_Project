# To run just use python (or python3) tests.py
import os
import unittest

os.environ["MYAPP_DATABASE_URL"] = "sqlite://"
os.environ["MYAPP_SECRET_KEY"] = "test-secret"

from sqlalchemy.exc import IntegrityError
from app.models import User, Review, Discussion, BannedUser, fileModel, NoteVote, NoteReport, CourseQuiz, QuizReport, QuizUpvote, Notification

from app import app, db

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

class UserModelCase(BaseTestCase):
    def test_password_hashing(self):
        u1 = User(email='u1@student.uwa.edu.au', name='u1')
        u1.set_password('Abc12345')
        self.assertFalse(u1.check_password('Abc54321'))
        self.assertTrue(u1.check_password('Abc12345'))

class ReviewModelCase(BaseTestCase):
    def test_unique_review_per_user_course(self):
        u = User(email="a@b.com", name="A")
        db.session.add(u)
        db.session.commit()

        r1 = Review(user_id=u.id, course_code="CITS3403", rating=5, text="Good")
        r2 = Review(user_id=u.id, course_code="CITS3403", rating=4, text="Ok")
        db.session.add_all([r1, r2])
        with self.assertRaises(IntegrityError):
            db.session.commit()

    
class AuthRoutesCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = app.test_client()

    def test_login_invalid_password(self):
        u = User(name="U", email="u@student.uwa.edu.au", role="student")
        u.set_password("secret123")
        db.session.add(u)
        db.session.commit()

        resp = self.client.post("/login", data={
            "email": "u@x.com",
            "password": "wrong",
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers["Location"])

    def test_login_banned_user(self):
        u = User(name="U", email="u@student.uwa.edu.au", role="student")
        u.set_password("secret123")
        banned = BannedUser(email="u@student.uwa.edu.au", name="U", reason="test")
        db.session.add_all([u, banned])
        db.session.commit()

        resp = self.client.post("/login", data={
            "email": "u@x.com",
            "password": "secret123",
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers["Location"])

    def test_signup_short_password(self):
        resp = self.client.post("/signup", data={
            "name": "testJeff",
            "email": "testJeff@student.uwa.edu.au",
            "password": "short",
            "confirm_password": "short",
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn("/signup", resp.headers["Location"])


class NotePreviewCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = User(email="u@student.uwa.edu.au", name="U")
        db.session.add(self.user)
        db.session.commit()

    def test_has_preview_pdf_filename(self):
        note = fileModel(
            course_code="CITS3403",
            author_id=self.user.id,
            title="PDF",
            filename="note.pdf",
            file=b"data",
        )
        self.assertTrue(note.has_preview)

    def test_has_preview_txt_filename(self):
        note = fileModel(
            course_code="CITS3403",
            author_id=self.user.id,
            title="TXT",
            filename="note.txt",
            file=b"data",
        )
        self.assertTrue(note.has_preview)

    def test_has_preview_with_pdf_cache(self):
        note = fileModel(
            course_code="CITS3403",
            author_id=self.user.id,
            title="DOCX",
            filename="note.docx",
            file=b"data",
            pdf_cache=b"%PDF-1.4 ...",
        )
        self.assertTrue(note.has_preview)

    def test_no_preview_without_pdf_cache(self):
        note = fileModel(
            course_code="CITS3403",
            author_id=self.user.id,
            title="DOCX",
            filename="note.docx",
            file=b"data",
            pdf_cache=None,
        )
        self.assertFalse(note.has_preview)

class DiscussionModelCase(BaseTestCase):
    def test_display_name_anonymous(self):
        d = Discussion(course_code="CITS3403", text="hi", user_id=None)
        self.assertEqual(d.display_name, "Anonymous")

    def test_display_name_with_user(self):
        u = User(email="u@student.uwa.edu.au", name="User")
        db.session.add(u)
        db.session.commit()

        d = Discussion(course_code="CITS3403", text="hi", user=u)
        db.session.add(d)
        db.session.flush()
        self.assertEqual(d.display_name, "User")

    def test_parent_child_relationship(self):
        u = User(email="u@student.uwa.edu.au", name="User")
        db.session.add(u)
        db.session.commit()

        parent = Discussion(course_code="CITS3403", text="parent", user_id=u.id)
        db.session.add(parent)
        db.session.commit()

        child = Discussion(course_code="CITS3403", text="reply", user_id=u.id, parent_id=parent.id)
        db.session.add(child)
        db.session.commit()

        self.assertEqual(child.parent.id, parent.id)
        self.assertEqual(parent.replies[0].id, child.id)

if __name__ == '__main__':
    unittest.main(verbosity=2)