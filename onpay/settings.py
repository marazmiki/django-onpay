# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.conf import settings as s
from django.utils.translation import ugettext_lazy as _


gate_url = 'https://secure.onpay.ru/pay/{gate}'


ONPAY_CURRENCY = getattr(s, 'ONPAY_CURRENCY', 'RUR')
ONPAY_CURRENCIES = getattr(s, 'ONPAY_CURRENCIES', (
    ('RUR', _('Russian rubles')),
    ('TST', _('Test currency')),
))
ONPAY_SECRET = getattr(s, 'ONPAY_SECRET', '****************')
ONPAY_GATE = getattr(s, 'ONPAY_GATE', 'login')
ONPAY_GATE_URL = getattr(s, 'ONPAY_GATE_URL', gate_url.format(gate=ONPAY_GATE))
ONPAY_SUCCESS_URL = getattr(s, 'ONPAY_SUCCESS_URL', '')
ONPAY_FAILURE_URL = getattr(s, 'ONPAY_SUCCESS_URL', '')
