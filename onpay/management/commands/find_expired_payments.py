# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.core.management.base import NoArgsCommand
from django.utils.timezone import now
from onpay.models import Order
import datetime


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        today = now()
        limit = today - datetime.timedelta(seconds=60 * 60)

        Order.objects.filter(
            date_created__lte=limit
        ).update(state=Order.STATE_EXPIRED)
