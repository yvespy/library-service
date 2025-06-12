from django.utils import timezone

from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "book_title",
            "user",
            "user_full_name",
        ]

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "book")

    def validate_book(self, book):
        if book.inventory < 1:
            raise serializers.ValidationError("This book is not available.")
        return book

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(
            user=self.context["request"].user, **validated_data
        )
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",)

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("This borrowing is already returned.")
        return attrs

    def save(self, **kwargs):
        self.instance.actual_return_date = timezone.now().date()
        self.instance.save()

        book = self.instance.book
        book.inventory += 1
        book.save()
        return self.instance
