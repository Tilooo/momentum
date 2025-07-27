# core/views.py

from django.shortcuts import render, redirect
from .models import Invoice, Client
from .forms import InvoiceForm
import random # for invoice numbers

def invoice_list(request):
    invoices = Invoice.objects.all()
    context = {
        'invoices': invoices
    }
    return render(request, 'core/invoice_list.html', context)


def invoice_create(request):
    """
    Renders a blank form for creating an invoice.
    This view is called by HTMX.
    """
    form = InvoiceForm()
    context = {'form': form}
    return render(request, 'core/partials/invoice_form.html', context)


def invoice_store(request):
    """
    Processes the submitted invoice form.
    """
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            # generates a unique invoice number
            invoice.invoice_number = f'INV-{random.randint(1000, 9999)}'
            invoice.save()

            # after saving, returns a small HTML snippet of the new invoice
            context = {'invoice': invoice}
            return render(request, 'core/partials/invoice_item.html', context)

    # if form is not valid, handled errors here
    return redirect('invoice-list')