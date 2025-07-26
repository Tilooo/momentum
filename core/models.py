# core/models.py

from django.db import models
from django.utils import timezone


class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    # Invoice Status Choices
    DRAFT = 'DRAFT'
    SENT = 'SENT'
    PAID = 'PAID'
    CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SENT, 'Sent'),
        (PAID, 'Paid'),
        (CANCELLED, 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    title = models.CharField(max_length=255)
    invoice_number = models.CharField(max_length=50, unique=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.client.name}"

    class Meta:
        ordering = ['-created_at']  # Shows newest invoices first