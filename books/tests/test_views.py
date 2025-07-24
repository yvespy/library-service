from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book


class BookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = Book.objects.create(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=3.00,
        )

    def test_list_books(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "The Hobbit")

    def test_retrieve_book(self):
        response = self.client.get(f"/api/books/{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author"], "J.R.R. Tolkien")

    def test_create_book(self):
        payload = {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "cover": "SOFT",
            "inventory": 7,
            "daily_fee": "1.80",
        }
        response = self.client.post("/api/books/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.last().title, "Brave New World")
