# core/views.py

import re
import random
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils.timezone import now

from .models import Invoice, Client, Expense
from .forms import InvoiceForm


def invoice_list(request):
    """
    Fetches all invoices and calculates financial totals for the dashboard.
    """
    invoices = Invoice.objects.all()

    # total income from all PAID invoices calculated
    paid_invoices_total = Invoice.objects.filter(status='PAID').aggregate(total=Sum('amount'))
    total_income = paid_invoices_total['total'] or Decimal('0.00')

    # total outstanding from all SENT invoices calculated
    sent_invoices_total = Invoice.objects.filter(status='SENT').aggregate(total=Sum('amount'))
    total_outstanding = sent_invoices_total['total'] or Decimal('0.00')

    # tax rate as a Decimal
    TAX_RATE = Decimal('0.25')
    tax_pool = total_income * TAX_RATE

    context = {
        'invoices': invoices,
        'total_income': total_income,
        'total_outstanding': total_outstanding,
        'tax_pool': tax_pool,
    }
    return render(request, 'core/invoice_list.html', context)



def invoice_create(request):
    form = InvoiceForm()
    return render(request, 'core/partials/invoice_create_form.html', {'form': form})


def invoice_store(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_number = f'INV-{random.randint(1000, 9999)}'
            invoice.save()
            new_item_html = render(request, 'core/partials/invoice_item.html', {'invoice': invoice}).content.decode()
            clear_form_html = '<div id="invoice-form-container" hx-swap-oob="true"></div>'
            remove_empty_message_html = '<li id="empty-message" hx-swap-oob="true"></li>'
            return HttpResponse(new_item_html + clear_form_html + remove_empty_message_html)
        else:
            return render(request, 'core/partials/invoice_create_form.html', {'form': form})
    return HttpResponse("Invalid request method.", status=405)


def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(instance=invoice)
    return render(request, 'core/partials/invoice_edit_form.html', {'form': form, 'invoice': invoice})


def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return render(request, 'core/partials/invoice_item.html', {'invoice': invoice})
        else:
            return render(request, 'core/partials/invoice_edit_form.html', {'form': form, 'invoice': invoice})
    return HttpResponse("Invalid request method.", status=405)


def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'DELETE':
        invoice.delete()
        return HttpResponse("")
    return HttpResponse(status=405)


def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/partials/invoice_item.html', {'invoice': invoice})


def clear_form(request):
    return HttpResponse("")

def invoice_create(request):
    form = InvoiceForm()
    return render(request, 'core/partials/invoice_create_form.html', {'form': form})

def invoice_store(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_number = f'INV-{random.randint(1000, 9999)}'
            invoice.save()
            new_item_html = render(request, 'core/partials/invoice_item.html', {'invoice': invoice}).content.decode()
            clear_form_html = '<div id="invoice-form-container" hx-swap-oob="true"></div>'
            remove_empty_message_html = '<li id="empty-message" hx-swap-oob="true"></li>'
            return HttpResponse(new_item_html + clear_form_html + remove_empty_message_html)
        else:
            return render(request, 'core/partials/invoice_create_form.html', {'form': form})
    return HttpResponse("Invalid request method.", status=405)

def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(instance=invoice)
    return render(request, 'core/partials/invoice_edit_form.html', {'form': form, 'invoice': invoice})

def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return render(request, 'core/partials/invoice_item.html', {'invoice': invoice})
        else:
            return render(request, 'core/partials/invoice_edit_form.html', {'form': form, 'invoice': invoice})
    return HttpResponse("Invalid request method.", status=405)

def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'DELETE':
        invoice.delete()
        return HttpResponse("")
    return HttpResponse(status=405)

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/partials/invoice_item.html', {'invoice': invoice})

def clear_form(request):
    return HttpResponse("")


def expense_inbox(request):
    expenses = Expense.objects.all()[:5] # to get the 5 most recent expenses
    context = {
        'expenses': expenses
    }
    return render(request, 'core/expense_inbox.html', context)


def parse_receipt(request):
    if request.method == 'POST':
        receipt_text = request.POST.get('receipt_text', '').lower()

        amount = None
        title = "Unknown Expense"

        amount_match = re.search(r'total[\s:]*\$?(\d+\.\d{2})', receipt_text)  # to find an amount
        if not amount_match:
            amount_match = re.search(r'\$?(\d+\.\d{2})', receipt_text)

        if amount_match:
            amount = Decimal(amount_match.group(1))

        # to identify the vendor
        if 'uber' in receipt_text:
            title = 'Uber Ride'
        elif 'amazon' in receipt_text:
            title = 'Amazon Purchase'
        elif 'google' in receipt_text:
            title = 'Google Service'

        if amount:
            # If amount is found, to create the expense
            Expense.objects.create(
                title=title,
                amount=amount,
                expense_date=now().date()
            )
            messages.success(request, f"Successfully created expense: {title} for ${amount}")
        else:
            messages.error(request, "Could not find a valid total amount in the receipt text.")

    return redirect('expense-inbox')