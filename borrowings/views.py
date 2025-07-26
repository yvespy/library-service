from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)
from payments.models import Payment
from payments.serializers import PaymentCreateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List borrowings",
        description="Returns a list of borrowings. Supports filtering by `user_id` and `is_active`.",
        parameters=[
            OpenApiParameter(name="user_id", description="Filter by user ID", required=False, type=int),
            OpenApiParameter(name="is_active", description="Filter by active status (`true` or `false`)", required=False, type=bool),
        ],
        responses={200: BorrowingListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Retrieve borrowing",
        description="Get detailed information about a specific borrowing.",
        responses={200: BorrowingDetailSerializer}
    ),
    create=extend_schema(
        summary="Create borrowing",
        description="Creates a borrowing and automatically generates a related payment.",
        request=BorrowingCreateSerializer,
        responses={201: BorrowingCreateSerializer}
    ),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(
        summary="Delete borrowing",
        description="Deletes the borrowing entry.",
        responses={204: None}
    ),
)
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

    @extend_schema(
        summary="Return a book",
        description="Marks a borrowing as returned. If overdue, generates a fine payment.",
        responses={200: None},
    )
    @action(detail=True, methods=["post"])
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "Book returned"}, status=status.HTTP_200_OK)
