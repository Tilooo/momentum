# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice-list'),
]