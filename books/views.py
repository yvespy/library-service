from rest_framework import viewsets

from books.models import Book
from books.serializers import BookSerializer, BookListSerializer, BookDetailSerializer


class BookView(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        elif self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer
