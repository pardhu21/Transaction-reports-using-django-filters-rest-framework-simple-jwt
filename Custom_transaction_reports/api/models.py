from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    cost = models.IntegerField()
    category = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()

    def __str__(self) -> str:
        return self.name

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    merchant = models.ForeignKey(User,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='TransactionProduct')
    timestamp = models.TimeField(auto_now=True)

    def quantity_list(self):
        products = self.products.all()
        quantites = []
        for product_ in products:
            quantites.append(TransactionProduct.objects.get(transaction = self, product = product_).quantity)
        products_id = [product.id for product in products]
        return list(zip(products_id,quantites))


    def total_amount(self):
        return sum([Product.objects.get(pk=i[0]).cost * i[1] for i in self.quantity_list()])

class TransactionProduct(models.Model):
    transaction =models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('transaction', 'product')

    def __str__(self) -> str:
        return f'Product {self.product} of quantity {self.quantity}'

    