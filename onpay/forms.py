# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django import forms
from onpay.models import Order
from dateutil.parser import parse


CURRENCY_CHOICES = (
    ('RUR', 'RUR'),
    ('TST', 'TST'),
)


class CheckForm(forms.Form):
    TYPE_CHOICES = (
        ('check', 'check'),
        ('pay', 'payment'),
    )
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    md5 = forms.CharField()
    order_currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    order_amount = forms.FloatField()
    amount = forms.FloatField()
    pay_for = forms.ModelChoiceField(queryset=Order.objects.all())


class PayForm(CheckForm):
    balance_amount = forms.FloatField()
    paid_amount = forms.FloatField()
    paymentDateTime = forms.CharField()
    onpay_id = forms.IntegerField()
    user_phone = forms.CharField(required=False)
    balance_currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    note = forms.CharField(required=False)
    exchange_rate = forms.FloatField()
    protection_code = forms.CharField(required=False)
    day_to_expiry = forms.CharField(required=False)
    user_email = forms.EmailField()

    def clean_paymentDateTime(self):
        try:
            return parse(self.cleaned_data['paymentDateTime'])
        except TypeError:
            raise forms.ValidationError('Wrong paymentDateTime value')
