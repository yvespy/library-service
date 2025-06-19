from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    borrowing = models.ForeignKey("borrowings.Borrowing", on_delete=models.CASCADE, related_name="payments")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    type = models.CharField(max_length=10, choices=Type.choices)
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=7)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.borrowing} - {self.type} - {self.status}"
