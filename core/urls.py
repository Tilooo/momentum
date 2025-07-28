# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice-list'),
    path('invoices/create/', views.invoice_create, name='invoice-create'),
    path('invoices/store/', views.invoice_store, name='invoice-store'),
    path('invoices/clear/', views.clear_form, name='clear-form'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice-delete'),
]