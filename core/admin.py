from django.contrib import admin

from core import models


admin.site.register(models.Property)
admin.site.register(models.Booking)
admin.site.register(models.PricingRule)

