from django.db import models

_property = property


class Property(models.Model):
    """
        Model that represents a property.
        A property could be a house, a flat, a hotel room, etc.
    """
    name = models.CharField(max_length=255, blank=True)
    base_price = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.id


class PricingRule(models.Model):
    """
        Model that represents a pricing rule that will be applied to a property when booking.
        A rule can have a fixed price, or a percent modifier.
        Only one rule can apply per day.
        We can have multiple rules for the same day, but only the most relevant rule applies.
    """
    property = models.ForeignKey('core.Property', blank=False, null=False, on_delete=models.CASCADE)
    price_modifier = models.FloatField(null=True, blank=True)
    min_stay_length = models.IntegerField(null=True, blank=True)
    fixed_price = models.FloatField(null=True, blank=True)
    specific_day = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'Specific day:{self.specific_day} - Min stay length: {self.min_stay_length} ' \
               f'- Fixed price: {self.fixed_price} - Price modifier: {self.price_modifier}'


class Booking(models.Model):
    """
        Model that represent a booking.
        A booking is done when a customer books a property for a given range of days.
        The booking model is also in charge of calculating the final price the customer will pay.
    """
    property = models.ForeignKey('core.Property', blank=False, null=False, on_delete=models.CASCADE)
    date_start = models.DateField(blank=False, null=False)
    date_end = models.DateField(blank=False, null=False)
    final_price = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @_property
    def stay_length(self):
        return (self.date_end - self.date_start).days + 1
