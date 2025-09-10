from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

class Payment(models.Model):
    """
    Payment model: allows create single payments objs.

    Fields:
        - `id` (integer): unique payment id.
        - `user` (string): user who makes the payment.
        - `collect` (string): payment purpose.
        - `amount` (number): payment amount (two decimal places).
        - `timestamp` (string, datetime): payment time (ISO format).

    Example:
    ```json
    {
        "id": 1,
        "user": "Homer Simpson",
        "amount": 500.00,
        "collect": "Wedding",
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
    Collect model.

    Fields:
        - `id` (integer): unique collect id.
        - `author` (string): user who start the collect.
        - `title` (string): short name of the collect.
        - `purpose` (string): collection purpose (one from the PURPOSE_CHOICES).
        - `description` (string): collect description.
        - `target_amount` (number): target amount.
        - `current_amount` (number): collected amount.
        - `participants` (number): unique participants.
        - `created_at` (string, datetime): collect start.
        - `ended_at` (string, datetime): collect end.
        - `image` (image): collect image.

    Example:
        ```json
            {
            "id": 12345,
            "author": "homer_simpson",
            "title": "Lisa's wedding",
            "purpose": "Wedding",
            "description": "Collect on Lisa's wedding",
            "target_amount": 50000.0,
            "current_amount": 32750.0,
            "participants": 148,
            "created_at": "2023-10-01T09:30:00Z",
            "ended_at": "2023-12-31T23:59:59Z",
            "image": "/media/collects/lisas_wedding.jpg"
            }
        ```
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
    participants = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(
        upload_to='collections/',
        null=True,
        blank=True
        )
    class Meta:
        ordering = ['-created_at', 'ended_at', 'target_amount']
    
    def __str__(self):
        return f"Collect: {self.title} by {self.author} for {self.target_amount}"
    
    def add_payment(self, user, amount):
        with transaction.atomic():
            collect = Collect.objects.select_for_update().get(pk=self.pk)
