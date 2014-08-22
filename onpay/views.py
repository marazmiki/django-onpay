# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from onpay.forms import CheckForm, PayForm
import logging


logger = logging.getLogger(__name__)


@csrf_exempt
def result(request):
    check_form = CheckForm(request.POST or None)
    pay_form = PayForm(request.POST or None)

    if not check_form.is_valid() and not pay_form.is_valid():
        return HttpResponseBadRequest('Wrong API request')

    if pay_form.is_valid():
        po = pay_form.cleaned_data['pay_for']
        onpay_id = pay_form.cleaned_data['onpay_id']
        order_amount = pay_form.cleaned_data['order_amount']

        if po.crc_pay_correct(crc=pay_form.cleaned_data['md5'],
                              order_amount=order_amount,
                              onpay_id=onpay_id):

            md5_checksum = po.crc_pay_create(order_amount=order_amount,
                                             onpay_id=onpay_id)

            result_xml = render_to_string('onpay/pay_success.xml',
                                          {'onpay_id': onpay_id,
                                           'pay_for': po.id,
                                           'order_id': po.id,
                                           'md5_checksum': md5_checksum})
            po.mark_as_success()
            return HttpResponse(result_xml, content_type='text/xml')

        else:
            po.mark_as_failure()

    if check_form.is_valid():
        order = check_form.cleaned_data['pay_for']

        if order.crc_check_correct(check_form.cleaned_data['md5']):
            md5_checksum = order.crc_check_create()
            result_xml = render_to_string('onpay/check_success.xml',
                                          {'md5_checksum': md5_checksum,
                                           'pay_for': order.id})
            return HttpResponse(result_xml, content_type='text/xml')

        else:
            logger.debug('check failed')
            return HttpResponseBadRequest('Check failed')
