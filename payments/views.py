import stripe
from rest_framework import viewsets, permissions, status
from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentCreateSerializer
from rest_framework.decorators import api_view
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


@api_view(["GET"])
def stripe_success(request):
    session_id = request.query_params.get("session_id")

    if not session_id:
        return Response(
            {"error": "Missing session_id"}, status=status.HTTP_400_BAD_REQUEST
        )

    session = stripe.checkout.Session.retrieve(session_id)

    try:
        payment = Payment.objects.get(session_id=session_id)
    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if session.payment_status == "paid" and payment.status != Payment.Status.PAID:
        payment.status = Payment.Status.PAID
        payment.save()

    return Response({"message": "Payment was successful!"})


@api_view(["GET"])
def stripe_cancel(request):
    return Response({"message": "Payment was canceled or failed."})
