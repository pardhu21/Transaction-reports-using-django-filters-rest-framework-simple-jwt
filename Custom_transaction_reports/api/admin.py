from django.contrib import admin
from .models import Product, Transaction, TransactionProduct, Customer, Filter
# Register your models here.

class TransactionProductInline(admin.TabularInline):
    model = TransactionProduct

class TransactionAdmin(admin.ModelAdmin):
    inlines = [TransactionProductInline]

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionProduct)
admin.site.register([Product, Customer, Filter])
