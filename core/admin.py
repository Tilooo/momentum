# core/admin.py

from django.contrib import admin
from .models import Client, Invoice

admin.site.register(Client)
admin.site.register(Invoice)