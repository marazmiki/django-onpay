# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from onpay import settings
from onpay.signals import (order_created, order_updated,
                           order_success, order_failure)
import hashlib
import urllib


try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@python_2_unicode_compatible
class Order(models.Model):
    MODE_LIVE = 0
    MODE_TEST = 1

    STATE_SUCCESS = 0
    STATE_FAILURE = 1
    STATE_WAITING = 3
    STATE_EXPIRED = 2

    amount = models.IntegerField(_('amount'))
    currency = models.CharField(_('currency'),
                                max_length=3,
                                default=settings.ONPAY_CURRENCY,
                                choices=settings.ONPAY_CURRENCIES)
    comment = models.TextField(_('order notes'), default='')
    email = models.EmailField(_('buyer e-mail'))
    date_created = models.DateTimeField(_('created at'), auto_now_add=True)
    state = models.IntegerField(_('order status'),
                                default=STATE_WAITING, choices=(
                                    (STATE_SUCCESS, _('Success')),
                                    (STATE_FAILURE, _('Failed')),
                                    (STATE_WAITING, _('Waiting')),
                                    (STATE_EXPIRED, _('Expired')),
                                ))
    mode = models.IntegerField(_('mode'), default=MODE_LIVE, choices=(
                                   (MODE_LIVE, _('live')),
                                   (MODE_TEST, _('text')),
                               ))

    def mark_as_success(self):
        self._mark(state=self.STATE_SUCCESS, signal=order_success)

    def mark_as_failure(self):
        self._mark(state=self.STATE_FAILURE, signal=order_failure)

    def can_be_payed(self):
        return self.state == self.STATE_WAITING

    def is_successfully_paid(self):
        return self.state == self.STATE_SUCCESS

    def is_pay_failed(self):
        return self.state in [self.STATE_EXPIRED, self.STATE_FAILURE]

    def get_pay_url(self, currency=settings.ONPAY_CURRENCY,
                    success_url=settings.ONPAY_SUCCESS_URL,
                    failure_url=settings.ONPAY_SUCCESS_URL):
        pattern = 'fix;{amount:.1f};{currency};{order_id:d};no;{secret}'
        md5_str = pattern.format(amount=self.amount,
                                 currency=settings.ONPAY_CURRENCY,
                                 secret=settings.ONPAY_SECRET,
                                 order_id=self.id)
        if six.PY3:
            md5_str = md5_str.encode('utf-8')
        md5 = hashlib.md5(md5_str).hexdigest()

        return settings.ONPAY_GATE_URL + '?' + urlencode({
            'pay_mode': 'fix',
            'f': 7,
            'price': self.amount,
            'pay_for': self.id,
            'convert': 'no',
            'price_final': 'true',
            'user_email': self.email,
            'md5': md5,
            'currency': currency,
            'url_success_enc': success_url,
            'url_fail_enc': failure_url,
        })

    pay_url = property(get_pay_url)

    def _mark(self, state, signal):
        self.state = state
        self.save(update_fields=['state'])
        signal.send(sender=self.__class__, order=self)

    def _check(self, flag=''):
        pattern = 'check;{order_id};{amount:.1f};{currency};{flag}{secret}'
        raw_string = pattern.format(order_id=self.id,
                                    amount=self.amount,
                                    currency=settings.ONPAY_CURRENCY,
                                    secret=settings.ONPAY_SECRET,
                                    flag=flag)
        if six.PY3:
            raw_string = raw_string.encode('utf-8')
        hashed_string = hashlib.md5(raw_string).hexdigest().upper()
        return hashed_string

    def crc_check_correct(self, crc):
        return crc == self.crc_check_get()

    def crc_check_get(self):
        return self._check(flag='')

    def crc_check_create(self):
        return self._check(flag='0;')

    def crc_pay_correct(self, crc, onpay_id, order_amount):
        actual_crc = self.crc_pay_get(onpay_id, order_amount)
        # print("expected crc: %s, actual: %s" % (crc, actual_crc))
        return crc == actual_crc

    def crc_pay_get(self, onpay_id, order_amount):
        pattern = ('pay;{order_id};{onpay_id};{order_amount};'
                   '{currency};{secret}')
        md5source = pattern.format(order_id=self.id,
                                   onpay_id=onpay_id,
                                   order_amount=order_amount,
                                   currency=settings.ONPAY_CURRENCY,
                                   secret=settings.ONPAY_SECRET)
        if six.PY3:
            md5source = md5source.encode('utf-8')
        md5hash = hashlib.md5(md5source).hexdigest().upper()
        return md5hash

    def crc_pay_create(self, onpay_id, order_amount):
        pattern = ('pay;{po:d};{onpay_id};{order_id:d};{order_amount};'
                   '{currency};0;{secret}')
        result_m5source = pattern.format(po=self.id,
                                         onpay_id=onpay_id,
                                         order_id=self.id,
                                         order_amount=order_amount,
                                         currency=settings.ONPAY_CURRENCY,
                                         secret=settings.ONPAY_SECRET)
        if six.PY3:
            result_m5source = result_m5source.encode('utf-8')
        result_m5hash = hashlib.md5(result_m5source).hexdigest().upper()
        return result_m5hash

    def __str__(self):
        return '#%s' % self.pk

    class Meta(object):
        verbose_name = _('payment')
        verbose_name_plural = _('payments')


def order_trigger(**kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    sender = kwargs['sender']

    if created:
        order_created.send(sender=sender, order=instance)
    else:
        order_updated.send(sender=sender, order=instance)


def mode_trigger(**kwargs):
    instance = kwargs['instance']
    if instance.pk:
        return
    if instance.currency == 'TST':
        instance.mode = instance.MODE_TEST


models.signals.pre_save.connect(mode_trigger, sender=Order,
                                dispatch_uid='onpay.models')
models.signals.post_save.connect(order_trigger, sender=Order,
                                 dispatch_uid='onpay.models')
