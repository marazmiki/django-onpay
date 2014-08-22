# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django import test
from django.core.urlresolvers import reverse_lazy
from django.utils import six
from django.utils.timezone import now
from onpay.utils import create_order
from onpay import signals


# Some constants
ONPAY_ID = '123'
CRC_PAY_CORRECT = '5C89A599E3E15DE4E3EC2803DC0BF596'
CRC_PAY_CREATE = 'BEAC0AA488C13E9B89B5F8B8DA425F5C'
CRC_CHECK_CORRECT = '48CE93AD7E0053BA37316676F4B29C4A'
CRC_CHECK_CREATE = '8E1D15E585D02885B40BA7E69C7572FF'


def signal_catcher(*args, **kwargs):
    raise ZeroDivisionError


class TestViews(test.TestCase):
    urls = 'onpay.urls'

    def setUp(self):
        self.order = create_order(amount=10,
                                  currency='RUR',
                                  comment='Test order',
                                  email='bender@ilovebender.com')
        self.client = test.Client()
        self.url = reverse_lazy('onpay_result')

    def get_check_data(self):
        return {
            'type': 'check',
            'md5': CRC_CHECK_CORRECT,
            'order_currency': self.order.currency,
            'order_amount': 1.0,
            'amount': 1.0,
            'pay_for': self.order.pk
        }

    def get_pay_data(self):
        return {
            'type': 'pay',
            'md5': CRC_CHECK_CORRECT,
            'order_currency': self.order.currency,
            'order_amount': 1.0,
            'amount': 1.0,
            'pay_for': self.order.pk,
            'balance_amount': 1.0,
            'paid_amount': 1.0,
            'paymentDateTime': now().isoformat(),
            'onpay_id': ONPAY_ID,
            'balance_currency': self.order.currency,
            'exchange_rate': 1,
            'user_email': 'bender@ilovebender.com'
        }

    def assertOrderSuccessfullyPaid(self, order):
        self.assertTrue(
            order.__class__.objects.get(pk=order.pk).is_successfully_paid()
        )

    def assertOrderFailed(self, order):
        self.assertFalse(
            order.__class__.objects.get(pk=order.pk).is_successfully_paid()
        )

    def test_bad_request(self):
        resp = self.client.post(self.url)
        self.assertEquals(400, resp.status_code)

    def test_bad_request_pay_wrong_date(self):
        data = self.get_pay_data()
        data.update(paymentDateTime='not-a-timestamp')
        del data['type']  # wittingly invalid form
        resp = self.client.post(self.url, data=data)
        self.assertEquals(400, resp.status_code)

    def test_check_form_valid(self):
        resp = self.client.post(self.url, self.get_check_data())

        self.assertEquals(200, resp.status_code)
        self.assertContains(resp, '<comment>OK</comment>')
        self.assertContains(resp, CRC_CHECK_CREATE)

    def test_check_form_valid_md5_failed(self):
        data = self.get_check_data()
        data.update(md5='*****')
        resp = self.client.post(self.url, data=data)
        self.assertEquals(400, resp.status_code)
        self.assertIn('failed', resp.content)

    def test_pay_form_valid(self):
        data = self.get_pay_data()
        data.update(md5=CRC_PAY_CORRECT)
        resp = self.client.post(self.url, data=data)

        self.assertEquals(200, resp.status_code)
        self.assertContains(resp, '<comment>OK</comment>')
        self.assertContains(resp, CRC_PAY_CREATE)
        self.assertOrderSuccessfullyPaid(self.order)

    def test_pay_form_valid_md5_failed(self):
        data = self.get_pay_data()
        data.update(md5='NOT_' + CRC_PAY_CORRECT)
        resp = self.client.post(self.url, data=data)
        self.assertEquals(400, resp.status_code)
        self.assertOrderFailed(self.order)


class TestUtils(test.TestCase):
    def test_create_order_full(self):
        order = create_order(amount=10.0,
                             currency='RUR',
                             comment='Test order',
                             email='bender@ilovebender.com')

        self.assertEquals(10.0, order.amount)
        self.assertEquals('RUR', order.currency)
        self.assertEquals('Test order', order.comment)
        self.assertEquals('bender@ilovebender.com', order.email)
        self.assertEquals(order.MODE_LIVE, order.mode)
        self.assertEquals(order.STATE_WAITING, order.state)

    def test_create_order_with_tst_currency(self):
        order = create_order(amount=10, currency='TST', comment='Test order',
                             email='bender@ilovebender.com')
        self.assertEquals('TST', order.currency)
        self.assertEquals(order.MODE_TEST, order.mode)

    def test_create_order_with_unknown_currency(self):
        def raised_exception():
            create_order(amount=10,
                         currency='WTF',
                         comment='Test order',
                         email='bender@ilovebender.com')
        self.assertRaises(TypeError, raised_exception)


class TestModels(test.TestCase):
    def create_order(self):
        return create_order(amount=10, currency='RUR',
                            comment='Test order',
                            email='bender@ilovebender.com')

    def assertSignalCatched(self, signal, callable_, ):
        signal.connect(signal_catcher)
        try:
            callable_()
            self.fail('Signal are not sent')
        except ZeroDivisionError:
            pass
        finally:
            signal.disconnect(signal_catcher)

    def setUp(self):
        self.order = self.create_order()

    def test_str(self):
        self.assertIn(container=six.text_type(self.order),
                      member=six.text_type(self.order.pk))

    def test_mark_as_success(self):
        self.order.mark_as_success()
        self.assertEquals(self.order.STATE_SUCCESS, self.order.state)

    def test_mark_as_success_signal(self):
        self.assertSignalCatched(signals.order_success,
                                 lambda: self.order.mark_as_success())

    def test_mark_as_failure(self):
        self.order.mark_as_failure()
        self.assertEquals(self.order.STATE_FAILURE,
                          self.order.state)

    def test_mark_as_failure_signal(self):
        self.assertSignalCatched(signals.order_failure,
                                 lambda: self.order.mark_as_failure())

    def test_can_be_payed(self):
        self.assertTrue(self.order.can_be_payed())

    def test_can_be_payed_not(self):
        order = self.order
        for state in [order.STATE_FAILURE,
                      order.STATE_SUCCESS,
                      order.STATE_EXPIRED]:
            order.state = state
            order.save()
            self.assertFalse(order.can_be_payed())

    def test_is_successfully_paid(self):
        order = self.order
        order.mark_as_success()
        self.assertTrue(order.is_successfully_paid())

    def test_is_successfully_paid_not(self):
        order = self.order
        for state in [order.STATE_FAILURE,
                      order.STATE_WAITING,
                      order.STATE_EXPIRED]:
            order.state = state
            order.save()
            self.assertFalse(order.is_successfully_paid())

    def test_is_pay_failed(self):
        order = self.order
        for state in [order.STATE_EXPIRED, order.STATE_FAILURE]:
            order.state = state
            order.save()
            self.assertTrue(order.is_pay_failed())

    def test_is_pay_failed_not(self):
        order = self.create_order()
        for state in [order.STATE_SUCCESS, order.STATE_WAITING]:
            order.state = state
            order.save()
            self.assertFalse(order.is_pay_failed())

    def test_get_pay_url_smoke(self):
        order = self.create_order()
        self.assertEquals(order.pay_url,
                          order.get_pay_url())

    def test_crc_check_correct(self):
        self.assertTrue(self.order.crc_check_correct(CRC_CHECK_CORRECT))

    def test_crc_check_correct_not(self):
        self.assertFalse(
            self.order.crc_check_correct('NOT_' + CRC_CHECK_CORRECT)
        )

    def test_crc_check_create(self):
        self.assertEquals(
            CRC_CHECK_CREATE, self.order.crc_check_create()
        )

    def test_crc_pay_correct(self):
        self.assertTrue(self.order.crc_pay_correct(crc=CRC_PAY_CORRECT,
                                                   onpay_id='123',
                                                   order_amount=1.0))

    def test_crc_pay_correct_not(self):
        self.assertFalse(
            self.order.crc_pay_correct(crc='NOT_' + CRC_PAY_CORRECT,
                                       onpay_id=ONPAY_ID,
                                       order_amount=1.0)
        )

    def test_crc_pay_get(self):
        self.assertEquals(CRC_PAY_CORRECT,
                          self.order.crc_pay_get(onpay_id=ONPAY_ID,
                                                 order_amount=1.0))

    def test_crc_pay_create(self):
        self.assertEquals(
            CRC_PAY_CREATE,
            self.order.crc_pay_create(onpay_id=ONPAY_ID,
                                      order_amount=1.0))
