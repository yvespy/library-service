import stripe
from django.conf import settings
from rest_framework import serializers
from payments.models import Payment
from borrowings.models import Borrowing
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentSerializer(serializers.ModelSerializer):
    borrowing_id = serializers.IntegerField(source="borrowing.id", read_only=True)
    book_title = serializers.CharField(source="borrowing.book.title", read_only=True)
    user_email = serializers.EmailField(source="borrowing.user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "borrowing_id",
            "book_title",
            "user_email",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.ModelSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(queryset=Borrowing.objects.all())

    class Meta:
        model = Payment
        fields = ("borrowing", "type")

    def create(self, validated_data):
        borrowing = validated_data["borrowing"]
        payment_type = validated_data["type"]

        amount = borrowing.book.daily_fee * Decimal(
            (borrowing.expected_return_date - borrowing.borrow_date).days
        )
        amount_in_cents = int(amount * 100)

        request = self.context.get("request")

        success_url = (
            request.build_absolute_uri("/payments/success/")
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = request.build_absolute_uri("/payments/cancel/")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount_in_cents,
                        "product_data": {
                            "name": f"{borrowing.book.title} (Borrowing #{borrowing.id})"
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        payment = Payment.objects.create(
            borrowing=borrowing,
            status=Payment.Status.PENDING,
            type=payment_type,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=amount,
        )

        return payment
