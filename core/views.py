# core/views.py

import re
import random
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils.timezone import now

from .models import Invoice, Client, Expense
from .forms import InvoiceForm, ExpenseForm


# invoice views
def invoice_list(request):
    invoices = Invoice.objects.all()
    paid_invoices_total = Invoice.objects.filter(status='PAID').aggregate(total=Sum('amount'))
    total_income = paid_invoices_total['total'] or Decimal('0.00')
    sent_invoices_total = Invoice.objects.filter(status='SENT').aggregate(total=Sum('amount'))
    total_outstanding = sent_invoices_total['total'] or Decimal('0.00')
    TAX_RATE = Decimal('0.25')
    tax_pool = total_income * TAX_RATE
    context = {'invoices': invoices, 'total_income': total_income, 'total_outstanding': total_outstanding, 'tax_pool': tax_pool}
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

# expense views

def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'core/expense_list.html', {'expenses': expenses})

def expense_inbox(request):
    expenses = Expense.objects.all()[:5]
    return render(request, 'core/expense_inbox.html', {'expenses': expenses})

def parse_receipt(request):
    if request.method == 'POST':
        receipt_text = request.POST.get('receipt_text', '').lower()
        amount = None
        title = "Unknown Expense"
        amount_match = re.search(r'total[\s:]*\$?(\d+\.\d{2})', receipt_text)
        if not amount_match:
            amount_match = re.search(r'\$?(\d+\.\d{2})', receipt_text)
        if amount_match:
            amount = Decimal(amount_match.group(1))
        if 'uber' in receipt_text:
            title = 'Uber Ride'
        elif 'amazon' in receipt_text:
            title = 'Amazon Purchase'
        elif 'google' in receipt_text:
            title = 'Google Service'
        if amount:
            Expense.objects.create(title=title, amount=amount, expense_date=now().date())
        return redirect('expense-inbox')
    return redirect('expense-inbox')

# expense CRUD views

def expense_create(request):
    form = ExpenseForm()
    return render(request, 'core/partials/expense_create_form.html', {'form': form})

def expense_store(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            new_item_html = render(request, 'core/partials/expense_item.html', {'expense': expense}).content.decode()
            clear_form_html = '<div id="expense-form-container" hx-swap-oob="true"></div>'
            return HttpResponse(new_item_html + clear_form_html)
        else:
            return render(request, 'core/partials/expense_create_form.html', {'form': form})
    return HttpResponse("Invalid request method.", status=405)

def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    form = ExpenseForm(instance=expense)
    return render(request, 'core/partials/expense_edit_form.html', {'form': form, 'expense': expense})

def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return render(request, 'core/partials/expense_item.html', {'expense': expense})
        else:
            return render(request, 'core/partials/expense_edit_form.html', {'form': form, 'expense': expense})
    return HttpResponse("Invalid request method.", status=405)

def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'DELETE':
        expense.delete()
        return HttpResponse("")
    return HttpResponse(status=405)

def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    return render(request, 'core/partials/expense_item.html', {'expense': expense})