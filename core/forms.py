# core/forms.py

from django import forms
from .models import Invoice, Client, Expense #
from django.utils.timezone import now

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'title', 'amount', 'due_date', 'status']
        widgets = {
            'client': forms.Select(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'title': forms.TextInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'amount': forms.NumberInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'status': forms.Select(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all()
        if not self.instance.pk:
            self.fields['due_date'].initial = now().date()

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'expense_date', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'amount': forms.NumberInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'category': forms.TextInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md', 'placeholder': 'e.g., Software, Travel'}),
        }