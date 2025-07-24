from django.test import TestCase
from datetime import date, timedelta

from users.models import User
from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="pass1234"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoverType.SOFT,
            inventory=3,
            daily_fee=1.0,
        )

    def test_str_method(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )
        expected_str = f"{self.user.email} borrowing {self.book.title}"
        self.assertEqual(str(borrowing), expected_str)

    def test_is_active_true(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )
        self.assertTrue(borrowing.is_active())

    def test_is_active_false(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
            actual_return_date=date.today(),
        )
        self.assertFalse(borrowing.is_active())
