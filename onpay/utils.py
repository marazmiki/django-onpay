# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from onpay.models import Order
from onpay.settings import ONPAY_CURRENCIES


def create_order(amount, currency, comment, email):
    if currency.upper() not in dict(ONPAY_CURRENCIES):
        raise TypeError('Unsupported currency code %s' % currency)
    return Order.objects.create(amount=amount,
                                currency=currency,
                                comment=comment,
                                email=email)
