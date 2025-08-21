# coding=utf-8
from django import forms
from django.forms import ModelForm
from .models import InvoiceModel


class InvoiceModelForm(forms.ModelForm):
    class Meta:
        model = InvoiceModel
        fields = '__all__'
        exclude = ['invoice_id', 'quotation', 'created_by']

    def __init__(self, *args, **kwargs):
        super(InvoiceModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control w3-input w3-border w3-round-large w3-margin-bottom'
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={
                    'class':'form-control w3-input w3-border w3-round-large w3-margin-bottom',
                    'type':'date'
                })




'''
# model form snipet

class ModelNameForm(forms.ModelForm):

    class Meta:
        model = ModelName
        fields = ['x', 'y', 'z']

        labels = {
            'x': 'Name x',
            'y': 'Name y',
            'z': 'Name Z',
        }

    def __init__(self, *args, **kwargs):
        super(ModelNameForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ModelNameForm, self).clean()
        return cleaned_data
'''
