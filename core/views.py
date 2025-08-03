# core/views.py

import re
from datetime import datetime
import random
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils.timezone import now
from django.contrib import messages

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
    """
    Parses text from a submitted receipt and attempts to create an Expense.
    """
    if request.method == 'POST':
        receipt_text = request.POST.get('receipt_text', '').lower()

        PARSER_RULES = [
            {'vendor': 'Uber', 'keywords': ['uber'], 'category': 'Travel'},
            {'vendor': 'Amazon', 'keywords': ['amazon', 'order #'], 'category': 'Shopping'},
            {'vendor': 'Google', 'keywords': ['google llc'], 'category': 'Software'},
            {'vendor': 'Starbucks', 'keywords': ['starbucks'], 'category': 'Food & Drink'},
            {'vendor': 'Maxima', 'keywords': ['maxima'], 'category': 'Groceries'},
            {'vendor': 'Iki', 'keywords': ['iki'], 'category': 'Groceries'},
        ]

        # default values
        amount = None
        title = "Unknown Expense"
        category = "Miscellaneous"
        expense_date = now().date()  # default to today

        # parsing logic

        # parse the amount
        amount = None

        # split the receipt into individual lines
        lines = receipt_text.split('\n')

        lines.reverse()

        total_line = None
        for line in lines:
            if 'total' in line and 'subtotal' not in line:
                total_line = line
                break

        if total_line:
            amount_match = re.search(r'€?(\d+\.\d{2})', total_line)
            if amount_match:
                amount = Decimal(amount_match.group(1))

        if not amount:
            all_numbers = re.findall(r'€?(\d+\.\d{2})', receipt_text)
            if all_numbers:
                amount = max([Decimal(n) for n in all_numbers])

        for rule in PARSER_RULES:
            if any(keyword in receipt_text for keyword in rule['keywords']):
                title = f"{rule['vendor']} Purchase"
                category = rule['category']
                break  # stop after the first match

        # parse the date
        date_patterns = [
            r'\b(\w{3})\s(\d{1,2}),\s(\d{4})\b',  # Mmm DD, YYYY
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{1,2})/(\d{1,2})/(\d{4})'  # DD/MM/YYYY
        ]
        date_str = None
        for pattern in date_patterns:
            date_match = re.search(pattern, receipt_text)
            if date_match:
                date_str = date_match.group(0)
                break

        if date_str:
            try:
                expense_date = datetime.strptime(date_str, '%b %d, %Y').date()
            except ValueError:
                try:
                    expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        expense_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    except ValueError:
                        expense_date = now().date()

        # create the expense
        if amount:
            Expense.objects.create(
                title=title,
                amount=amount,
                expense_date=expense_date,
                category=category
            )
            messages.success(request, f"Successfully created expense: '{title}' for €{amount}")
        else:
            messages.error(request, "Could not find a valid total amount in the receipt text.")

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