# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.contrib import admin
from onpay.models import Order


class OrderAdmin(admin.ModelAdmin):
    list_filter = ['state']
    date_hierarchy = 'date_created'
    list_display = ['id', 'comment', 'amount', 'email',
                    'date_created', 'state']

admin.site.register(Order, OrderAdmin)
