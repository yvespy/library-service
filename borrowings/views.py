from rest_framework import viewsets, status
from rest_framework.response import Response
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)
from payments.models import Payment
from payments.serializers import PaymentCreateSerializer
from rest_framework.decorators import action


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user").all()

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingCreateSerializer

    def get_queryset(self):
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if is_active is not None:
            queryset = queryset.filter(
                actual_return_date__isnull=is_active.lower() == "true"
            )
        return queryset

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)

        payment_serializer = PaymentCreateSerializer(
            data={
                "borrowing": borrowing.id,
                "type": Payment.Type.PAYMENT,
            },
            context={"request": self.request},
        )
        payment_serializer.is_valid(raise_exception=True)
        payment_serializer.save()

    @action(detail=True, methods=["post"])
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "Book returned"}, status=status.HTTP_200_OK)
