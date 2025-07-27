# core/forms.py

from django import forms
from .models import Invoice, Client
from django.utils.timezone import now

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'title', 'amount', 'due_date']
        widgets = {
            'client': forms.Select(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'title': forms.TextInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'amount': forms.NumberInput(attrs={'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full p-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # the client field a dropdown of existing clients
        self.fields['client'].queryset = Client.objects.all()
        # For now, a default due date
        self.fields['due_date'].initial = now().date()