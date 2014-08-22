# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.dispatch import Signal


order_created = Signal(providing_args=['order'])
order_updated = Signal(providing_args=['order'])
order_success = Signal(providing_args=['order'])
order_failure = Signal(providing_args=['order'])