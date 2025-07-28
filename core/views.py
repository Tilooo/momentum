# core/views.py

import random
from django.shortcuts import render, redirect, get_object_or_404
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
            invoice = form.save(commit=False)
            invoice.invoice_number = f'INV-{random.randint(1000, 9999)}'
            invoice.save()

            # render the new item
            context = {'invoice': invoice}
            response = render(request, 'core/partials/invoice_item.html', context)

            # a special HTMX header to add the new item to the top of the list, clear the form after success.
            response['HX-Trigger'] = 'clear-form-and-add-item'
            return response
        else:       # if the form is NOT valid
            context = {'form': form}
            return render(request, 'core/partials/invoice_form.html', context)

    return HttpResponse("Invalid request method.", status=405)


def clear_form(request):
    """
    Returns an empty response to clear the form container via HTMX.
    """
    return HttpResponse("")


def invoice_delete(request, pk):
    """
    Deletes an invoice and returns an empty response.
    """
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'DELETE':
        invoice.delete()
        return HttpResponse("")

    return HttpResponse(status=405)