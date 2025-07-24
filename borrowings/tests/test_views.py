from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta, date

from users.models import User
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class BorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="pass1234"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoverType.HARD,
            inventory=2,
            daily_fee=1.5,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_borrowing(self):
        url = reverse("borrowing-list")
        data = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=5)).isoformat(),
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

        borrowing = Borrowing.objects.last()
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(Payment.objects.count(), 1)

    def test_list_borrowings(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )
        url = reverse("borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_return_borrowing_no_fine(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=2),
        )
        url = reverse("borrowing-return-borrowing", args=[borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 3)

    def test_return_borrowing_with_fine(self):
        overdue_date = date.today() - timedelta(days=2)
        borrowing = Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date=overdue_date
        )

        url = reverse("borrowing-return-borrowing", args=[borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fines = Payment.objects.filter(borrowing=borrowing, type=Payment.Type.FINE)
        self.assertEqual(fines.count(), 1)

        fine = fines.first()
        self.assertEqual(fine.status, Payment.Status.PENDING)
        self.assertGreater(fine.money_to_pay, 0)
