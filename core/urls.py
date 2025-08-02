# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice-list'),
    path('invoices/create/', views.invoice_create, name='invoice-create'),
    path('invoices/store/', views.invoice_store, name='invoice-store'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice-edit'),
    path('invoices/<int:pk>/update/', views.invoice_update, name='invoice-update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice-delete'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice-detail'),
    path('invoices/clear/', views.clear_form, name='clear-form'),

    # expense urls
    path('expenses/', views.expense_list, name='expense-list'),
    path('expenses/inbox/', views.expense_inbox, name='expense-inbox'),
    path('expenses/parse/', views.parse_receipt, name='parse-receipt'),

    # expense CRUD urls
    path('expenses/create/', views.expense_create, name='expense-create'),
    path('expenses/store/', views.expense_store, name='expense-store'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense-edit'),
    path('expenses/<int:pk>/update/', views.expense_update, name='expense-update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense-delete'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense-detail'),
]