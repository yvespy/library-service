from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books.views import BookView

router = DefaultRouter()
router.register("books", BookView)

urlpatterns = [
    path("", include(router.urls)),
]
