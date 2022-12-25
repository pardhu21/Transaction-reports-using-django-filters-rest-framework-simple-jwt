from django.db import models
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    cost = models.IntegerField()
    category = models.CharField(max_length=50) #make it a select type field by adding few pre defined categories

    def __str__(self) -> str:
        return self.name

class Filter(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_amount_lower_than = models.IntegerField(blank=True, null=True)
    total_amount_greater_than = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=100,blank=True,null=True)
    pin_code =models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=200)
    pin_code = models.IntegerField()

    def __str__(self) -> str:
        return self.name

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    merchant = models.ForeignKey(User,on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='TransactionProduct')
    total_amount = models.IntegerField(blank=True, editable=False, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'ID:{self.id} Transaction between {self.customer} and {self.merchant}'

    #returns a zipped list containing porduct id and its quantity of a tranaction 
    def quantity_list(self):
        products = self.products.all()
        quantites = []
        for product_ in products:
            quantites.append(TransactionProduct.objects.get(transaction = self, product = product_).quantity)
        products_id = [product.id for product in products]
        return list(zip(products_id,quantites))


#Many to Many field relationship table containing an extra field for product quantity
class TransactionProduct(models.Model):
    transaction =models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    #Restricts multiple entries on one product in same transaction
    class Meta:
        unique_together = ('transaction', 'product')

    def __str__(self) -> str:
        return f'Product {self.product} of quantity {self.quantity}'

#Function to update total_amount field by multiplying number of products and their cost
def tranaction_product_update(sender, instance, *args, **kwargs):
    transaction = instance.transaction
    products = instance.transaction.products.all()
    total = 0
    for product in products:
        quantity = TransactionProduct.objects.get(transaction = transaction, product = product).quantity
        total += product.cost * quantity
    transaction.total_amount = total
    transaction.save()

#Signals: Calls the aboe function whenever TransactionProduct table is updated, saved or a row is delete from it 
post_save.connect(tranaction_product_update, sender=TransactionProduct)
post_delete.connect(tranaction_product_update, sender=TransactionProduct)  