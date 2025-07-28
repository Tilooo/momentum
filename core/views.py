# core/views.py

import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Invoice, Client
from .forms import InvoiceForm


def invoice_list(request):
    """
    Fetches all invoices from the database and passes them to the template.
    """
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
    Handles both success and validation errors.
    """
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the invoice
            invoice = form.save(commit=False)
            invoice.invoice_number = f'INV-{random.randint(1000, 9999)}'
            invoice.save()

            new_invoice_html = render(request, 'core/partials/invoice_item.html', {'invoice': invoice})

            clear_form_html = '<div id="invoice-form-container" hx-swap-oob="true"></div>'

            remove_empty_message_html = '<li id="empty-message" hx-swap-oob="true"></li>'

            response_html = new_invoice_html.content.decode() + clear_form_html + remove_empty_message_html

            return HttpResponse(response_html)
        else:
            context = {'form': form}
            return render(request, 'core/partials/invoice_form.html', context)

    return HttpResponse("Invalid request method.", status=405)


def clear_form(request):
    """
    Returns an empty response to clear the form container via HTMX.
    """
    return HttpResponse("")