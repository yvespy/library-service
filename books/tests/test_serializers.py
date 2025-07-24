from django.test import TestCase
from books.models import Book
from books.serializers import BookSerializer, BookListSerializer, BookDetailSerializer


class BookSerializerTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="1984",
            author="George Orwell",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=2.50,
        )

    def test_book_serializer_fields(self):
        serializer = BookSerializer(instance=self.book)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "author", "cover", "inventory", "daily_fee"},
        )

    def test_book_list_serializer_fields(self):
        serializer = BookListSerializer(instance=self.book)
        data = serializer.data
        self.assertEqual(set(data.keys()), {"id", "title", "author"})

    def test_book_detail_serializer_fields(self):
        serializer = BookDetailSerializer(instance=self.book)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {"id", "title", "author", "cover", "inventory", "daily_fee"},
        )
