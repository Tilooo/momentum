# core/views.py

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Invoice, Client
from .forms import InvoiceForm

def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'core/invoice_list.html', {'invoices': invoices})

def invoice_create(request):
    """ Renders a blank form for creating a new invoice. """
    form = InvoiceForm()
    return render(request, 'core/partials/invoice_form.html', {'form': form})

def invoice_store(request):
    """ Processes the submitted form for creating a new invoice. """
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_number = f'INV-{random.randint(1000, 9999)}'
            invoice.save()
            new_invoice_html = render(request, 'core/partials/invoice_item.html', {'invoice': invoice})
            clear_form_html = '<div id="invoice-form-container" hx-swap-oob="true"></div>'
            remove_empty_message_html = '<li id="empty-message" hx-swap-oob="true"></li>'
            return HttpResponse(new_invoice_html.content.decode() + clear_form_html + remove_empty_message_html)
        else:
            return render(request, 'core/partials/invoice_form.html', {'form': form})
    return HttpResponse("Invalid request method.", status=405)

def invoice_edit(request, pk):
    """ Renders the form pre-filled with an existing invoice's data. """
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(instance=invoice)
    return render(request, 'core/partials/invoice_form.html', {'form': form, 'invoice': invoice})

def invoice_update(request, pk):
    """ Processes the submitted form for updating an existing invoice. """
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return render(request, 'core/partials/invoice_item.html', {'invoice': invoice})
        else:
            return render(request, 'core/partials/invoice_form.html', {'form': form, 'invoice': invoice})
    return HttpResponse("Invalid request method.", status=405)

def invoice_detail(request, pk):
    """ Returns the HTML for a single invoice item (used for cancelling an edit). """
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/partials/invoice_item.html', {'invoice': invoice})

def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'DELETE':
        invoice.delete()
        return HttpResponse("")
    return HttpResponse(status=405)

def clear_form(request):
    return HttpResponse("")