# payments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, stripe_success, stripe_cancel

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payments")

urlpatterns = [
    path("success/", stripe_success, name="stripe-success"),
    path("cancel/", stripe_cancel, name="stripe-cancel"),
    path("", include(router.urls)),
]
