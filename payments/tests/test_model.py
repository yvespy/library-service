from django.test import TestCase
from decimal import Decimal
from payments.models import Payment
from books.models import Book
from users.models import User
from borrowings.models import Borrowing
from datetime import timedelta
from django.utils import timezone


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@mail.com", password="testpass")
        self.book = Book.objects.create(
            title="1984",
            author="George Orwell",
            cover=Book.CoverType.HARD,
            inventory=3,
            daily_fee=Decimal("1.50"),
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=5),
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
            session_url="https://fake-url.com",
            session_id="fake-session-id",
            money_to_pay=Decimal("7.50"),
        )

        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(str(payment), f"{self.borrowing} - PAYMENT - PENDING")
