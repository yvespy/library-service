from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

from books.models import Book
from books.serializers import BookSerializer, BookListSerializer, BookDetailSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all books",
        description="Returns a list of all books (id, title, author).",
        responses={200: BookListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Retrieve a single book",
        description="Get detailed info about a specific book.",
        responses={200: BookDetailSerializer}
    ),
    create=extend_schema(
        summary="Create a new book",
        description="Create a book by providing title, author, cover, inventory, and daily fee.",
        request=BookSerializer,
        responses={201: BookSerializer}
    ),
    update=extend_schema(
        summary="Update a book",
        description="Fully update a book by ID.",
        request=BookSerializer,
        responses={200: BookSerializer}
    ),
    partial_update=extend_schema(
        summary="Partially update a book",
        description="Partially update a book by ID.",
        request=BookSerializer,
        responses={200: BookSerializer}
    ),
    destroy=extend_schema(
        summary="Delete a book",
        description="Delete a book by ID.",
        responses={204: None}
    )
)
class BookView(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        elif self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer
