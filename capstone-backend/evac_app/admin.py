from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donor_name', 'item_name', 'quantity', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('donor_name', 'item_name', 'contact_number')