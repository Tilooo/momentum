# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # C(R)UD: Create
    path('', views.invoice_list, name='invoice-list'),
    path('invoices/create/', views.invoice_create, name='invoice-create'),
    path('invoices/store/', views.invoice_store, name='invoice-store'),

    # CR(U)D: Update
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice-edit'),
    path('invoices/<int:pk>/update/', views.invoice_update, name='invoice-update'),

    # CRU(D): Delete
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice-delete'),

    # Helper URLs
    path('invoices/clear/', views.clear_form, name='clear-form'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice-detail'),
]