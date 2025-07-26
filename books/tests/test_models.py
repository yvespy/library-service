from django.test import TestCase
from books.models import Book


class BookModelTest(TestCase):
    def test_str_representation(self):
        book = Book.objects.create(
            title="Test Book",
            author="John Smith",
            cover=Book.CoverType.HARD,
            inventory=3,
            daily_fee=1.50,
        )
        self.assertEqual(str(book), "Test Book by John Smith")
