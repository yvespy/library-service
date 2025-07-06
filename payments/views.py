from decimal import Decimal
import stripe
from rest_framework import viewsets, permissions, status
from payments.models import Payment
from payments.serializers import PaymentSerializer
from rest_framework.decorators import api_view, action
from rest_framework.response import Response


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        payment = self.get_object()

        if payment.status == Payment.Status.PAID:
            return Response(
                {"detail": "This payment is already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment.session_url:
            return Response(
                {
                    "detail": "Payment session already exists.",
                    "url": payment.session_url,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing = payment.borrowing
        amount_in_cents = int(Decimal(payment.money_to_pay) * 100)

        success_url = request.build_absolute_uri(
            f"/payments/success/?session_id={{CHECKOUT_SESSION_ID}}&type={payment.type}"
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
                            "name": f"{borrowing.book.title} ({payment.type} for Borrowing #{borrowing.id})"
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return Response({"url": session.url}, status=status.HTTP_200_OK)


@api_view(["GET"])
def stripe_success(request):
    session_id = request.query_params.get("session_id")
    payment_type = request.query_params.get("type")

    if not session_id:
        return Response(
            {"error": "Missing session_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.InvalidRequestError:
        return Response(
            {"error": "Invalid or expired session_id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        payment = Payment.objects.get(session_id=session_id)
    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if session.payment_status == "paid" and payment.status != Payment.Status.PAID:
        payment.status = Payment.Status.PAID
        payment.save()

    if payment_type == Payment.Type.FINE:
        message = "Fine was successfully paid."
    else:
        message = "Payment was successful."

    return Response({"message": message})


@api_view(["GET"])
def stripe_cancel(request):
    return Response({"message": "Payment was canceled or failed."})
