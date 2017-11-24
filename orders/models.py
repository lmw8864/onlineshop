from django.db import models
from shop.models import Product

from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from coupons.models import Coupon

from .iamport import validation_prepare, get_transaction
import time
import random
import hashlib
from django.db.models.signals import post_save


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_discount(self):
        return self.get_total_cost() * (self.discount / Decimal('100'))

    def get_total_cost_after_discount(self):
        total_cost = self.get_total_cost()
        total_discount = self.get_total_discount()
        return total_cost - total_discount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items')
    product = models.ForeignKey(Product, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity


# https://api.iamport.kr/

class OrderTransactionManager(models.Manager):
    # Create new transaction
    def create_new(self, order, amount, success=None, transaction_status=None):
        if not order:
            raise ValueError("Your order can not be validated.")

        short_hash = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:2]
        time_hash = hashlib.sha1(str(int(time.time())).encode('utf-8')).hexdigest()[-3:]
        base = str(order.email).split("@")[0]
        key = hashlib.sha1((short_hash + time_hash + base).encode('utf-8')).hexdigest()[:10]
        merchant_order_id = "%s" % key

        # IAMPORT payments pre-validation step (payments.validation)
        validation_prepare(merchant_order_id, amount)

        # Transaction save
        new_trans = self.model(
            order=order,
            merchant_order_id=merchant_order_id,
            amount=amount
        )

        if success is not None:
            new_trans.success = success
            new_trans.transaction_status = transaction_status

        new_trans.save(using=self._db)
        return new_trans.merchant_order_id

    def validation_trans(self, merchant_order_id):
        result = get_transaction(merchant_order_id)
        if result['status'] == 'paid':
            return result
        else:
            return None


class OrderTransaction(models.Model):
    order = models.ForeignKey(Order)
    merchant_order_id = models.CharField(max_length=120, null=True, blank=True)
    transaction_id = models.CharField(max_length=120, null=True, blank=True)
    amount = models.PositiveIntegerField(default=0)
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    type = models.CharField(max_length=120, blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = OrderTransactionManager()  # This is the point!

    def __str__(self):
        return str(self.order.id)

    class Meta:
        ordering = ['-created']


def new_order_trans_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        # Result from IAMPORT after the transaction
        v_trans = OrderTransaction.objects.validation_trans(
            merchant_order_id=instance.merchant_order_id
        )

        res_merchant_id = v_trans['merchant_order_id']
        res_imp_id = v_trans['imp_id']
        res_amount = v_trans['amount']

        # Check the database for actual payment information
        r_trans = OrderTransaction.objects.filter(
            merchant_order_id=res_merchant_id,
            transaction_id=res_imp_id,
            amount=res_amount
        ).exists()

        if not v_trans or not r_trans:
            raise ValueError("It's an abnormal transaction.")


post_save.connect(new_order_trans_validation, sender=OrderTransaction)
