from django.test import TestCase
from decimal import Decimal
from payments.models import Payment
from payments.serializers import PaymentSerializer
from books.models import Book
from users.models import User
from borrowings.models import Borrowing
from datetime import timedelta
from django.utils import timezone


class PaymentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@mail.com", password="testpass")
        self.book = Book.objects.create(
            title="1984",
            author="George Orwell",
            cover=Book.CoverType.SOFT,
            inventory=2,
            daily_fee=Decimal("1.00"),
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=3),
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status=Payment.Status.PAID,
            type=Payment.Type.PAYMENT,
            session_url="https://url.com",
            session_id="abc123",
            money_to_pay=Decimal("3.00"),
        )

    def test_payment_serializer_fields(self):
        serializer = PaymentSerializer(instance=self.payment)
        data = serializer.data

        self.assertEqual(data["status"], Payment.Status.PAID)
        self.assertEqual(data["type"], Payment.Type.PAYMENT)
        self.assertEqual(data["money_to_pay"], "3.00")
        self.assertEqual(data["borrowing_id"], self.borrowing.id)
        self.assertEqual(data["book_title"], self.book.title)
        self.assertEqual(data["user_email"], self.user.email)
