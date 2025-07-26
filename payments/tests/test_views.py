from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from books.models import Book
from users.models import User
from borrowings.models import Borrowing
from payments.models import Payment
from datetime import timedelta
from django.utils import timezone


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@mail.com", password="pass1234")
        self.book = Book.objects.create(
            title="Book Title",
            author="Author",
            cover=Book.CoverType.SOFT,
            inventory=1,
            daily_fee=Decimal("2.00"),
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=2),
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
            session_url="https://url.com",
            session_id="session123",
            money_to_pay=Decimal("4.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_list_user_payments(self):
        response = self.client.get("/payments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_payment(self):
        response = self.client.get(f"/payments/{self.payment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.payment.id)
