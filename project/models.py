from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

class Payment(models.Model):
    """
    Payment model.

    Fields:
        - `id` (integer): unique payment id.
        - `user` (string): user who makes the payment.
        - `amount` (number): payment amount (two decimal places).
        - `timestamp` (string, datetime): payment time (ISO format).

    Example:
    ```json
    {
        "id": 1,
        "user": "Homer Simpson",
        "amount": 500.00,
        "timestamp": "2025-04-05T10:30:00Z"
    }
    ```
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
        )
    collect = models.ForeignKey(
        'Collect',
        on_delete=models.CASCADE,
        related_name='payments'
        )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of the user: {self.user.username} - {self.amount}"


class Collect(models.Model):
    """
    """
    PURPOSE_CHOICES = [
        ('birth', 'Birthday'),
        ('wedding', 'Wedding'),
        ('charity', 'Charity'),
        ('other', 'Other'),
    ]
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collections',
    )
    title = models.CharField(max_length=200)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
        )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
        )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
        )