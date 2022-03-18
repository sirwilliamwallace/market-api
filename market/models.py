from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='کد محصول')
    name = models.CharField(max_length=100, verbose_name='نام محصول')
    price = models.PositiveIntegerField(verbose_name='قیمت')
    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی')

    def increase_inventory(self, amount):
        """
        Increase the inventory of the product by the given amount.
        """
        if amount < 0:
            raise ValueError('amount must be greater than 0')
        self.inventory += amount
        self.save()

    def decrease_inventory(self, amount):
        """
        Decrease the inventory of the product by the given amount.
        """
        if amount < 0:
            raise ValueError('amount must be greater than 0')
        elif amount > self.inventory:
            raise ValueError('not enough inventory')
        self.inventory -= amount
        self.save()

    def jsonified(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'price': self.price,
            'inventory': self.inventory
        }


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    phone = models.CharField(max_length=20, verbose_name='شماره تلفن')
    address = models.TextField(verbose_name='آدرس')
    balance = models.PositiveIntegerField(default=20000,
                                          verbose_name='مانده حساب')  # default is 20000 as a bonus to customers

    def deposit(self, amount):
        """
        Increase the balance of the customer by the given amount.
        """
        if amount < 1:
            raise ValueError('amount must be greater than 0')
        self.balance += amount
        self.save()

    def spend(self, amount):
        """
        Decrease the balance of the customer by the given amount.
        """
        if amount < 1:
            raise ValueError('amount must be greater than 0')
        self.balance -= amount
        self.save()


class OrderRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name='سفارش')
    amount = models.PositiveIntegerField(verbose_name='تعداد')


class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4
    STATUS_CHOICES = (
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED, 'ثبت شده'),
        (STATUS_CANCELED, 'لغو شده'),
        (STATUS_SENT, 'ارسال شده'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='خریدار')
    order_time = models.DateTimeField(auto_now_add=True, verbose_name='زمان سفارش')
    total_price = models.PositiveIntegerField(default=0, verbose_name='مجموع قیمت')
    status = models.IntegerField(choices=STATUS_CHOICES, verbose_name='وضعیت')

    @staticmethod
    def initiate(customer):
        """
        Create a new order for the given customer.
        """
        order = Order(customer=customer, status=Order.STATUS_SHOPPING)
        order.save()
        return order

    def add_product(self, product, amount):
        """
        Add the given product to the order with the given amount.
        """
        if amount < 1:
            raise ValueError('amount must be greater than 0')
        order_row = OrderRow(product=product, order=self, amount=amount)
        order_row.save()
        self.total_price += product.price * amount
        self.save()

    def remove_product(self, product, amount=None):
        """
        Remove the given product from the order with the given amount.
        """
        if amount is None:
            order_row = OrderRow.objects.get(product=product, order=self)
            amount = order_row.amount
        if amount < 1:
            raise ValueError('amount must be greater than 0')
        order_row = OrderRow.objects.get(product=product, order=self)
        order_row.delete()
        self.total_price -= product.price * amount
        self.save()

    def submit(self):
        """
        Submit the order.
        """
        if self.status != Order.STATUS_SHOPPING:
            raise ValueError('order is not in shopping status')
        self.status = Order.STATUS_SUBMITTED
        self.save()

    def cancel(self):
        """
        Cancel the order.
        """
        if self.status != Order.STATUS_SHOPPING:
            raise ValueError('order is not in shopping status')
        self.status = Order.STATUS_CANCELED
        self.save()

    def send(self):
        """
        Send the order.
        """
        if self.status != Order.STATUS_SUBMITTED:
            raise ValueError('order is not in submitted status')
        self.status = Order.STATUS_SENT
        self.save()
