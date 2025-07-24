from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book
from users.models import User
from borrowings.models import Borrowing
from payments.models import Payment
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone


class StripeIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@mail.com", password="pass1234")
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Book",
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
            type=Payment.Type.FINE,
            session_url="",
            session_id="",
            money_to_pay=Decimal("4.00"),
        )

    @patch("stripe.checkout.Session.create")
    def test_pay_action_creates_stripe_session(self, mock_stripe_create):
        mock_session = MagicMock()
        mock_session.id = "test_session_id"
        mock_session.url = "https://stripe.test/session"

        mock_stripe_create.return_value = mock_session

        url = f"/payments/{self.payment.id}/pay/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["url"], mock_session.url)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.session_id, "test_session_id")
        self.assertEqual(self.payment.session_url, "https://stripe.test/session")
