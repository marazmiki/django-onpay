# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.conf.urls import url
from onpay.views import result


urlpatterns = [
    url(r'^result/$', result, name='onpay_result'),
]
