from django.contrib import admin
from .models import Product, StockHistory

# Inline to view stock history on product detail page
class StockHistoryInline(admin.TabularInline):
    model = StockHistory
    extra = 0
    readonly_fields = ('action', 'quantity_changed', 'timestamp')
    can_delete = False

# Custom Product admin display
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'main_category', 'sub_category',
        'quantity', 'purchased_price', 'selling_price', 'date_purchased', 'supplier_name'
    )
    list_filter = ('main_category', 'sub_category', 'date_purchased')
    search_fields = ('name', 'supplier_name')
    readonly_fields = ('date_purchased', 'product_code')
    inlines = [StockHistoryInline]

# Custom StockHistory admin view (if you want to view it separately too)
@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'action', 'quantity_changed', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('product__name',)
    readonly_fields = ('timestamp',)
