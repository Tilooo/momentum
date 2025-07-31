# core/admin.py

from django.contrib import admin
from .models import Client, Invoice, Expense

admin.site.register(Client)
admin.site.register(Invoice)
admin.site.register(Expense)