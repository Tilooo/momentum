# core/views.py

from django.shortcuts import render
from .models import Invoice

def invoice_list(request):
    invoices = Invoice.objects.all()
    context = {
        'invoices': invoices
    }
    return render(request, 'core/invoice_list.html', context)