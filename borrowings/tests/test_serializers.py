from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingCreateSerializer, BorrowingReturnSerializer
from payments.models import Payment


class BorrowingSerializerTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=1.00,
        )

    def test_create_serializer_valid_data(self):
        expected_return_date = date.today() + timedelta(days=7)
        data = {"book": self.book.id, "expected_return_date": expected_return_date}

        serializer = BorrowingCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        borrowing = serializer.save(user=self.user)

        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.expected_return_date, expected_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)  # inventory reduced

    def test_return_serializer_sets_actual_return_date_and_fine(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() - timedelta(days=3),  # overdue
        )

        serializer = BorrowingReturnSerializer(instance=borrowing, data={})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        returned_borrowing = serializer.save()

        self.assertIsNotNone(returned_borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)  # inventory restored

        fine_payment = Payment.objects.filter(
            borrowing=borrowing, type=Payment.Type.FINE
        ).first()

        self.assertIsNotNone(fine_payment)
        self.assertEqual(fine_payment.status, Payment.Status.PENDING)
        self.assertEqual(fine_payment.money_to_pay, self.book.daily_fee * 3 * 2)
